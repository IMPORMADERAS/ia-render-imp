import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import smtplib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path

from fastapi import Cookie, HTTPException

from ..config import settings

DB_PATH = Path(settings.data_dir) / "accounts.db"
SESSION_COOKIE_NAME = "iaimp_session"
USERNAME_RE = re.compile(r"^[a-zA-Z0-9._-]{3,32}$")
PHONE_RE = re.compile(r"^\+?[0-9]{7,15}$")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class InsufficientBalanceError(Exception):
    pass


@dataclass
class AuthenticatedUser:
    user_id: int
    username: str
    balance_cop: int


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_auth_wallet_db() -> None:
    with _get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT UNIQUE NOT NULL,
                            first_name TEXT NOT NULL DEFAULT '',
                            last_name TEXT NOT NULL DEFAULT '',
                            phone TEXT NOT NULL DEFAULT '',
                            email TEXT NOT NULL DEFAULT '',
              password_hash TEXT NOT NULL,
              salt TEXT NOT NULL,
              balance_cop INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sessions (
              token TEXT PRIMARY KEY,
              user_id INTEGER NOT NULL,
              expires_at TEXT NOT NULL,
              created_at TEXT NOT NULL,
              FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS wallet_ledger (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL,
              tx_type TEXT NOT NULL,
              amount_cop INTEGER NOT NULL,
              module TEXT NOT NULL,
              note TEXT NOT NULL,
              created_at TEXT NOT NULL,
              FOREIGN KEY(user_id) REFERENCES users(id)
            );

                        CREATE TABLE IF NOT EXISTS recharge_payments (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            reference TEXT UNIQUE NOT NULL,
                            user_id INTEGER NOT NULL,
                            amount_cop INTEGER NOT NULL,
                            amount_in_cents INTEGER NOT NULL,
                            currency TEXT NOT NULL,
                            status TEXT NOT NULL,
                            transaction_id TEXT,
                            checkout_url TEXT,
                            gateway_payload TEXT,
                            created_at TEXT NOT NULL,
                            updated_at TEXT NOT NULL,
                            settled_at TEXT,
                            FOREIGN KEY(user_id) REFERENCES users(id)
                        );

                        CREATE TABLE IF NOT EXISTS password_reset_tokens (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            token TEXT UNIQUE NOT NULL,
                            user_id INTEGER NOT NULL,
                            email TEXT NOT NULL,
                            expires_at TEXT NOT NULL,
                            created_at TEXT NOT NULL,
                            sent_at TEXT,
                            used_at TEXT,
                            FOREIGN KEY(user_id) REFERENCES users(id)
                        );

                        CREATE TABLE IF NOT EXISTS notification_events (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            event_key TEXT UNIQUE NOT NULL,
                            created_at TEXT NOT NULL
                        );
            """
        )

        columns = {
            str(r["name"])
            for r in conn.execute("PRAGMA table_info(users)").fetchall()
        }
        if "first_name" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN first_name TEXT NOT NULL DEFAULT ''")
        if "last_name" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN last_name TEXT NOT NULL DEFAULT ''")
        if "phone" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN phone TEXT NOT NULL DEFAULT ''")
        if "email" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN email TEXT NOT NULL DEFAULT ''")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")


def _normalize_username(username: str) -> str:
    value = (username or "").strip().lower()
    if not USERNAME_RE.fullmatch(value):
        raise ValueError("Usuario invalido. Usa 3-32 caracteres: letras, numeros, ., _, -")
    return value


def _hash_password(password: str, salt: str) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 240_000)
    return dk.hex()


def _normalize_phone(phone: str) -> str:
    value = (phone or "").strip().replace(" ", "")
    if not PHONE_RE.fullmatch(value):
        raise ValueError("Celular invalido. Usa solo numeros (opcional +) entre 7 y 15 digitos")
    return value


def _normalize_optional_phone(phone: str) -> str:
    value = (phone or "").strip()
    if not value:
        return ""
    return _normalize_phone(value)


def _normalize_email(email: str) -> str:
    value = (email or "").strip().lower()
    if not EMAIL_RE.fullmatch(value):
        raise ValueError("Email invalido")
    return value


def _public_user(row: sqlite3.Row) -> dict:
    return {
        "user_id": int(row["id"]),
        "username": str(row["username"]),
        "first_name": str(row["first_name"] or ""),
        "last_name": str(row["last_name"] or ""),
        "phone": str(row["phone"] or ""),
        "email": str(row["email"] or ""),
        "balance_cop": int(row["balance_cop"]),
        "created_at": str(row["created_at"] or ""),
    }


def register_user(first_name: str, last_name: str, email: str, password: str, phone: str = "") -> dict:
    safe_first_name = (first_name or "").strip()
    safe_last_name = (last_name or "").strip()
    if len(safe_first_name) < 2:
        raise ValueError("Nombres invalidos")
    if len(safe_last_name) < 2:
        raise ValueError("Apellidos invalidos")

    safe_email = _normalize_email(email)
    uname = _normalize_username(f"user_{secrets.token_hex(4)}")
    if len((password or "").strip()) < 6:
        raise ValueError("La contraseña debe tener al menos 6 caracteres")

    salt = secrets.token_hex(16)
    pwd_hash = _hash_password(password, salt)
    now = _utc_now_iso()

    try:
        with _get_conn() as conn:
            exists = conn.execute("SELECT 1 FROM users WHERE email = ?", (safe_email,)).fetchone()
            if exists is not None:
                raise ValueError("Ese email ya existe")

            conn.execute(
                """
                INSERT INTO users (username, first_name, last_name, phone, email, password_hash, salt, balance_cop, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
                """,
                (uname, safe_first_name, safe_last_name, (phone or "").strip(), safe_email, pwd_hash, salt, now, now),
            )
            row = conn.execute("SELECT * FROM users WHERE email = ?", (safe_email,)).fetchone()
            if row is None:
                raise RuntimeError("No se pudo crear el usuario")
            return _public_user(row)
    except sqlite3.IntegrityError as exc:
        raise ValueError("Ese email ya existe") from exc


def _format_cop(amount_cop: int) -> str:
    return f"{int(amount_cop):,}".replace(",", ".")


def _record_notification_event_once(event_key: str) -> bool:
    safe_key = (event_key or "").strip()
    if not safe_key:
        return False

    try:
        with _get_conn() as conn:
            conn.execute(
                "INSERT INTO notification_events (event_key, created_at) VALUES (?, ?)",
                (safe_key, _utc_now_iso()),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def _get_user_contact(user_id: int) -> dict | None:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT id, first_name, last_name, email, balance_cop FROM users WHERE id = ?",
            (int(user_id),),
        ).fetchone()

    if row is None:
        return None

    return {
        "user_id": int(row["id"]),
        "first_name": str(row["first_name"] or ""),
        "last_name": str(row["last_name"] or ""),
        "email": str(row["email"] or ""),
        "balance_cop": int(row["balance_cop"] or 0),
    }


def _full_name(first_name: str, last_name: str) -> str:
    return (f"{(first_name or '').strip()} {(last_name or '').strip()}").strip() or "usuario"


def send_registration_success_notification(user: dict) -> dict:
    user_id = int(user.get("user_id") or 0)
    if user_id <= 0:
        return {"delivered": False, "mode": "skipped", "reason": "user_id_invalido"}

    if not _record_notification_event_once(f"registration-success:{user_id}"):
        return {"delivered": False, "mode": "skipped", "reason": "already_sent"}

    email = str(user.get("email") or "").strip()
    if not email:
        return {"delivered": False, "mode": "skipped", "reason": "email_vacio"}

    name = _full_name(str(user.get("first_name") or ""), str(user.get("last_name") or ""))
    body = (
        f"Hola {name},\n\n"
        "Tu registro en IA-IMP fue exitoso.\n"
        "Ya puedes iniciar sesion, recargar saldo y usar los modulos de generacion.\n\n"
        "Gracias por confiar en IA-IMP."
    )
    return send_email_notification(email, "Registro exitoso en IA-IMP", body)


def send_password_reset_success_notification(email: str) -> dict:
    safe_email = _normalize_email(email)
    body = (
        "Tu contraseña en IA-IMP fue actualizada correctamente.\n\n"
        "Si no realizaste este cambio, te recomendamos cambiar tu contraseña de inmediato "
        "y contactar al soporte."
    )
    return send_email_notification(safe_email, "Contraseña actualizada en IA-IMP", body)


def send_payment_success_notification(
    *,
    user_id: int,
    reference: str,
    amount_cop: int,
    balance_cop: int,
    transaction_id: str,
) -> dict:
    contact = _get_user_contact(user_id)
    if contact is None or not str(contact.get("email") or "").strip():
        return {"delivered": False, "mode": "skipped", "reason": "contacto_no_disponible"}

    safe_reference = (reference or "").strip() or "SIN-REFERENCIA"
    event_key = f"payment-success:{safe_reference}"
    if not _record_notification_event_once(event_key):
        return {"delivered": False, "mode": "skipped", "reason": "already_sent"}

    name = _full_name(str(contact.get("first_name") or ""), str(contact.get("last_name") or ""))
    safe_tx_id = (transaction_id or "").strip() or "N/A"
    body = (
        f"Hola {name},\n\n"
        "Pago exitoso en IA-IMP.\n\n"
        "Recibo:\n"
        f"- Referencia: {safe_reference}\n"
        f"- Transaccion: {safe_tx_id}\n"
        f"- Monto acreditado: ${_format_cop(amount_cop)} COP\n"
        f"- Saldo actual: ${_format_cop(balance_cop)} COP\n"
        f"- Fecha (UTC): {datetime.now(timezone.utc).isoformat()}\n"
    )
    return send_email_notification(str(contact["email"]), "Pago exitoso IA-IMP (recibo)", body)


def send_payment_failed_notification(
    *,
    user_id: int,
    reference: str,
    amount_cop: int,
    status: str,
    transaction_id: str,
) -> dict:
    contact = _get_user_contact(user_id)
    if contact is None or not str(contact.get("email") or "").strip():
        return {"delivered": False, "mode": "skipped", "reason": "contacto_no_disponible"}

    safe_reference = (reference or "").strip() or "SIN-REFERENCIA"
    safe_status = (status or "").strip().upper() or "FAILED"
    event_key = f"payment-failed:{safe_reference}:{safe_status}"
    if not _record_notification_event_once(event_key):
        return {"delivered": False, "mode": "skipped", "reason": "already_sent"}

    name = _full_name(str(contact.get("first_name") or ""), str(contact.get("last_name") or ""))
    safe_tx_id = (transaction_id or "").strip() or "N/A"
    body = (
        f"Hola {name},\n\n"
        "Tu intento de pago en IA-IMP no fue aprobado.\n\n"
        "Detalle:\n"
        f"- Referencia: {safe_reference}\n"
        f"- Estado: {safe_status}\n"
        f"- Transaccion: {safe_tx_id}\n"
        f"- Monto solicitado: ${_format_cop(amount_cop)} COP\n"
        f"- Fecha (UTC): {datetime.now(timezone.utc).isoformat()}\n\n"
        "Puedes intentarlo nuevamente desde el modulo de recargas."
    )
    return send_email_notification(str(contact["email"]), "Pago no aprobado en IA-IMP", body)


def send_low_balance_notification(
    *,
    user_id: int,
    email: str,
    first_name: str,
    last_name: str,
    balance_cop: int,
    threshold_cop: int = 1000,
) -> dict:
    if int(balance_cop) > int(threshold_cop):
        return {"delivered": False, "mode": "skipped", "reason": "above_threshold"}

    name = _full_name(first_name, last_name)
    body = (
        f"Hola {name},\n\n"
        "Tu saldo en IA-IMP esta por agotarse.\n"
        f"- Saldo actual: ${_format_cop(balance_cop)} COP\n"
        f"- Umbral de alerta: ${_format_cop(threshold_cop)} COP\n\n"
        "Te recomendamos recargar para evitar interrupciones en tus renders."
    )
    return send_email_notification(email, "Alerta de saldo bajo IA-IMP", body)


def authenticate_user(login: str, password: str) -> dict | None:
    login_value = (login or "").strip()
    if not login_value:
        return None

    try:
        safe_email = _normalize_email(login_value)
    except ValueError:
        return None

    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (safe_email,)).fetchone()
        if row is None:
            return None

        expected = str(row["password_hash"])
        provided = _hash_password(password or "", str(row["salt"]))
        if not hmac.compare_digest(expected, provided):
            return None
        return _public_user(row)


def create_session(user_id: int, days: int = 30) -> str:
    token = secrets.token_urlsafe(36)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=max(1, days))

    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO sessions (token, user_id, expires_at, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (token, int(user_id), expires.isoformat(), now.isoformat()),
        )

    return token


def delete_session(token: str) -> None:
    if not token:
        return
    with _get_conn() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))


def get_user_by_session_token(token: str | None) -> dict | None:
    if not token:
        return None

    now = datetime.now(timezone.utc)
    with _get_conn() as conn:
        row = conn.execute(
            """
            SELECT s.token, s.user_id, s.expires_at, u.id, u.username, u.first_name, u.last_name, u.phone, u.email, u.balance_cop, u.created_at
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token = ?
            """,
            (token,),
        ).fetchone()

        if row is None:
            return None

        expires = datetime.fromisoformat(str(row["expires_at"]))
        if expires < now:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
            return None

        return {
            "user_id": int(row["id"]),
            "username": str(row["username"]),
            "first_name": str(row["first_name"] or ""),
            "last_name": str(row["last_name"] or ""),
            "phone": str(row["phone"] or ""),
            "email": str(row["email"] or ""),
            "balance_cop": int(row["balance_cop"]),
            "created_at": str(row["created_at"] or ""),
        }


def require_authenticated_user(session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME)) -> AuthenticatedUser:
    user = get_user_by_session_token(session_token)
    if user is None:
        raise HTTPException(status_code=401, detail="Debes iniciar sesion")
    return AuthenticatedUser(
        user_id=int(user["user_id"]),
        username=str(user["username"]),
        balance_cop=int(user["balance_cop"]),
    )


def _add_ledger(conn: sqlite3.Connection, user_id: int, tx_type: str, amount_cop: int, module: str, note: str) -> None:
    conn.execute(
        """
        INSERT INTO wallet_ledger (user_id, tx_type, amount_cop, module, note, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (int(user_id), tx_type, int(amount_cop), module, note, _utc_now_iso()),
    )


def get_user_balance(user_id: int) -> int:
    with _get_conn() as conn:
        row = conn.execute("SELECT balance_cop FROM users WHERE id = ?", (int(user_id),)).fetchone()
        if row is None:
            raise ValueError("Usuario no encontrado")
        return int(row["balance_cop"])


def credit_balance(user_id: int, amount_cop: int, module: str, note: str) -> int:
    amount = int(amount_cop)
    if amount <= 0:
        raise ValueError("El monto debe ser mayor a 0")

    with _get_conn() as conn:
        row = conn.execute("SELECT balance_cop FROM users WHERE id = ?", (int(user_id),)).fetchone()
        if row is None:
            raise ValueError("Usuario no encontrado")

        new_balance = int(row["balance_cop"]) + amount
        conn.execute(
            "UPDATE users SET balance_cop = ?, updated_at = ? WHERE id = ?",
            (new_balance, _utc_now_iso(), int(user_id)),
        )
        _add_ledger(conn, int(user_id), "credit", amount, module, note)
        return new_balance


def debit_balance(user_id: int, amount_cop: int, module: str, note: str) -> int:
    amount = int(amount_cop)
    if amount <= 0:
        raise ValueError("El monto debe ser mayor a 0")

    should_notify_low_balance = False
    low_balance_contact: dict | None = None
    low_balance_threshold = 1000

    with _get_conn() as conn:
        row = conn.execute("SELECT balance_cop FROM users WHERE id = ?", (int(user_id),)).fetchone()
        if row is None:
            raise ValueError("Usuario no encontrado")

        current = int(row["balance_cop"])
        if current < amount:
            raise InsufficientBalanceError("Saldo insuficiente")

        new_balance = current - amount
        conn.execute(
            "UPDATE users SET balance_cop = ?, updated_at = ? WHERE id = ?",
            (new_balance, _utc_now_iso(), int(user_id)),
        )
        _add_ledger(conn, int(user_id), "debit", amount, module, note)
        should_notify_low_balance = current > low_balance_threshold and new_balance <= low_balance_threshold
        if should_notify_low_balance:
            contact_row = conn.execute(
                "SELECT email, first_name, last_name FROM users WHERE id = ?",
                (int(user_id),),
            ).fetchone()
            if contact_row is not None:
                low_balance_contact = {
                    "email": str(contact_row["email"] or "").strip(),
                    "first_name": str(contact_row["first_name"] or ""),
                    "last_name": str(contact_row["last_name"] or ""),
                }

    if should_notify_low_balance and low_balance_contact and low_balance_contact.get("email"):
        try:
            send_low_balance_notification(
                user_id=int(user_id),
                email=str(low_balance_contact["email"]),
                first_name=str(low_balance_contact["first_name"]),
                last_name=str(low_balance_contact["last_name"]),
                balance_cop=new_balance,
                threshold_cop=low_balance_threshold,
            )
        except Exception:
            pass

    return new_balance


def get_recent_ledger(user_id: int, limit: int = 50) -> list[dict]:
    safe_limit = max(1, min(200, int(limit)))
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, tx_type, amount_cop, module, note, created_at
            FROM wallet_ledger
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (int(user_id), safe_limit),
        ).fetchall()

    return [
        {
            "id": int(r["id"]),
            "tx_type": str(r["tx_type"]),
            "amount_cop": int(r["amount_cop"]),
            "module": str(r["module"]),
            "note": str(r["note"]),
            "created_at": str(r["created_at"]),
        }
        for r in rows
    ]


def get_user_profile(user_id: int) -> dict:
    with _get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, username, first_name, last_name, phone, email, balance_cop, created_at, updated_at
            FROM users
            WHERE id = ?
            """,
            (int(user_id),),
        ).fetchone()
        if row is None:
            raise ValueError("Usuario no encontrado")
        return _public_user(row)


def list_all_users() -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, username, first_name, last_name, phone, email, balance_cop, created_at, updated_at
            FROM users
            ORDER BY id DESC
            """
        ).fetchall()

    return [
        {
            "user_id": int(row["id"]),
            "username": str(row["username"]),
            "first_name": str(row["first_name"] or ""),
            "last_name": str(row["last_name"] or ""),
            "phone": str(row["phone"] or ""),
            "email": str(row["email"] or ""),
            "balance_cop": int(row["balance_cop"]),
            "created_at": str(row["created_at"] or ""),
            "updated_at": str(row["updated_at"] or ""),
        }
        for row in rows
    ]


