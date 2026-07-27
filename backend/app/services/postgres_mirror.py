from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from ..config import settings


def is_postgres_mirror_enabled() -> bool:
    return bool(settings.postgres_mirror_enabled and (settings.postgres_dsn or "").strip())


def _conn():
    import psycopg
    from psycopg.rows import dict_row

    dsn = (settings.postgres_dsn or "").strip()
    if not dsn:
        raise RuntimeError("POSTGRES_DSN no configurado")
    return psycopg.connect(dsn, row_factory=dict_row)


def _safe_iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _public_user_from_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "user_id": int(row.get("id") or 0),
        "username": str(row.get("username") or ""),
        "first_name": str(row.get("first_name") or ""),
        "last_name": str(row.get("last_name") or ""),
        "phone": str(row.get("phone") or ""),
        "email": str(row.get("email") or ""),
        "balance_cop": int(row.get("balance_cop") or 0),
        "created_at": str(row.get("created_at") or ""),
        "updated_at": str(row.get("updated_at") or ""),
    }


def init_postgres_mirror_schema() -> None:
    if not is_postgres_mirror_enabled():
        return

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS mirror_users (
                  id BIGINT PRIMARY KEY,
                  username TEXT NOT NULL,
                  first_name TEXT NOT NULL DEFAULT '',
                  last_name TEXT NOT NULL DEFAULT '',
                  phone TEXT NOT NULL DEFAULT '',
                  email TEXT NOT NULL DEFAULT '',
                  password_hash TEXT NOT NULL DEFAULT '',
                  salt TEXT NOT NULL DEFAULT '',
                  balance_cop BIGINT NOT NULL DEFAULT 0,
                  created_at TEXT NOT NULL DEFAULT '',
                  updated_at TEXT NOT NULL DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS mirror_sessions (
                  token TEXT PRIMARY KEY,
                  user_id BIGINT NOT NULL,
                  expires_at TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS mirror_wallet_ledger (
                  id BIGSERIAL PRIMARY KEY,
                  source_ledger_id BIGINT,
                  user_id BIGINT NOT NULL,
                  tx_type TEXT NOT NULL,
                  amount_cop BIGINT NOT NULL,
                  module TEXT NOT NULL,
                  note TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS mirror_generation_records (
                  record_type TEXT NOT NULL,
                  record_id TEXT NOT NULL,
                  user_id BIGINT NOT NULL DEFAULT 0,
                  updated_at TEXT NOT NULL DEFAULT '',
                  payload_json JSONB NOT NULL,
                  PRIMARY KEY (record_type, record_id)
                );

                                CREATE TABLE IF NOT EXISTS mirror_recharge_payments (
                                    id BIGSERIAL PRIMARY KEY,
                                    reference TEXT UNIQUE NOT NULL,
                                    user_id BIGINT NOT NULL,
                                    amount_cop BIGINT NOT NULL,
                                    amount_in_cents BIGINT NOT NULL,
                                    currency TEXT NOT NULL,
                                    status TEXT NOT NULL,
                                    transaction_id TEXT,
                                    checkout_url TEXT,
                                    gateway_payload TEXT,
                                    created_at TEXT NOT NULL,
                                    updated_at TEXT NOT NULL,
                                    settled_at TEXT
                                );

                                CREATE TABLE IF NOT EXISTS mirror_password_reset_tokens (
                                    id BIGSERIAL PRIMARY KEY,
                                    token TEXT UNIQUE NOT NULL,
                                    user_id BIGINT NOT NULL,
                                    email TEXT NOT NULL,
                                    expires_at TEXT NOT NULL,
                                    created_at TEXT NOT NULL,
                                    sent_at TEXT,
                                    used_at TEXT
                                );

                                CREATE TABLE IF NOT EXISTS mirror_notification_events (
                                    id BIGSERIAL PRIMARY KEY,
                                    event_key TEXT UNIQUE NOT NULL,
                                    created_at TEXT NOT NULL
                                );

                CREATE INDEX IF NOT EXISTS idx_mirror_users_email ON mirror_users(email);
                CREATE INDEX IF NOT EXISTS idx_mirror_sessions_user ON mirror_sessions(user_id);
                CREATE INDEX IF NOT EXISTS idx_mirror_wallet_ledger_user ON mirror_wallet_ledger(user_id, id DESC);
                CREATE UNIQUE INDEX IF NOT EXISTS uidx_mirror_wallet_ledger_source ON mirror_wallet_ledger(source_ledger_id) WHERE source_ledger_id IS NOT NULL;
                CREATE INDEX IF NOT EXISTS idx_mirror_generation_user_updated ON mirror_generation_records(record_type, user_id, updated_at DESC);
                                CREATE INDEX IF NOT EXISTS idx_mirror_recharge_payments_user ON mirror_recharge_payments(user_id, id DESC);
                                CREATE INDEX IF NOT EXISTS idx_mirror_password_reset_user ON mirror_password_reset_tokens(user_id, id DESC);
                """
            )
        conn.commit()


def get_postgres_mirror_health() -> dict[str, Any]:
    response: dict[str, Any] = {
        "enabled": is_postgres_mirror_enabled(),
        "configured": bool((settings.postgres_dsn or "").strip()),
        "ok": False,
        "error": "",
    }
    if not response["configured"]:
        response["error"] = "POSTGRES_DSN no configurado"
        return response

    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        response["ok"] = True
    except Exception as exc:
        response["error"] = str(exc)

    return response


def mirror_upsert_user(payload: dict[str, Any]) -> None:
    if not is_postgres_mirror_enabled():
        return

    data = {
        "id": int(payload.get("id") or payload.get("user_id") or 0),
        "username": str(payload.get("username") or ""),
        "first_name": str(payload.get("first_name") or ""),
        "last_name": str(payload.get("last_name") or ""),
        "phone": str(payload.get("phone") or ""),
        "email": str(payload.get("email") or ""),
        "password_hash": str(payload.get("password_hash") or ""),
        "salt": str(payload.get("salt") or ""),
        "balance_cop": int(payload.get("balance_cop") or 0),
        "created_at": str(payload.get("created_at") or ""),
        "updated_at": str(payload.get("updated_at") or ""),
    }
    if data["id"] <= 0:
        return

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO mirror_users (
                  id, username, first_name, last_name, phone, email,
                  password_hash, salt, balance_cop, created_at, updated_at
                )
                VALUES (%(id)s, %(username)s, %(first_name)s, %(last_name)s, %(phone)s, %(email)s,
                        %(password_hash)s, %(salt)s, %(balance_cop)s, %(created_at)s, %(updated_at)s)
                ON CONFLICT (id) DO UPDATE SET
                  username = EXCLUDED.username,
                  first_name = EXCLUDED.first_name,
                  last_name = EXCLUDED.last_name,
                  phone = EXCLUDED.phone,
                  email = EXCLUDED.email,
                  password_hash = EXCLUDED.password_hash,
                  salt = EXCLUDED.salt,
                  balance_cop = EXCLUDED.balance_cop,
                  created_at = EXCLUDED.created_at,
                  updated_at = EXCLUDED.updated_at
                """,
                data,
            )
        conn.commit()


def mirror_create_session(token: str, user_id: int, expires_at_iso: str, created_at_iso: str) -> None:
    if not is_postgres_mirror_enabled() or not token:
        return

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO mirror_sessions (token, user_id, expires_at, created_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (token) DO UPDATE SET
                  user_id = EXCLUDED.user_id,
                  expires_at = EXCLUDED.expires_at,
                  created_at = EXCLUDED.created_at
                """,
                (token, int(user_id), str(expires_at_iso), str(created_at_iso)),
            )
        conn.commit()


def mirror_delete_session(token: str) -> None:
    if not is_postgres_mirror_enabled() or not token:
        return

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM mirror_sessions WHERE token = %s", (token,))
        conn.commit()


def mirror_delete_sessions_for_user(user_id: int) -> None:
    if not is_postgres_mirror_enabled():
        return

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM mirror_sessions WHERE user_id = %s", (int(user_id),))
        conn.commit()


def mirror_add_wallet_ledger(
    user_id: int,
    tx_type: str,
    amount_cop: int,
    module: str,
    note: str,
    created_at: str,
    source_ledger_id: int | None = None,
) -> None:
    if not is_postgres_mirror_enabled():
        return

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO mirror_wallet_ledger (source_ledger_id, user_id, tx_type, amount_cop, module, note, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_ledger_id) DO NOTHING
                """,
                (
                    int(source_ledger_id) if source_ledger_id is not None else None,
                    int(user_id),
                    str(tx_type),
                    int(amount_cop),
                    str(module),
                    str(note),
                    str(created_at),
                ),
            )
        conn.commit()


def mirror_upsert_generation_record(record_type: str, record_id: str, user_id: int, updated_at: str, payload: dict[str, Any]) -> None:
    if not is_postgres_mirror_enabled():
        return

    payload_json = json.dumps(payload, ensure_ascii=False)
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO mirror_generation_records (record_type, record_id, user_id, updated_at, payload_json)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (record_type, record_id) DO UPDATE SET
                  user_id = EXCLUDED.user_id,
                  updated_at = EXCLUDED.updated_at,
                  payload_json = EXCLUDED.payload_json
                """,
                (str(record_type), str(record_id), int(user_id), str(updated_at), payload_json),
            )
        conn.commit()


def mirror_delete_user_data(user_id: int) -> None:
    if not is_postgres_mirror_enabled():
        return

    uid = int(user_id)
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM mirror_sessions WHERE user_id = %s", (uid,))
            cur.execute("DELETE FROM mirror_wallet_ledger WHERE user_id = %s", (uid,))
            cur.execute("DELETE FROM mirror_password_reset_tokens WHERE user_id = %s", (uid,))
            cur.execute("DELETE FROM mirror_recharge_payments WHERE user_id = %s", (uid,))
            cur.execute("DELETE FROM mirror_users WHERE id = %s", (uid,))
            cur.execute("DELETE FROM mirror_generation_records WHERE user_id = %s", (uid,))
        conn.commit()


def record_notification_event_once(event_key: str, created_at: str) -> bool:
    if not is_postgres_mirror_enabled():
        raise RuntimeError("Postgres mirror no habilitado")

    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO mirror_notification_events (event_key, created_at) VALUES (%s, %s)",
                    (str(event_key), str(created_at)),
                )
            conn.commit()
        return True
    except Exception as exc:
        if "duplicate" in str(exc).lower() or "unique" in str(exc).lower():
            return False
        raise


def create_password_reset_token_record(token: str, user_id: int, email: str, expires_at: str, created_at: str) -> None:
    if not is_postgres_mirror_enabled():
        raise RuntimeError("Postgres mirror no habilitado")

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO mirror_password_reset_tokens (token, user_id, email, expires_at, created_at, sent_at, used_at)
                VALUES (%s, %s, %s, %s, %s, NULL, NULL)
                ON CONFLICT (token) DO UPDATE SET
                  user_id = EXCLUDED.user_id,
                  email = EXCLUDED.email,
                  expires_at = EXCLUDED.expires_at,
                  created_at = EXCLUDED.created_at
                """,
                (str(token), int(user_id), str(email), str(expires_at), str(created_at)),
            )
        conn.commit()


def mark_password_reset_sent_record(token: str, sent_at: str) -> None:
    if not is_postgres_mirror_enabled():
        raise RuntimeError("Postgres mirror no habilitado")

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE mirror_password_reset_tokens SET sent_at = %s WHERE token = %s", (str(sent_at), str(token)))
        conn.commit()


def get_password_reset_token_record(token: str) -> dict[str, Any] | None:
    if not is_postgres_mirror_enabled():
        return None

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT token, user_id, email, expires_at, created_at, sent_at, used_at
                FROM mirror_password_reset_tokens
                WHERE token = %s
                LIMIT 1
                """,
                (str(token),),
            )
            row = cur.fetchone()
    return dict(row) if isinstance(row, dict) else None


def mark_password_reset_used_record(token: str, used_at: str) -> None:
    if not is_postgres_mirror_enabled():
        raise RuntimeError("Postgres mirror no habilitado")

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE mirror_password_reset_tokens SET used_at = %s WHERE token = %s", (str(used_at), str(token)))
        conn.commit()


def create_recharge_payment_intent_record(
    *,
    reference: str,
    user_id: int,
    amount_cop: int,
    amount_in_cents: int,
    currency: str,
    checkout_url: str,
    created_at: str,
    updated_at: str,
    status: str = "PENDING",
    transaction_id: str = "",
    gateway_payload: str = "",
    settled_at: str = "",
) -> None:
    if not is_postgres_mirror_enabled():
        raise RuntimeError("Postgres mirror no habilitado")

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO mirror_recharge_payments (
                  reference, user_id, amount_cop, amount_in_cents, currency, status,
                                    transaction_id, checkout_url, gateway_payload, created_at, updated_at, settled_at
                )
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (reference) DO UPDATE SET
                  user_id = EXCLUDED.user_id,
                  amount_cop = EXCLUDED.amount_cop,
                  amount_in_cents = EXCLUDED.amount_in_cents,
                                    status = EXCLUDED.status,
                                    transaction_id = EXCLUDED.transaction_id,
                  currency = EXCLUDED.currency,
                  checkout_url = EXCLUDED.checkout_url,
                                    gateway_payload = EXCLUDED.gateway_payload,
                  updated_at = EXCLUDED.updated_at
                """,
                                (
                                        str(reference),
                                        int(user_id),
                                        int(amount_cop),
                                        int(amount_in_cents),
                                        str(currency),
                                        str(status or "PENDING"),
                                        transaction_id or None,
                                        str(checkout_url),
                                        str(gateway_payload or ""),
                                        str(created_at),
                                        str(updated_at),
                                        str(settled_at or "") or None,
                                ),
            )
        conn.commit()


