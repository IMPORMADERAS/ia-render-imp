from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from threading import Lock
from typing import Any

from fastapi import Request

from .queue import get_optional_redis_connection


_MEMORY_LOCK = Lock()
_MEMORY_STARTED_AT = datetime.now(timezone.utc).isoformat()
_MEMORY_BUCKETS: dict[str, dict[str, float]] = {}


def _utc_day_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def _metrics_hash_key(scope: str) -> str:
    return f"metrics:{_utc_day_key()}:{scope}"


def _metrics_meta_key() -> str:
    return f"metrics:{_utc_day_key()}:meta"


def _module_from_path(path: str) -> str:
    value = str(path or "").strip().lower()
    if value.startswith("/jobs"):
        return "render"
    if value.startswith("/animate"):
        return "video"
    if value.startswith("/music"):
        return "music"
    if value.startswith("/influencer"):
        return "influencer"
    if value.startswith("/payments"):
        return "payments"
    if value.startswith("/auth"):
        return "auth"
    if value.startswith("/chat"):
        return "chat"
    if value.startswith("/admin-api"):
        return "admin"
    return "other"


def _increment_metrics(scope: str, fields: dict[str, int | float]) -> None:
    redis_conn = get_optional_redis_connection()
    if redis_conn is None:
        with _MEMORY_LOCK:
            bucket = _MEMORY_BUCKETS.setdefault(scope, {})
            for name, value in fields.items():
                bucket[name] = float(bucket.get(name, 0.0)) + float(value)
        return

    key = _metrics_hash_key(scope)
    meta_key = _metrics_meta_key()
    pipe = redis_conn.pipeline(transaction=False)
    for name, value in fields.items():
        pipe.hincrbyfloat(key, name, float(value))
    pipe.expire(key, 3 * 24 * 60 * 60)
    pipe.hsetnx(meta_key, "started_at", datetime.now(timezone.utc).isoformat())
    pipe.expire(meta_key, 3 * 24 * 60 * 60)
    pipe.execute()


def record_api_request(module: str, status_code: int, duration_ms: float) -> None:
    safe_module = str(module or "other").strip().lower()
    fields: dict[str, int | float] = {
        "requests_total": 1,
        "duration_ms_total": max(0.0, float(duration_ms)),
    }
    if int(status_code) >= 500:
        fields["errors_5xx"] = 1
    elif int(status_code) >= 400:
        fields["errors_4xx"] = 1
    _increment_metrics(f"api:{safe_module}", fields)


def record_job_outcome(module: str, status: str, duration_seconds: int | float = 0) -> None:
    safe_module = str(module or "other").strip().lower()
    safe_status = str(status or "unknown").strip().lower()
    fields: dict[str, int | float] = {
        "jobs_total": 1,
        "job_duration_seconds_total": max(0.0, float(duration_seconds or 0)),
    }
    if safe_status == "completed":
        fields["jobs_completed"] = 1
    elif safe_status == "failed":
        fields["jobs_failed"] = 1
    elif safe_status == "rejected":
        fields["jobs_rejected"] = 1
    _increment_metrics(f"worker:{safe_module}", fields)


def record_capacity_rejection(module: str) -> None:
    record_job_outcome(module, "rejected", 0)


def get_metrics_snapshot() -> dict[str, Any]:
    redis_conn = get_optional_redis_connection()
    modules = ["render", "video", "music", "influencer", "payments", "auth", "chat", "admin", "other"]
    if redis_conn is None:
        results: list[dict[str, Any]] = []

        with _MEMORY_LOCK:
            memory_copy = {scope: values.copy() for scope, values in _MEMORY_BUCKETS.items()}
            started_at = _MEMORY_STARTED_AT

        for module in modules:
            api_raw = memory_copy.get(f"api:{module}", {})
            worker_raw = memory_copy.get(f"worker:{module}", {})

            def _num(mapping: dict[str, float], name: str) -> float:
                try:
                    return float(mapping.get(name, 0.0) or 0.0)
                except Exception:
                    return 0.0

            requests_total = _num(api_raw, "requests_total")
            duration_total = _num(api_raw, "duration_ms_total")
            jobs_total = _num(worker_raw, "jobs_total")
            jobs_duration_total = _num(worker_raw, "job_duration_seconds_total")

            if requests_total <= 0 and jobs_total <= 0:
                continue

            results.append(
                {
                    "module": module,
                    "api_requests_total": int(requests_total),
                    "api_errors_4xx": int(_num(api_raw, "errors_4xx")),
                    "api_errors_5xx": int(_num(api_raw, "errors_5xx")),
                    "api_avg_duration_ms": round(duration_total / requests_total, 2) if requests_total > 0 else 0.0,
                    "jobs_total": int(jobs_total),
                    "jobs_completed": int(_num(worker_raw, "jobs_completed")),
                    "jobs_failed": int(_num(worker_raw, "jobs_failed")),
                    "jobs_rejected": int(_num(worker_raw, "jobs_rejected")),
                    "job_avg_duration_seconds": round(jobs_duration_total / jobs_total, 2) if jobs_total > 0 else 0.0,
                }
            )

        return {"enabled": True, "source": "memory", "modules": results, "started_at": started_at}

    started_at = str(redis_conn.hget(_metrics_meta_key(), "started_at") or b"").replace("b'", "").replace("'", "")
    results: list[dict[str, Any]] = []

    for module in modules:
        api_raw = redis_conn.hgetall(_metrics_hash_key(f"api:{module}")) or {}
        worker_raw = redis_conn.hgetall(_metrics_hash_key(f"worker:{module}")) or {}

        def _num(mapping: dict, name: str) -> float:
            value = mapping.get(name.encode()) if isinstance(next(iter(mapping.keys()), b""), bytes) else mapping.get(name)
            try:
                return float(value or 0)
            except Exception:
                return 0.0

        requests_total = _num(api_raw, "requests_total")
        duration_total = _num(api_raw, "duration_ms_total")
        jobs_total = _num(worker_raw, "jobs_total")
        jobs_duration_total = _num(worker_raw, "job_duration_seconds_total")

        if requests_total <= 0 and jobs_total <= 0:
            continue

        results.append(
            {
                "module": module,
                "api_requests_total": int(requests_total),
                "api_errors_4xx": int(_num(api_raw, "errors_4xx")),
                "api_errors_5xx": int(_num(api_raw, "errors_5xx")),
                "api_avg_duration_ms": round(duration_total / requests_total, 2) if requests_total > 0 else 0.0,
                "jobs_total": int(jobs_total),
                "jobs_completed": int(_num(worker_raw, "jobs_completed")),
                "jobs_failed": int(_num(worker_raw, "jobs_failed")),
                "jobs_rejected": int(_num(worker_raw, "jobs_rejected")),
                "job_avg_duration_seconds": round(jobs_duration_total / jobs_total, 2) if jobs_total > 0 else 0.0,
            }
        )

    return {"enabled": True, "started_at": started_at, "modules": results}


class MetricsTimer:
    def __init__(self) -> None:
        self.started = perf_counter()

    def elapsed_ms(self) -> float:
        return max(0.0, (perf_counter() - self.started) * 1000.0)


def module_from_request(request: Request) -> str:
    return _module_from_path(str(request.url.path or ""))