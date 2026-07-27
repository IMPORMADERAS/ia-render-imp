from __future__ import annotations

from typing import Any, Callable

from fastapi import BackgroundTasks

from ..config import settings


class QueueUnavailableError(RuntimeError):
    pass


def is_queue_enabled() -> bool:
    return bool(settings.jobs_queue_enabled and (settings.redis_url or "").strip())


def _queue_name(name: str | None) -> str:
    candidate = (name or "").strip()
    if candidate:
        return candidate
    return (settings.rq_default_queue or "default").strip() or "default"


def get_redis_connection():
    import redis

    redis_url = (settings.redis_url or "").strip()
    if not redis_url:
        raise RuntimeError("Falta REDIS_URL para cola distribuida")
    return redis.from_url(redis_url)


def get_optional_redis_connection():
    redis_url = (settings.redis_url or "").strip()
    if not redis_url:
        return None
    try:
        return get_redis_connection()
    except Exception:
        return None


def enqueue_or_background(
    background_tasks: BackgroundTasks,
    func: Callable[..., Any],
    *args: Any,
    queue_name: str | None = None,
    **kwargs: Any,
) -> str | None:
    strict_mode = bool(settings.queue_require_redis)

    if is_queue_enabled():
        try:
            from rq import Queue

            queue = Queue(
                name=_queue_name(queue_name),
                connection=get_redis_connection(),
                default_timeout=max(60, int(settings.rq_job_timeout_seconds)),
            )
            job = queue.enqueue(
                func,
                *args,
                **kwargs,
                job_timeout=max(60, int(settings.rq_job_timeout_seconds)),
            )
            return str(job.id)
        except Exception as exc:
            if strict_mode:
                raise QueueUnavailableError("Cola distribuida no disponible") from exc
            # Keep compatibility by running in-process when queue is unavailable.
            pass

    if strict_mode:
        raise QueueUnavailableError("Cola distribuida deshabilitada o sin REDIS_URL")

    background_tasks.add_task(func, *args, **kwargs)
    return None


def get_queue_health_metrics() -> dict[str, Any]:
    response: dict[str, Any] = {
        "queue_enabled": is_queue_enabled(),
        "strict_mode": bool(settings.queue_require_redis),
        "redis_configured": bool((settings.redis_url or "").strip()),
        "redis_ok": False,
        "error": "",
        "queues": [],
    }

    redis_conn = get_optional_redis_connection()
    if redis_conn is None:
        response["error"] = "Redis no configurado"
        return response

    try:
        redis_conn.ping()
        response["redis_ok"] = True
    except Exception as exc:
        response["error"] = str(exc)
        return response

    try:
        from rq import Queue

        names = [q.strip() for q in (settings.rq_queues or "default").split(",") if q.strip()]
        if not names:
            names = ["default"]

        queues: list[dict[str, Any]] = []
        for name in names:
            queue = Queue(name=name, connection=redis_conn)
            queues.append(
                {
                    "name": name,
                    "queued": int(queue.count),
                    "started": int(len(queue.started_job_registry)),
                    "failed": int(len(queue.failed_job_registry)),
                    "deferred": int(len(queue.deferred_job_registry)),
                    "scheduled": int(len(queue.scheduled_job_registry)),
                    "finished": int(len(queue.finished_job_registry)),
                }
            )

        response["queues"] = queues
        response["total_backlog"] = int(sum(q["queued"] + q["deferred"] + q["scheduled"] for q in queues))
    except Exception as exc:
        response["error"] = str(exc)

    return response