def get_recharge_payment_intent_record(reference: str) -> dict[str, Any] | None:
    if not is_postgres_mirror_enabled():
        return None

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, reference, user_id, amount_cop, amount_in_cents, currency, status,
                       transaction_id, checkout_url, gateway_payload, created_at, updated_at, settled_at
                FROM mirror_recharge_payments
                WHERE reference = %s
                LIMIT 1
                """,
                (str(reference),),
            )
            row = cur.fetchone()
    return dict(row) if isinstance(row, dict) else None


def list_pending_recharge_payment_intents_records(user_id: int, limit: int = 30) -> list[dict[str, Any]]:
    if not is_postgres_mirror_enabled():
        return []

    safe_limit = max(1, min(200, int(limit)))
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, reference, user_id, amount_cop, amount_in_cents, currency, status,
                       transaction_id, checkout_url, gateway_payload, created_at, updated_at, settled_at
                FROM mirror_recharge_payments
                WHERE user_id = %s AND settled_at IS NULL
                ORDER BY id DESC
                LIMIT %s
                """,
                (int(user_id), safe_limit),
            )
            rows = cur.fetchall() or []
    return [dict(row) for row in rows if isinstance(row, dict)]


def set_recharge_payment_status_record(reference: str, status: str, transaction_id: str = "", gateway_payload: str = "") -> None:
    if not is_postgres_mirror_enabled():
        raise RuntimeError("Postgres mirror no habilitado")

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE mirror_recharge_payments
                SET status = %s, transaction_id = %s, gateway_payload = %s, updated_at = %s
                WHERE reference = %s
                """,
                (str(status), transaction_id or None, gateway_payload or "", _safe_iso_now(), str(reference)),
            )
        conn.commit()


def settle_recharge_if_approved_record(*, reference: str, transaction_id: str, gateway_payload: str) -> dict[str, Any]:
    if not is_postgres_mirror_enabled():
        raise RuntimeError("Postgres mirror no habilitado")

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, user_id, amount_cop, status, settled_at
                FROM mirror_recharge_payments
                WHERE reference = %s
                FOR UPDATE
                """,
                (str(reference),),
            )
            row = cur.fetchone()
            if not isinstance(row, dict):
                raise ValueError("Referencia de recarga no encontrada")

            if row.get("settled_at"):
                cur.execute("SELECT balance_cop FROM mirror_users WHERE id = %s", (int(row.get("user_id") or 0),))
                user_row = cur.fetchone()
                balance = int((user_row or {}).get("balance_cop") or 0)
                conn.commit()
                return {"already_applied": True, "balance_cop": balance}

            cur.execute("SELECT balance_cop FROM mirror_users WHERE id = %s FOR UPDATE", (int(row.get("user_id") or 0),))
            user_row = cur.fetchone()
            if not isinstance(user_row, dict):
                raise ValueError("Usuario de recarga no encontrado")

            amount = int(row.get("amount_cop") or 0)
            new_balance = int(user_row.get("balance_cop") or 0) + amount
            now = _safe_iso_now()
            cur.execute(
                "UPDATE mirror_users SET balance_cop = %s, updated_at = %s WHERE id = %s",
                (new_balance, now, int(row.get("user_id") or 0)),
            )
            cur.execute(
                """
                INSERT INTO mirror_wallet_ledger (source_ledger_id, user_id, tx_type, amount_cop, module, note, created_at)
                VALUES (NULL, %s, %s, %s, %s, %s, %s)
                """,
                (int(row.get("user_id") or 0), "credit", amount, "wompi_recharge", f"Recarga aprobada Wompi ({reference})", now),
            )
            cur.execute(
                """
                UPDATE mirror_recharge_payments
                SET status = 'APPROVED', transaction_id = %s, gateway_payload = %s, updated_at = %s, settled_at = %s
                WHERE reference = %s
                """,
                (str(transaction_id), gateway_payload or "", now, now, str(reference)),
            )
        conn.commit()

    return {"already_applied": False, "balance_cop": new_balance}