def set_user_balance(user_id: int, new_balance_cop: int, module: str = "admin_adjustment", note: str = "Ajuste de saldo por administrador") -> int:
    target_balance = int(new_balance_cop)
    if target_balance < 0:
        raise ValueError("El saldo no puede ser negativo")

    with _get_conn() as conn:
        row = conn.execute("SELECT balance_cop FROM users WHERE id = ?", (int(user_id),)).fetchone()
        if row is None:
            raise ValueError("Usuario no encontrado")

        current_balance = int(row["balance_cop"])
        if current_balance == target_balance:
            return current_balance

        now = _utc_now_iso()
        conn.execute(
            "UPDATE users SET balance_cop = ?, updated_at = ? WHERE id = ?",
            (target_balance, now, int(user_id)),
        )

        delta = target_balance - current_balance
        tx_type = "credit" if delta > 0 else "debit"
        _add_ledger(conn, int(user_id), tx_type, abs(delta), module, note)
        return target_balance


def change_password(user_id: int, current_password: str, new_password: str) -> None:
    if len((new_password or "").strip()) < 6:
        raise ValueError("La nueva contraseña debe tener al menos 6 caracteres")

    with _get_conn() as conn:
        row = conn.execute("SELECT password_hash, salt FROM users WHERE id = ?", (int(user_id),)).fetchone()
        if row is None:
            raise ValueError("Usuario no encontrado")

        expected = str(row["password_hash"])
        provided = _hash_password(current_password or "", str(row["salt"]))
        if not hmac.compare_digest(expected, provided):
            raise ValueError("La contraseña actual no coincide")

        new_salt = secrets.token_hex(16)
        new_hash = _hash_password(new_password, new_salt)
        conn.execute(
            "UPDATE users SET password_hash = ?, salt = ?, updated_at = ? WHERE id = ?",
            (new_hash, new_salt, _utc_now_iso(), int(user_id)),
        )


