from __future__ import annotations

from app.config import settings
from app.services.queue import get_redis_connection


def _listen_queues() -> list[str]:
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
    worker.work(with_scheduler=True)


if __name__ == "__main__":
    main()