def get_user_auth_by_email(email: str) -> dict[str, Any] | None:
    if not is_postgres_mirror_enabled():
        return None

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, first_name, last_name, phone, email, password_hash, salt,
                       balance_cop, created_at, updated_at
                FROM mirror_users
                WHERE lower(email) = lower(%s)
                LIMIT 1
                """,
                (str(email or ""),),
            )
            row = cur.fetchone()
    return dict(row) if isinstance(row, dict) else None


def get_user_auth_by_id(user_id: int) -> dict[str, Any] | None:
    if not is_postgres_mirror_enabled():
        return None

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, first_name, last_name, phone, email, password_hash, salt,
                       balance_cop, created_at, updated_at
                FROM mirror_users
                WHERE id = %s
                LIMIT 1
                """,
                (int(user_id),),
            )
            row = cur.fetchone()
    return dict(row) if isinstance(row, dict) else None


def create_user(
    *,
    username: str,
    first_name: str,
    last_name: str,
    phone: str,
    email: str,
    password_hash: str,
    salt: str,
    balance_cop: int,
    created_at: str,
    updated_at: str,
) -> dict[str, Any]:
    if not is_postgres_mirror_enabled():
        raise RuntimeError("Postgres mirror no habilitado")

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM mirror_users WHERE lower(email) = lower(%s) LIMIT 1", (str(email),))
            if cur.fetchone() is not None:
                raise ValueError("Ese email ya existe")

            cur.execute("SELECT id FROM mirror_users WHERE username = %s LIMIT 1", (str(username),))
            if cur.fetchone() is not None:
                raise ValueError("Ese usuario ya existe")

            cur.execute(
                """
                INSERT INTO mirror_users (
                  id, username, first_name, last_name, phone, email, password_hash, salt, balance_cop, created_at, updated_at
                )
                VALUES (
                  COALESCE((SELECT MAX(id) + 1 FROM mirror_users), 1),
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id, username, first_name, last_name, phone, email, balance_cop, created_at, updated_at
                """,
                (
                    str(username),
                    str(first_name),
                    str(last_name),
                    str(phone),
                    str(email),
                    str(password_hash),
                    str(salt),
                    int(balance_cop),
                    str(created_at),
                    str(updated_at),
                ),
            )
            row = cur.fetchone()
        conn.commit()

    if not isinstance(row, dict):
        raise RuntimeError("No se pudo crear el usuario en Postgres")
    return _public_user_from_row(row)