def update_user_profile(user_id: int, first_name: str, last_name: str, email: str, phone: str, username: str) -> dict:
    safe_first_name = (first_name or "").strip()
    safe_last_name = (last_name or "").strip()
    if len(safe_first_name) < 2:
        raise ValueError("Nombres invalidos")
    if len(safe_last_name) < 2:
        raise ValueError("Apellidos invalidos")

    safe_email = _normalize_email(email)
    safe_phone = _normalize_optional_phone(phone)
    safe_username = _normalize_username(username)

    with _get_conn() as conn:
        existing_user = conn.execute("SELECT id FROM users WHERE id = ?", (int(user_id),)).fetchone()
        if existing_user is None:
            raise ValueError("Usuario no encontrado")

        email_owner = conn.execute("SELECT id FROM users WHERE email = ?", (safe_email,)).fetchone()
        if email_owner is not None and int(email_owner["id"]) != int(user_id):
            raise ValueError("Ese email ya existe")

        username_owner = conn.execute("SELECT id FROM users WHERE username = ?", (safe_username,)).fetchone()
        if username_owner is not None and int(username_owner["id"]) != int(user_id):
            raise ValueError("Ese usuario ya existe")

        conn.execute(
            """
            UPDATE users
            SET username = ?, first_name = ?, last_name = ?, phone = ?, email = ?, updated_at = ?
            WHERE id = ?
            """,
            (safe_username, safe_first_name, safe_last_name, safe_phone, safe_email, _utc_now_iso(), int(user_id)),
        )

        row = conn.execute("SELECT * FROM users WHERE id = ?", (int(user_id),)).fetchone()
        if row is None:
            raise ValueError("Usuario no encontrado")
        return _public_user(row)


