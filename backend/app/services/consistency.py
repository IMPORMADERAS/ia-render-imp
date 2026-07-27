from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from ..config import settings
from .postgres_mirror import get_mirror_counts


def _sqlite_conn(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _sqlite_counts() -> dict[str, int]:
    accounts_path = Path(settings.data_dir) / "accounts.db"
    generations_path = Path(settings.data_dir) / "generations.db"

    users = 0
    sessions = 0
    wallet_ledger = 0
    recharge_payments = 0
    password_reset_tokens = 0
    notification_events = 0
    jobs = 0
    anims = 0
    music_jobs = 0

    if accounts_path.exists():
        with _sqlite_conn(accounts_path) as conn:
            users = int((conn.execute("SELECT COUNT(*) AS c FROM users").fetchone() or {"c": 0})["c"])
            sessions = int((conn.execute("SELECT COUNT(*) AS c FROM sessions").fetchone() or {"c": 0})["c"])
            wallet_ledger = int((conn.execute("SELECT COUNT(*) AS c FROM wallet_ledger").fetchone() or {"c": 0})["c"])
            recharge_payments = int((conn.execute("SELECT COUNT(*) AS c FROM recharge_payments").fetchone() or {"c": 0})["c"])
            password_reset_tokens = int((conn.execute("SELECT COUNT(*) AS c FROM password_reset_tokens").fetchone() or {"c": 0})["c"])
            notification_events = int((conn.execute("SELECT COUNT(*) AS c FROM notification_events").fetchone() or {"c": 0})["c"])

    if generations_path.exists():
        with _sqlite_conn(generations_path) as conn:
            jobs = int((conn.execute("SELECT COUNT(*) AS c FROM jobs").fetchone() or {"c": 0})["c"])
            anims = int((conn.execute("SELECT COUNT(*) AS c FROM anims").fetchone() or {"c": 0})["c"])
            music_jobs = int((conn.execute("SELECT COUNT(*) AS c FROM music_jobs").fetchone() or {"c": 0})["c"])

    return {
        "users": users,
        "sessions": sessions,
        "wallet_ledger": wallet_ledger,
        "recharge_payments": recharge_payments,
        "password_reset_tokens": password_reset_tokens,
        "notification_events": notification_events,
        "jobs": jobs,
        "anims": anims,
        "music_jobs": music_jobs,
    }


def _pct(a: int, b: int) -> float:
    if int(a) <= 0:
        return 100.0 if int(b) <= 0 else 0.0
    return round((min(int(a), int(b)) / float(max(1, int(a)))) * 100.0, 2)


def get_consistency_report() -> dict[str, Any]:
    sqlite_counts = _sqlite_counts()
    mirror_counts = get_mirror_counts()

    metrics: dict[str, dict[str, Any]] = {}
    all_green = True
    for key in ("users", "sessions", "wallet_ledger", "recharge_payments", "password_reset_tokens", "notification_events", "jobs", "anims", "music_jobs"):
        sqlite_value = int(sqlite_counts.get(key, 0))
        mirror_value = int(mirror_counts.get(key, 0))
        match = sqlite_value == mirror_value
        if not match:
            all_green = False
        metrics[key] = {
            "sqlite": sqlite_value,
            "postgres": mirror_value,
            "match": match,
            "coverage_pct": _pct(sqlite_value, mirror_value),
            "delta": mirror_value - sqlite_value,
        }

    return {
        "ok": all_green,
        "sqlite": sqlite_counts,
        "postgres": mirror_counts,
        "metrics": metrics,
    }