def create_wallet_session(token: str, user_id: int, expires_at_iso: str, created_at_iso: str) -> None:
    mirror_create_session(token, user_id, expires_at_iso, created_at_iso)


def delete_wallet_session(token: str) -> None:
    mirror_delete_session(token)


def credit_balance(user_id: int, amount_cop: int, module: str, note: str) -> int:
    if not is_postgres_mirror_enabled():
        raise RuntimeError("Postgres mirror no habilitado")

    now = _safe_iso_now()
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance_cop FROM mirror_users WHERE id = %s FOR UPDATE", (int(user_id),))
            row = cur.fetchone()
            if not isinstance(row, dict):
                raise ValueError("Usuario no encontrado")

            new_balance = int(row.get("balance_cop") or 0) + int(amount_cop)
            cur.execute(
                "UPDATE mirror_users SET balance_cop = %s, updated_at = %s WHERE id = %s",
                (new_balance, now, int(user_id)),
            )
            cur.execute(
                """
                INSERT INTO mirror_wallet_ledger (source_ledger_id, user_id, tx_type, amount_cop, module, note, created_at)
                VALUES (NULL, %s, %s, %s, %s, %s, %s)
                """,
                (int(user_id), "credit", int(amount_cop), str(module), str(note), now),
            )
        conn.commit()
    return new_balance