def get_user_by_email(email: str) -> dict | None:
    safe_email = _normalize_email(email)
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (safe_email,)).fetchone()
        if row is None:
            return None
        return _public_user(row)


def create_password_reset_token(user_id: int, email: str, minutes_valid: int = 60) -> str:
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=max(5, minutes_valid))

    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO password_reset_tokens (token, user_id, email, expires_at, created_at, sent_at, used_at)
            VALUES (?, ?, ?, ?, ?, NULL, NULL)
            """,
            (token, int(user_id), _normalize_email(email), expires.isoformat(), now.isoformat()),
        )

    return token


def mark_password_reset_sent(token: str) -> None:
    with _get_conn() as conn:
        conn.execute(
            "UPDATE password_reset_tokens SET sent_at = ? WHERE token = ?",
            (_utc_now_iso(), (token or "").strip()),
        )


def reset_password_from_token(token: str, new_password: str) -> dict:
    safe_token = (token or "").strip()
    if len((new_password or "").strip()) < 6:
        raise ValueError("La nueva contraseña debe tener al menos 6 caracteres")

    with _get_conn() as conn:
        row = conn.execute(
            """
            SELECT token, user_id, email, expires_at, used_at
            FROM password_reset_tokens
            WHERE token = ?
            """,
            (safe_token,),
        ).fetchone()
        if row is None:
            raise ValueError("Token de recuperacion invalido")
        if row["used_at"]:
            raise ValueError("Este enlace de recuperacion ya fue usado")

        expires_at = datetime.fromisoformat(str(row["expires_at"]))
        if expires_at < datetime.now(timezone.utc):
            raise ValueError("El enlace de recuperacion expiro")

        new_salt = secrets.token_hex(16)
        new_hash = _hash_password(new_password, new_salt)
        conn.execute(
            "UPDATE users SET password_hash = ?, salt = ?, updated_at = ? WHERE id = ?",
            (new_hash, new_salt, _utc_now_iso(), int(row["user_id"])),
        )
        conn.execute(
            "UPDATE password_reset_tokens SET used_at = ? WHERE token = ?",
            (_utc_now_iso(), safe_token),
        )

    return {"ok": True, "email": str(row["email"])}


def send_email_notification(to_email: str, subject: str, body: str) -> dict:
    safe_to = _normalize_email(to_email)
    host = (os.getenv("SMTP_HOST") or getattr(settings, "smtp_host", "") or "").strip()
    port = int(os.getenv("SMTP_PORT") or getattr(settings, "smtp_port", 587) or 587)
    username = (os.getenv("SMTP_USERNAME") or getattr(settings, "smtp_username", "") or "").strip()
    password = os.getenv("SMTP_PASSWORD") or getattr(settings, "smtp_password", "") or ""
    use_tls = str(os.getenv("SMTP_USE_TLS") or getattr(settings, "smtp_use_tls", "true")).strip().lower() in {"1", "true", "yes", "si", "on"}
    from_email = (os.getenv("SMTP_FROM_EMAIL") or getattr(settings, "smtp_from_email", "") or username or safe_to).strip()

    message = EmailMessage()
    message["From"] = from_email
    message["To"] = safe_to
    message["Subject"] = subject
    message.set_content(body)

    outbox_dir = Path(settings.data_dir) / "email_outbox"
    outbox_dir.mkdir(parents=True, exist_ok=True)

    if host:
        try:
            with smtplib.SMTP(host, port, timeout=20) as server:
                if use_tls:
                    server.starttls()
                if username and password:
                    server.login(username, password)
                server.send_message(message)
            return {"delivered": True, "mode": "smtp"}
        except Exception as exc:
            fallback_path = outbox_dir / f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(8)}.eml"
            fallback_path.write_text(message.as_string(), encoding="utf-8")
            return {"delivered": False, "mode": "outbox", "reason": str(exc), "file": str(fallback_path)}

    fallback_path = outbox_dir / f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(8)}.eml"
    fallback_path.write_text(message.as_string(), encoding="utf-8")
    return {"delivered": False, "mode": "outbox", "file": str(fallback_path)}


def create_password_reset_notification(email: str, user_id: int, base_url: str) -> dict:
    token = create_password_reset_token(user_id, email)
    reset_url = f"{base_url.rstrip('/')}/studio?reset_token={token}"
    body = (
        "Hemos recibido una solicitud para restablecer tu contraseña en IA-IMP.\n\n"
        f"Usa este enlace para continuar: {reset_url}\n\n"
        "Si no solicitaste este cambio, ignora este mensaje."
    )
    delivery = send_email_notification(email, "Recuperacion de contraseña IA-IMP", body)
    mark_password_reset_sent(token)
    return {"token": token, "reset_url": reset_url, "delivery": delivery}


def create_recharge_payment_intent(
    user_id: int,
    reference: str,
    amount_cop: int,
    amount_in_cents: int,
    currency: str,
    checkout_url: str,
) -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO recharge_payments (
              reference, user_id, amount_cop, amount_in_cents, currency, status,
              transaction_id, checkout_url, gateway_payload, created_at, updated_at, settled_at
            )
            VALUES (?, ?, ?, ?, ?, 'PENDING', NULL, ?, '', ?, ?, NULL)
            """,
            (
                reference,
                int(user_id),
                int(amount_cop),
                int(amount_in_cents),
                currency,
                checkout_url,
                _utc_now_iso(),
                _utc_now_iso(),
            ),
        )


