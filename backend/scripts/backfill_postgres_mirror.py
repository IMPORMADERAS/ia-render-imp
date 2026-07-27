from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.config import settings
from app.services.postgres_mirror import (
    create_password_reset_token_record,
    create_recharge_payment_intent_record,
    init_postgres_mirror_schema,
    is_postgres_mirror_enabled,
    mark_password_reset_sent_record,
    mark_password_reset_used_record,
    mirror_add_wallet_ledger,
    record_notification_event_once,
    mirror_create_session,
    mirror_upsert_generation_record,
    mirror_upsert_user,
    set_recharge_payment_status_record,
)


def _sqlite_conn(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _backfill_accounts() -> None:
    db_path = Path(settings.data_dir) / "accounts.db"
    if not db_path.exists():
        return

    with _sqlite_conn(db_path) as conn:
        users = conn.execute(
            """
            SELECT id, username, first_name, last_name, phone, email, password_hash, salt,
                   balance_cop, created_at, updated_at
            FROM users
            """
        ).fetchall()
        for row in users:
            mirror_upsert_user(
                {
                    "id": int(row["id"]),
                    "username": str(row["username"] or ""),
                    "first_name": str(row["first_name"] or ""),
                    "last_name": str(row["last_name"] or ""),
                    "phone": str(row["phone"] or ""),
                    "email": str(row["email"] or ""),
                    "password_hash": str(row["password_hash"] or ""),
                    "salt": str(row["salt"] or ""),
                    "balance_cop": int(row["balance_cop"] or 0),
                    "created_at": str(row["created_at"] or ""),
                    "updated_at": str(row["updated_at"] or ""),
                }
            )

        sessions = conn.execute("SELECT token, user_id, expires_at, created_at FROM sessions").fetchall()
        for row in sessions:
            mirror_create_session(
                str(row["token"] or ""),
                int(row["user_id"] or 0),
                str(row["expires_at"] or ""),
                str(row["created_at"] or ""),
            )

        ledger = conn.execute(
            """
            SELECT id, user_id, tx_type, amount_cop, module, note, created_at
            FROM wallet_ledger
            """
        ).fetchall()
        for row in ledger:
            mirror_add_wallet_ledger(
                user_id=int(row["user_id"] or 0),
                tx_type=str(row["tx_type"] or ""),
                amount_cop=int(row["amount_cop"] or 0),
                module=str(row["module"] or ""),
                note=str(row["note"] or ""),
                created_at=str(row["created_at"] or ""),
                source_ledger_id=int(row["id"]),
            )

        reset_tokens = conn.execute(
            """
            SELECT token, user_id, email, expires_at, created_at, sent_at, used_at
            FROM password_reset_tokens
            """
        ).fetchall()
        for row in reset_tokens:
            create_password_reset_token_record(
                str(row["token"] or ""),
                int(row["user_id"] or 0),
                str(row["email"] or ""),
                str(row["expires_at"] or ""),
                str(row["created_at"] or ""),
            )
            if str(row["sent_at"] or ""):
                mark_password_reset_sent_record(str(row["token"] or ""), str(row["sent_at"] or ""))
            if str(row["used_at"] or ""):
                mark_password_reset_used_record(str(row["token"] or ""), str(row["used_at"] or ""))

        recharge_payments = conn.execute(
            """
            SELECT reference, user_id, amount_cop, amount_in_cents, currency, status,
                   transaction_id, checkout_url, gateway_payload, created_at, updated_at, settled_at
            FROM recharge_payments
            """
        ).fetchall()
        for row in recharge_payments:
            create_recharge_payment_intent_record(
                reference=str(row["reference"] or ""),
                user_id=int(row["user_id"] or 0),
                amount_cop=int(row["amount_cop"] or 0),
                amount_in_cents=int(row["amount_in_cents"] or 0),
                currency=str(row["currency"] or ""),
                checkout_url=str(row["checkout_url"] or ""),
                created_at=str(row["created_at"] or ""),
                updated_at=str(row["updated_at"] or ""),
                    status=str(row["status"] or "PENDING"),
                    transaction_id=str(row["transaction_id"] or ""),
                    gateway_payload=str(row["gateway_payload"] or ""),
                    settled_at=str(row["settled_at"] or ""),
            )

        notification_events = conn.execute(
            "SELECT event_key, created_at FROM notification_events"
        ).fetchall()
        for row in notification_events:
            record_notification_event_once(str(row["event_key"] or ""), str(row["created_at"] or ""))


def _backfill_generations() -> None:
    db_path = Path(settings.data_dir) / "generations.db"
    if not db_path.exists():
        return

    with _sqlite_conn(db_path) as conn:
        for table in ("jobs", "anims", "music_jobs"):
            rows = conn.execute(f"SELECT id, user_id, updated_at, payload_json FROM {table}").fetchall()
            for row in rows:
                try:
                    payload = json.loads(str(row["payload_json"] or "{}"))
                except Exception:
                    continue
                if not isinstance(payload, dict):
                    continue
                mirror_upsert_generation_record(
                    record_type=table,
                    record_id=str(row["id"] or ""),
                    user_id=int(row["user_id"] or 0),
                    updated_at=str(row["updated_at"] or ""),
                    payload=payload,
                )


def main() -> None:
    if not is_postgres_mirror_enabled():
        raise RuntimeError("Activa POSTGRES_MIRROR_ENABLED=true y define POSTGRES_DSN antes del backfill")

    init_postgres_mirror_schema()
    _backfill_accounts()
    _backfill_generations()
    print("Backfill a Postgres mirror completado")


if __name__ == "__main__":
    main()