def debit_balance(user_id: int, amount_cop: int, module: str, note: str) -> dict[str, Any]:
    if not is_postgres_mirror_enabled():
        raise RuntimeError("Postgres mirror no habilitado")

    now = _safe_iso_now()
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT balance_cop, email, first_name, last_name FROM mirror_users WHERE id = %s FOR UPDATE",
                (int(user_id),),
            )
            row = cur.fetchone()
            if not isinstance(row, dict):
                raise ValueError("Usuario no encontrado")

            current = int(row.get("balance_cop") or 0)
            if current < int(amount_cop):
                raise ValueError("Saldo insuficiente")

            new_balance = current - int(amount_cop)
            cur.execute(
                "UPDATE mirror_users SET balance_cop = %s, updated_at = %s WHERE id = %s",
                (new_balance, now, int(user_id)),
            )
            cur.execute(
                """
                INSERT INTO mirror_wallet_ledger (source_ledger_id, user_id, tx_type, amount_cop, module, note, created_at)
                VALUES (NULL, %s, %s, %s, %s, %s, %s)
                """,
                (int(user_id), "debit", int(amount_cop), str(module), str(note), now),
            )
        conn.commit()

    return {
        "new_balance": new_balance,
        "previous_balance": current,
        "email": str(row.get("email") or "").strip(),
        "first_name": str(row.get("first_name") or ""),
        "last_name": str(row.get("last_name") or ""),
    }


