from __future__ import annotations

import hashlib
from typing import Any

from ..config import settings


_MODULE_FLAG_MAP = {
    "auth": ("postgres_primary_auth_enabled", "postgres_primary_auth_percent"),
    "wallet": ("postgres_primary_wallet_enabled", "postgres_primary_wallet_percent"),
    "jobs": ("postgres_primary_jobs_enabled", "postgres_primary_jobs_percent"),
}


def _safe_percent(value: Any) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(100, parsed))


def sqlite_fallback_enabled() -> bool:
    return bool(settings.sqlite_fallback_enabled)


def module_cutover_config(module: str) -> dict[str, Any]:
    key = str(module or "").strip().lower()
    flag_attr, percent_attr = _MODULE_FLAG_MAP.get(key, ("", ""))
    enabled = bool(getattr(settings, flag_attr, False)) if flag_attr else False
    percent = _safe_percent(getattr(settings, percent_attr, 0)) if percent_attr else 0
    return {
        "module": key,
        "enabled": enabled,
        "percent": percent,
        "sqlite_fallback_enabled": sqlite_fallback_enabled(),
    }


def _bucket(identity: str) -> int:
    seed = str(settings.postgres_cutover_seed or "iaimp-cutover")
    payload = f"{seed}:{identity}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    # Stable bucket in [0, 99]
    return int.from_bytes(digest[:2], byteorder="big", signed=False) % 100


def should_read_from_postgres(module: str, identity: str | int | None) -> bool:
    cfg = module_cutover_config(module)
    if not cfg["enabled"]:
        return False

    percent = int(cfg["percent"])
    if percent <= 0:
        return False
    if percent >= 100:
        return True

    identity_value = str(identity or "").strip().lower()
    if not identity_value:
        return False

    return _bucket(identity_value) < percent
