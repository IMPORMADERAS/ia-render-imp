from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock

from fastapi import HTTPException, Request


@dataclass
class _RateBucket:
    attempts: deque[datetime]
    blocked_until: datetime | None = None


_BUCKETS: dict[str, _RateBucket] = {}
_LOCK = Lock()


def client_ip_from_request(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        first = forwarded.split(",", 1)[0].strip()
        if first:
            return first
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def enforce_rate_limit(
    scope: str,
    key: str,
    *,
    max_attempts: int,
    window_seconds: int,
    block_seconds: int,
) -> None:
    now = datetime.now(timezone.utc)
    bucket_key = f"{scope}:{(key or '').strip().lower()}"
    window = timedelta(seconds=max(1, int(window_seconds)))
    block_delta = timedelta(seconds=max(1, int(block_seconds)))

    with _LOCK:
        bucket = _BUCKETS.get(bucket_key)
        if bucket is None:
            bucket = _RateBucket(attempts=deque())
            _BUCKETS[bucket_key] = bucket

        if bucket.blocked_until and bucket.blocked_until > now:
            retry_after = int((bucket.blocked_until - now).total_seconds())
            raise HTTPException(status_code=429, detail=f"Demasiados intentos. Intenta de nuevo en {max(1, retry_after)} segundos")

        while bucket.attempts and now - bucket.attempts[0] > window:
            bucket.attempts.popleft()

        bucket.attempts.append(now)
        if len(bucket.attempts) > max_attempts:
            bucket.blocked_until = now + block_delta
            bucket.attempts.clear()
            raise HTTPException(status_code=429, detail=f"Demasiados intentos. Intenta de nuevo en {block_seconds} segundos")


def reset_rate_limit(scope: str, key: str) -> None:
    bucket_key = f"{scope}:{(key or '').strip().lower()}"
    with _LOCK:
        _BUCKETS.pop(bucket_key, None)