def set_user_balance(user_id: int, new_balance_cop: int, module: str, note: str) -> int:
    if not is_postgres_mirror_enabled():
        raise RuntimeError("Postgres mirror no habilitado")

    now = _safe_iso_now()
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance_cop FROM mirror_users WHERE id = %s FOR UPDATE", (int(user_id),))
            row = cur.fetchone()
            if not isinstance(row, dict):
                raise ValueError("Usuario no encontrado")

            current = int(row.get("balance_cop") or 0)
            target = int(new_balance_cop)
            if current == target:
                return current

            cur.execute(
                "UPDATE mirror_users SET balance_cop = %s, updated_at = %s WHERE id = %s",
                (target, now, int(user_id)),
            )

            delta = target - current
            tx_type = "credit" if delta > 0 else "debit"
            cur.execute(
                """
                INSERT INTO mirror_wallet_ledger (source_ledger_id, user_id, tx_type, amount_cop, module, note, created_at)
                VALUES (NULL, %s, %s, %s, %s, %s, %s)
                """,
                (int(user_id), tx_type, abs(delta), str(module), str(note), now),
            )
        conn.commit()
    return target


def update_user_password(user_id: int, password_hash: str, salt: str) -> None:
    if not is_postgres_mirror_enabled():
        raise RuntimeError("Postgres mirror no habilitado")

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE mirror_users SET password_hash = %s, salt = %s, updated_at = %s WHERE id = %s",
                (str(password_hash), str(salt), _safe_iso_now(), int(user_id)),
            )
        conn.commit()


def update_user_profile(
    user_id: int,
    *,
    username: str,
    first_name: str,
    last_name: str,
    phone: str,
    email: str,
) -> dict[str, Any]:
    if not is_postgres_mirror_enabled():
        raise RuntimeError("Postgres mirror no habilitado")

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM mirror_users WHERE id = %s LIMIT 1", (int(user_id),))
            existing = cur.fetchone()
            if not isinstance(existing, dict):
                raise ValueError("Usuario no encontrado")

            cur.execute("SELECT id FROM mirror_users WHERE lower(email) = lower(%s) LIMIT 1", (str(email),))
            owner = cur.fetchone()
            if isinstance(owner, dict) and int(owner.get("id") or 0) != int(user_id):
                raise ValueError("Ese email ya existe")

            cur.execute("SELECT id FROM mirror_users WHERE username = %s LIMIT 1", (str(username),))
            owner = cur.fetchone()
            if isinstance(owner, dict) and int(owner.get("id") or 0) != int(user_id):
                raise ValueError("Ese usuario ya existe")

            cur.execute(
                """
                UPDATE mirror_users
                SET username = %s, first_name = %s, last_name = %s, phone = %s, email = %s, updated_at = %s
                WHERE id = %s
                RETURNING id, username, first_name, last_name, phone, email, balance_cop, created_at, updated_at
                """,
                (str(username), str(first_name), str(last_name), str(phone), str(email), _safe_iso_now(), int(user_id)),
            )
            row = cur.fetchone()
        conn.commit()

    if not isinstance(row, dict):
        raise ValueError("Usuario no encontrado")
    return _public_user_from_row(row)


def delete_user_account(user_id: int) -> dict[str, Any]:
    if not is_postgres_mirror_enabled():
        raise RuntimeError("Postgres mirror no habilitado")

    uid = int(user_id)
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT email, balance_cop FROM mirror_users WHERE id = %s LIMIT 1", (uid,))
            row = cur.fetchone()
            if not isinstance(row, dict):
                raise ValueError("Usuario no encontrado")

            safe_email = str(row.get("email") or "")
            balance_before = int(row.get("balance_cop") or 0)
            cur.execute("SELECT reference FROM mirror_recharge_payments WHERE user_id = %s", (uid,))
            payment_refs = [str(item.get("reference") or "").strip() for item in (cur.fetchall() or []) if isinstance(item, dict)]
            cur.execute("DELETE FROM mirror_sessions WHERE user_id = %s", (uid,))
            cur.execute("DELETE FROM mirror_wallet_ledger WHERE user_id = %s", (uid,))
            cur.execute("DELETE FROM mirror_password_reset_tokens WHERE user_id = %s", (uid,))
            cur.execute("DELETE FROM mirror_recharge_payments WHERE user_id = %s", (uid,))
            cur.execute("DELETE FROM mirror_users WHERE id = %s", (uid,))
            cur.execute("DELETE FROM mirror_notification_events WHERE event_key = %s", (f"registration-success:{uid}",))
            for ref in payment_refs:
                cur.execute("DELETE FROM mirror_notification_events WHERE event_key = %s", (f"payment-success:{ref}",))
                cur.execute("DELETE FROM mirror_notification_events WHERE event_key LIKE %s", (f"payment-failed:{ref}:%",))
        conn.commit()

    return {
        "ok": True,
        "user_id": uid,
        "email": safe_email,
        "balance_before": balance_before,
        "deleted_payment_refs": len(payment_refs),
    }