def get_recharge_payment_intent(reference: str) -> dict | None:
    with _get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, reference, user_id, amount_cop, amount_in_cents, currency, status,
                   transaction_id, checkout_url, gateway_payload, created_at, updated_at, settled_at
            FROM recharge_payments
            WHERE reference = ?
            """,
            (reference,),
        ).fetchone()

    if row is None:
        return None

    return {
        "id": int(row["id"]),
        "reference": str(row["reference"]),
        "user_id": int(row["user_id"]),
        "amount_cop": int(row["amount_cop"]),
        "amount_in_cents": int(row["amount_in_cents"]),
        "currency": str(row["currency"]),
        "status": str(row["status"]),
        "transaction_id": str(row["transaction_id"] or ""),
        "checkout_url": str(row["checkout_url"] or ""),
        "gateway_payload": str(row["gateway_payload"] or ""),
        "created_at": str(row["created_at"]),
        "updated_at": str(row["updated_at"]),
        "settled_at": str(row["settled_at"] or ""),
    }


def list_pending_recharge_payment_intents(user_id: int, limit: int = 30) -> list[dict]:
    safe_limit = max(1, min(200, int(limit)))
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, reference, user_id, amount_cop, amount_in_cents, currency, status,
                   transaction_id, checkout_url, gateway_payload, created_at, updated_at, settled_at
            FROM recharge_payments
            WHERE user_id = ? AND settled_at IS NULL
            ORDER BY id DESC
            LIMIT ?
            """,
            (int(user_id), safe_limit),
        ).fetchall()

    return [
        {
            "id": int(row["id"]),
            "reference": str(row["reference"]),
            "user_id": int(row["user_id"]),
            "amount_cop": int(row["amount_cop"]),
            "amount_in_cents": int(row["amount_in_cents"]),
            "currency": str(row["currency"]),
            "status": str(row["status"]),
            "transaction_id": str(row["transaction_id"] or ""),
            "checkout_url": str(row["checkout_url"] or ""),
            "gateway_payload": str(row["gateway_payload"] or ""),
            "created_at": str(row["created_at"]),
            "updated_at": str(row["updated_at"]),
            "settled_at": str(row["settled_at"] or ""),
        }
        for row in rows
    ]


