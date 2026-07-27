from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from ..config import settings
from .metrics import record_capacity_rejection
from .queue import get_optional_redis_connection, is_queue_enabled


_MODULES: dict[str, dict[str, Any]] = {
    "render": {
        "queue": "render",
        "backlog_limit": lambda: int(settings.render_queue_backlog_limit),
        "user_limit": lambda: int(settings.render_user_active_limit),
        "display": "render de imagen",
    },
    "video": {
        "queue": "video",
        "backlog_limit": lambda: int(settings.video_queue_backlog_limit),
        "user_limit": lambda: int(settings.video_user_active_limit),
        "display": "video IA",
    },
    "music": {
        "queue": "music",
        "backlog_limit": lambda: int(settings.music_queue_backlog_limit),
        "user_limit": lambda: int(settings.music_user_active_limit),
        "display": "musica IA",
    },
    "influencer": {
        "queue": "influencer",
        "backlog_limit": lambda: int(settings.influencer_queue_backlog_limit),
        "user_limit": lambda: int(settings.influencer_user_active_limit),
        "display": "influencer IA",
    },
}


def _cfg(module: str) -> dict[str, Any]:
    key = str(module or "").strip().lower()
    if key not in _MODULES:
        raise ValueError(f"Modulo de admision no soportado: {module}")
    return _MODULES[key]


def _safe_limit(value: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, parsed)


def _user_active_key(module: str, user_id: int) -> str:
    return f"capacity:user:{module}:{int(user_id)}"


def _slot_ttl_seconds() -> int:
    return max(300, int(settings.rq_job_timeout_seconds) + 600)


def _queue_pressure(module: str) -> int:
    redis_conn = get_optional_redis_connection()
    if redis_conn is None or not is_queue_enabled():
        return 0

    from rq import Queue

    queue = Queue(name=_cfg(module)["queue"], connection=redis_conn)
    return int(queue.count) + int(len(queue.started_job_registry)) + int(len(queue.deferred_job_registry)) + int(len(queue.scheduled_job_registry))


def _user_active_count(module: str, user_id: int) -> int:
    redis_conn = get_optional_redis_connection()
    if redis_conn is not None:
        try:
            return int(redis_conn.get(_user_active_key(module, user_id)) or 0)
        except Exception:
            pass

    return 0


def enforce_generation_capacity(module: str, user_id: int) -> None:
    cfg = _cfg(module)
    backlog_limit = _safe_limit(cfg["backlog_limit"]())
    user_limit = _safe_limit(cfg["user_limit"]())
    display = str(cfg["display"])

    if backlog_limit > 0:
        try:
            pressure = _queue_pressure(module)
            if pressure >= backlog_limit:
                record_capacity_rejection(module)
                raise HTTPException(
                    status_code=503,
                    detail=(
                        f"Alta demanda en {display}. La cola alcanzo su limite operativo temporal. "
                        "Intenta nuevamente en unos minutos."
                    ),
                )
        except HTTPException:
            raise
        except Exception:
            pass

    if user_limit > 0:
        active_count = _user_active_count(module, user_id)
        if active_count >= user_limit:
            record_capacity_rejection(module)
            raise HTTPException(
                status_code=429,
                detail=f"Ya tienes el maximo de solicitudes activas para {display}. Espera a que termine una antes de crear otra.",
            )


def reserve_generation_slot(module: str, user_id: int) -> None:
    redis_conn = get_optional_redis_connection()
    if redis_conn is None:
        return

    key = _user_active_key(module, user_id)
    ttl = _slot_ttl_seconds()
    try:
        current = int(redis_conn.get(key) or 0)
        redis_conn.setex(key, ttl, str(current + 1))
    except Exception:
        pass


def release_generation_slot(module: str, user_id: int) -> None:
    redis_conn = get_optional_redis_connection()
    if redis_conn is None:
        return

    key = _user_active_key(module, user_id)
    ttl = _slot_ttl_seconds()
    try:
        current = int(redis_conn.get(key) or 0)
        next_value = max(0, current - 1)
        if next_value <= 0:
            redis_conn.delete(key)
        else:
            redis_conn.setex(key, ttl, str(next_value))
    except Exception:
        pass