def get_mirror_counts() -> dict[str, int]:
    if not is_postgres_mirror_enabled():
        return {
            "users": 0,
            "sessions": 0,
            "wallet_ledger": 0,
            "jobs": 0,
            "anims": 0,
            "music_jobs": 0,
            "recharge_payments": 0,
            "password_reset_tokens": 0,
            "notification_events": 0,
        }

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS c FROM mirror_users")
            users = int((cur.fetchone() or {}).get("c") or 0)
            cur.execute("SELECT COUNT(*) AS c FROM mirror_sessions")
            sessions = int((cur.fetchone() or {}).get("c") or 0)
            cur.execute("SELECT COUNT(*) AS c FROM mirror_wallet_ledger")
            wallet_ledger = int((cur.fetchone() or {}).get("c") or 0)
            cur.execute("SELECT COUNT(*) AS c FROM mirror_generation_records WHERE record_type = 'jobs'")
            jobs = int((cur.fetchone() or {}).get("c") or 0)
            cur.execute("SELECT COUNT(*) AS c FROM mirror_generation_records WHERE record_type = 'anims'")
            anims = int((cur.fetchone() or {}).get("c") or 0)
            cur.execute("SELECT COUNT(*) AS c FROM mirror_generation_records WHERE record_type = 'music_jobs'")
            music_jobs = int((cur.fetchone() or {}).get("c") or 0)
            cur.execute("SELECT COUNT(*) AS c FROM mirror_recharge_payments")
            recharge_payments = int((cur.fetchone() or {}).get("c") or 0)
            cur.execute("SELECT COUNT(*) AS c FROM mirror_password_reset_tokens")
            password_reset_tokens = int((cur.fetchone() or {}).get("c") or 0)
            cur.execute("SELECT COUNT(*) AS c FROM mirror_notification_events")
            notification_events = int((cur.fetchone() or {}).get("c") or 0)

    return {
        "users": users,
        "sessions": sessions,
        "wallet_ledger": wallet_ledger,
        "jobs": jobs,
        "anims": anims,
        "music_jobs": music_jobs,
        "recharge_payments": recharge_payments,
        "password_reset_tokens": password_reset_tokens,
        "notification_events": notification_events,
    }


def get_user_by_session_token(token: str | None) -> dict[str, Any] | None:
    if not is_postgres_mirror_enabled() or not token:
        return None

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.token, s.user_id, s.expires_at,
                       u.id, u.username, u.first_name, u.last_name, u.phone, u.email, u.balance_cop,
                       u.created_at, u.updated_at
                FROM mirror_sessions s
                JOIN mirror_users u ON u.id = s.user_id
                WHERE s.token = %s
                LIMIT 1
                """,
                (str(token),),
            )
            row = cur.fetchone()

    if not isinstance(row, dict):
        return None

    expires_raw = str(row.get("expires_at") or "").strip()
    try:
        expires = datetime.fromisoformat(expires_raw)
    except Exception:
        expires = datetime.fromisoformat(_safe_iso_now())

    if expires < datetime.now(timezone.utc):
        try:
            mirror_delete_session(str(token))
        except Exception:
            pass
        return None

    return {
        "user_id": int(row.get("id") or 0),
        "username": str(row.get("username") or ""),
        "first_name": str(row.get("first_name") or ""),
        "last_name": str(row.get("last_name") or ""),
        "phone": str(row.get("phone") or ""),
        "email": str(row.get("email") or ""),
        "balance_cop": int(row.get("balance_cop") or 0),
        "created_at": str(row.get("created_at") or ""),
        "updated_at": str(row.get("updated_at") or ""),
    }


def get_user_profile(user_id: int) -> dict[str, Any] | None:
    if not is_postgres_mirror_enabled():
        return None

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, first_name, last_name, phone, email, balance_cop, created_at, updated_at
                FROM mirror_users
                WHERE id = %s
                LIMIT 1
                """,
                (int(user_id),),
            )
            row = cur.fetchone()
    if not isinstance(row, dict):
        return None
    return _public_user_from_row(row)


def get_user_public_by_email(email: str) -> dict[str, Any] | None:
    row = get_user_auth_by_email(email)
    if row is None:
        return None
    return _public_user_from_row(row)