def set_recharge_payment_status(reference: str, status: str, transaction_id: str = "", gateway_payload: str = "") -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            UPDATE recharge_payments
            SET status = ?, transaction_id = ?, gateway_payload = ?, updated_at = ?
            WHERE reference = ?
            """,
            (status, transaction_id or None, gateway_payload or "", _utc_now_iso(), reference),
        )


def settle_recharge_if_approved(
    *,
    reference: str,
    transaction_id: str,
    gateway_payload: str,
) -> dict:
    with _get_conn() as conn:
        conn.isolation_level = None
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            """
            SELECT id, user_id, amount_cop, status, settled_at
            FROM recharge_payments
            WHERE reference = ?
            """,
            (reference,),
        ).fetchone()
        if row is None:
            conn.execute("ROLLBACK")
            raise ValueError("Referencia de recarga no encontrada")

        if row["settled_at"]:
            user_row = conn.execute("SELECT balance_cop FROM users WHERE id = ?", (int(row["user_id"]),)).fetchone()
            balance = int(user_row["balance_cop"]) if user_row is not None else 0
            conn.execute("ROLLBACK")
            return {"already_applied": True, "balance_cop": balance}

        user_row = conn.execute("SELECT balance_cop FROM users WHERE id = ?", (int(row["user_id"]),)).fetchone()
        if user_row is None:
            conn.execute("ROLLBACK")
            raise ValueError("Usuario de recarga no encontrado")

        amount = int(row["amount_cop"])
        new_balance = int(user_row["balance_cop"]) + amount

        now = _utc_now_iso()
        conn.execute(
            "UPDATE users SET balance_cop = ?, updated_at = ? WHERE id = ?",
            (new_balance, now, int(row["user_id"])),
        )
        _add_ledger(
            conn,
            int(row["user_id"]),
            "credit",
            amount,
            "wompi_recharge",
            f"Recarga aprobada Wompi ({reference})",
        )
        conn.execute(
            """
            UPDATE recharge_payments
            SET status = 'APPROVED', transaction_id = ?, gateway_payload = ?, updated_at = ?, settled_at = ?
            WHERE reference = ?
            """,
            (transaction_id, gateway_payload or "", now, now, reference),
        )
        conn.execute("COMMIT")
        return {"already_applied": False, "balance_cop": new_balance}
