from __future__ import annotations

from typing import Any

from ..config import settings
from .consistency import get_consistency_report
from .metrics import get_metrics_snapshot
from .primary_router import module_cutover_config
from .queue import get_queue_health_metrics


_MODULE_THRESHOLDS = {
    "render": lambda: {
        "latency_ms": int(settings.render_latency_warn_ms),
        "rejections": int(settings.render_rejection_warn_count),
        "errors": int(settings.render_error_warn_count),
        "backlog": int(settings.render_queue_backlog_limit),
    },
    "video": lambda: {
        "latency_ms": int(settings.video_latency_warn_ms),
        "rejections": int(settings.video_rejection_warn_count),
        "errors": int(settings.video_error_warn_count),
        "backlog": int(settings.video_queue_backlog_limit),
    },
    "music": lambda: {
        "latency_ms": int(settings.music_latency_warn_ms),
        "rejections": int(settings.music_rejection_warn_count),
        "errors": int(settings.music_error_warn_count),
        "backlog": int(settings.music_queue_backlog_limit),
    },
    "influencer": lambda: {
        "latency_ms": int(settings.influencer_latency_warn_ms),
        "rejections": int(settings.influencer_rejection_warn_count),
        "errors": int(settings.influencer_error_warn_count),
        "backlog": int(settings.influencer_queue_backlog_limit),
    },
}

_QUEUE_NAME_TO_MODULE = {
    "render": "render",
    "video": "video",
    "music": "music",
    "influencer": "influencer",
}


def _queue_backlog_map(queue_health: dict[str, Any]) -> dict[str, int]:
    backlog: dict[str, int] = {}
    for queue in queue_health.get("queues", []) or []:
        name = str(queue.get("name") or "").strip().lower()
        module = _QUEUE_NAME_TO_MODULE.get(name)
        if not module:
            continue
        backlog[module] = int(queue.get("queued") or 0) + int(queue.get("scheduled") or 0) + int(queue.get("deferred") or 0)
    return backlog


def _find_metric(metrics: dict[str, Any], module: str) -> dict[str, Any]:
    for item in metrics.get("modules", []) or []:
        if str(item.get("module") or "").strip().lower() == module:
            return item
    return {}


def _consistency_state(consistency: dict[str, Any], module: str) -> tuple[bool, float]:
    if module == "render":
        keys = ["jobs"]
    elif module in {"video", "influencer"}:
        keys = ["anims"]
    elif module == "music":
        keys = ["music_jobs"]
    else:
        return True, 100.0

    metrics = consistency.get("metrics", {}) or {}
    coverages: list[float] = []
    ok = True
    for key in keys:
        item = metrics.get(key, {}) or {}
        coverage = float(item.get("coverage_pct") or 0)
        coverages.append(coverage)
        ok = ok and bool(item.get("match"))
    avg_coverage = sum(coverages) / len(coverages) if coverages else 100.0
    return ok, avg_coverage


def _recommendation(module: str, backlog: int, metrics: dict[str, Any], consistency: dict[str, Any]) -> dict[str, Any]:
    thresholds = _MODULE_THRESHOLDS[module]()
    cutover = module_cutover_config("jobs" if module in {"render", "video", "music", "influencer"} else module)
    consistency_ok, coverage = _consistency_state(consistency, module)

    latency = float(metrics.get("api_avg_duration_ms") or 0)
    errors = int(metrics.get("api_errors_5xx") or 0) + int(metrics.get("jobs_failed") or 0)
    rejections = int(metrics.get("jobs_rejected") or 0)
    backlog_ratio = (backlog / max(1, int(thresholds["backlog"]))) if int(thresholds["backlog"]) > 0 else 0.0
    status = "ok"
    action = "Mantener configuración actual"
    reasons: list[str] = []

    if backlog_ratio >= 1.0 or rejections >= int(thresholds["rejections"]) or errors >= int(thresholds["errors"]):
        status = "critical"
        action = "No subir tráfico. Aumentar workers o bajar concurrencia por módulo"
    elif backlog_ratio >= 0.7 or latency >= float(thresholds["latency_ms"]):
        status = "warn"
        action = "Mantener o subir muy gradual. Vigilar cola y latencia"

    if backlog_ratio >= 1.0:
        reasons.append(f"Backlog al {round(backlog_ratio * 100, 1)}% del límite")
    elif backlog_ratio >= 0.7:
        reasons.append(f"Backlog alto: {round(backlog_ratio * 100, 1)}% del límite")

    if latency >= float(thresholds["latency_ms"]):
        reasons.append(f"Latencia API alta: {round(latency, 2)} ms")
    if rejections >= int(thresholds["rejections"]):
        reasons.append(f"Rechazos por capacidad: {rejections}")
    if errors >= int(thresholds["errors"]):
        reasons.append(f"Errores acumulados: {errors}")

    if cutover.get("enabled") and coverage < float(settings.consistency_min_coverage_pct):
        status = "warn" if status == "ok" else status
        reasons.append(f"Consistencia por debajo del umbral: {round(coverage, 2)}%")

    if cutover.get("enabled") and cutover.get("percent", 0) < 100 and status == "ok" and consistency_ok and coverage >= float(settings.consistency_min_coverage_pct):
        action = f"Apto para subir cutover gradual desde {cutover.get('percent', 0)}%"
        reasons.append("Cola y consistencia en rango")

    if not reasons:
        reasons.append("Métricas dentro de rango")

    return {
        "module": module,
        "status": status,
        "action": action,
        "backlog": int(backlog),
        "latency_ms": round(latency, 2),
        "errors": int(errors),
        "rejections": int(rejections),
        "cutover_percent": int(cutover.get("percent") or 0),
        "consistency_coverage_pct": round(coverage, 2),
        "reasons": reasons,
    }


def get_capacity_advice() -> dict[str, Any]:
    queue_health = get_queue_health_metrics()
    metrics = get_metrics_snapshot()
    consistency = get_consistency_report()
    backlog_by_module = _queue_backlog_map(queue_health)

    modules: list[dict[str, Any]] = []
    for module in ("render", "video", "music", "influencer"):
        modules.append(
            _recommendation(
                module,
                backlog_by_module.get(module, 0),
                _find_metric(metrics, module),
                consistency,
            )
        )

    overall_status = "ok"
    if any(item["status"] == "critical" for item in modules):
        overall_status = "critical"
    elif any(item["status"] == "warn" for item in modules):
        overall_status = "warn"

    if overall_status == "critical":
        summary = "No subir tráfico. Hay al menos un módulo fuera de rango operativo."
    elif overall_status == "warn":
        summary = "Subida gradual solamente. Hay señales de saturación o consistencia parcial."
    else:
        summary = "Rango estable para seguir probando escalado gradual."

    return {
        "status": overall_status,
        "summary": summary,
        "modules": modules,
    }