def get_user_balance(user_id: int) -> int | None:
    if not is_postgres_mirror_enabled():
        return None

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance_cop FROM mirror_users WHERE id = %s LIMIT 1", (int(user_id),))
            row = cur.fetchone()
    if not isinstance(row, dict):
        return None
    return int(row.get("balance_cop") or 0)


def list_all_users(limit: int = 5000) -> list[dict[str, Any]]:
    if not is_postgres_mirror_enabled():
        return []

    safe_limit = max(1, min(50000, int(limit)))
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, first_name, last_name, phone, email, balance_cop, created_at, updated_at
                FROM mirror_users
                ORDER BY id DESC
                LIMIT %s
                """,
                (safe_limit,),
            )
            rows = cur.fetchall() or []
    return [_public_user_from_row(dict(row)) for row in rows if isinstance(row, dict)]


def get_recent_ledger(user_id: int, limit: int = 50) -> list[dict[str, Any]]:
    if not is_postgres_mirror_enabled():
        return []

    safe_limit = max(1, min(200, int(limit)))
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, tx_type, amount_cop, module, note, created_at
                FROM mirror_wallet_ledger
                WHERE user_id = %s
                ORDER BY id DESC
                LIMIT %s
                """,
                (int(user_id), safe_limit),
            )
            rows = cur.fetchall() or []

    items: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        items.append(
            {
                "id": int(row.get("id") or 0),
                "tx_type": str(row.get("tx_type") or ""),
                "amount_cop": int(row.get("amount_cop") or 0),
                "module": str(row.get("module") or ""),
                "note": str(row.get("note") or ""),
                "created_at": str(row.get("created_at") or ""),
            }
        )
    return items


def get_generation_record(record_type: str, record_id: str) -> dict[str, Any] | None:
    if not is_postgres_mirror_enabled():
        return None

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT payload_json
                FROM mirror_generation_records
                WHERE record_type = %s AND record_id = %s
                LIMIT 1
                """,
                (str(record_type), str(record_id)),
            )
            row = cur.fetchone()
    if not isinstance(row, dict):
        return None

    payload = row.get("payload_json")
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            return None
    return None


def list_generation_records(record_type: str, user_id: int, limit: int = 500) -> list[tuple[str, dict[str, Any]]]:
    if not is_postgres_mirror_enabled():
        return []

    safe_limit = max(1, min(5000, int(limit)))
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT record_id, payload_json
                FROM mirror_generation_records
                WHERE record_type = %s AND user_id = %s
                ORDER BY updated_at DESC
                LIMIT %s
                """,
                (str(record_type), int(user_id), safe_limit),
            )
            rows = cur.fetchall() or []

    items: list[tuple[str, dict[str, Any]]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        payload = row.get("payload_json")
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                payload = None
        if isinstance(payload, dict):
            items.append((str(row.get("record_id") or ""), payload))
    return items


def get_next_job_sequence() -> int | None:
    if not is_postgres_mirror_enabled():
        return None

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(MAX((payload_json->>'sequence')::bigint), 0) AS max_seq
                FROM mirror_generation_records
                WHERE record_type = 'jobs'
                """
            )
            row = cur.fetchone()

    if not isinstance(row, dict):
        return None
    max_seq = int(row.get("max_seq") or 0)
    return max_seq + 1 if max_seq > 0 else 1


def get_mirror_counts() -> dict[str, int]:
    if not is_postgres_mirror_enabled():
        return {
            "users": 0,
            "sessions": 0,
            "wallet_ledger": 0,
            "jobs": 0,
            "anims": 0,
            "music_jobs": 0,
        }

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS c FROM mirror_users")
            users = int((cur.fetchone() or {}).get("c") or 0)
            cur.execute("SELECT COUNT(*) AS c FROM mirror_sessions")
            sessions = int((cur.fetchone() or {}).get("c") or 0)
            cur.execute("SELECT COUNT(*) AS c FROM mirror_wallet_ledger")
            wallet_ledger = int((cur.fetchone() or {}).get("c") or 0)
            cur.execute("SELECT COUNT(*) AS c FROM mirror_generation_records WHERE record_type = 'jobs'")
            jobs = int((cur.fetchone() or {}).get("c") or 0)
            cur.execute("SELECT COUNT(*) AS c FROM mirror_generation_records WHERE record_type = 'anims'")
            anims = int((cur.fetchone() or {}).get("c") or 0)
            cur.execute("SELECT COUNT(*) AS c FROM mirror_generation_records WHERE record_type = 'music_jobs'")
            music_jobs = int((cur.fetchone() or {}).get("c") or 0)

    return {
        "users": users,
        "sessions": sessions,
        "wallet_ledger": wallet_ledger,
        "jobs": jobs,
        "anims": anims,
        "music_jobs": music_jobs,
    }
