from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock
from time import time

from fastapi import HTTPException, Request

from .queue import get_optional_redis_connection


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
    redis_conn = get_optional_redis_connection()
    if redis_conn is not None:
        try:
            _enforce_rate_limit_redis(
                redis_conn,
                scope=scope,
                key=key,
                max_attempts=max_attempts,
                window_seconds=window_seconds,
                block_seconds=block_seconds,
            )
            return
        except HTTPException:
            raise
        except Exception:
            # Fallback to in-memory limiter when Redis is temporarily unavailable.
            pass

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


def _enforce_rate_limit_redis(
    redis_conn,
    *,
    scope: str,
    key: str,
    max_attempts: int,
    window_seconds: int,
    block_seconds: int,
) -> None:
    now_ts = float(time())
    bucket_key = f"rate:{scope}:{(key or '').strip().lower()}"
    block_key = f"{bucket_key}:blocked"
    window = max(1, int(window_seconds))
    block = max(1, int(block_seconds))

    blocked_ttl = redis_conn.ttl(block_key)
    if blocked_ttl and int(blocked_ttl) > 0:
        retry_after = int(blocked_ttl)
        raise HTTPException(status_code=429, detail=f"Demasiados intentos. Intenta de nuevo en {max(1, retry_after)} segundos")

    min_score = now_ts - window
    pipe = redis_conn.pipeline(transaction=True)
    pipe.zremrangebyscore(bucket_key, 0, min_score)
    pipe.zadd(bucket_key, {f"{now_ts:.6f}:{now_ts}": now_ts})
    pipe.zcard(bucket_key)
    pipe.expire(bucket_key, window + block + 5)
    result = pipe.execute()
    attempts = int(result[2] or 0)

    if attempts > int(max_attempts):
        pipe = redis_conn.pipeline(transaction=True)
        pipe.delete(bucket_key)
        pipe.setex(block_key, block, "1")
        pipe.execute()
        raise HTTPException(status_code=429, detail=f"Demasiados intentos. Intenta de nuevo en {block} segundos")


def reset_rate_limit(scope: str, key: str) -> None:
    bucket_key = f"{scope}:{(key or '').strip().lower()}"
    redis_conn = get_optional_redis_connection()
    if redis_conn is not None:
        try:
            redis_base = f"rate:{scope}:{(key or '').strip().lower()}"
            redis_conn.delete(redis_base)
            redis_conn.delete(f"{redis_base}:blocked")
        except Exception:
            pass
    with _LOCK:
        _BUCKETS.pop(bucket_key, None)