from __future__ import annotations

from app.config import settings
from app.services.queue import get_redis_connection


def _listen_queues() -> list[str]:
    profile = (settings.rq_worker_queue_profile or "all").strip().lower()
    profiles: dict[str, list[str]] = {
        "all": [],
        "render": ["render"],
        "video": ["video", "influencer"],
        "music": ["music"],
        "chat": ["chat"],
        "thumbnail": ["thumbnail"],
        "default": ["default"],
    }

    if profile in profiles and profiles[profile]:
        return profiles[profile]

    raw = (settings.rq_queues or "").strip()
    if not raw:
        return ["default"]
    queues = [item.strip() for item in raw.split(",") if item.strip()]
    return queues or ["default"]


def main() -> None:
    from rq import Worker

    connection = get_redis_connection()
    queues = _listen_queues()
    worker = Worker(queues=queues, connection=connection)
    worker.work(with_scheduler=bool(settings.rq_worker_with_scheduler))


if __name__ == "__main__":
    main()
