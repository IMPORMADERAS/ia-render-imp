import hashlib
import hmac
import re
import secrets
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import Cookie, HTTPException

from ..config import settings
from .security import ensure_strong_password, insecure_admin_credentials

DB_PATH = Path(settings.data_dir) / "accounts.db"
ADMIN_SESSION_COOKIE_NAME = "iaimp_admin_session"
USERNAME_RE = re.compile(r"^[a-zA-Z0-9._-]{3,32}$")


@dataclass
class AdminUser:
    admin_id: int
    username: str


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def _hash_password(password: str, salt: str) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 240_000)
    return dk.hex()


def _normalize_username(username: str) -> str:
    value = (username or "").strip().lower()
    if not USERNAME_RE.fullmatch(value):
        raise ValueError("Usuario invalido. Usa 3-32 caracteres: letras, numeros, ., _, -")
    return value


def init_admin_auth_db() -> None:
    with _get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS admin_accounts (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT UNIQUE NOT NULL,
              password_hash TEXT NOT NULL,
              salt TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS admin_sessions (
              token TEXT PRIMARY KEY,
              admin_id INTEGER NOT NULL,
              expires_at TEXT NOT NULL,
              created_at TEXT NOT NULL,
              FOREIGN KEY(admin_id) REFERENCES admin_accounts(id)
            );
            """
        )

        raw_username = (settings.admin_username or "").strip()
        password = (settings.admin_password or "").strip()
        if settings.is_production:
            if not raw_username or not password:
                raise RuntimeError("Debes configurar ADMIN_USERNAME y ADMIN_PASSWORD en produccion")
            if insecure_admin_credentials(raw_username, password):
                raise RuntimeError("No puedes usar credenciales admin por defecto en produccion")

        if not raw_username or not password:
            return

        username = _normalize_username(raw_username)
        ensure_strong_password(password)

        salt = secrets.token_hex(16)
        password_hash = _hash_password(password, salt)
        now = _utc_now_iso()

        row = conn.execute("SELECT id FROM admin_accounts WHERE username = ?", (username,)).fetchone()
        if row is None:
            conn.execute(
                """
                INSERT INTO admin_accounts (username, password_hash, salt, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, password_hash, salt, now, now),
            )
        else:
            conn.execute(
                """
                UPDATE admin_accounts
                SET password_hash = ?, salt = ?, updated_at = ?
                WHERE username = ?
                """,
                (password_hash, salt, now, username),
            )


def authenticate_admin(login: str, password: str) -> dict | None:
    login_value = (login or "").strip()
    if not login_value:
        return None

    try:
        safe_username = _normalize_username(login_value)
    except ValueError:
        return None

    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM admin_accounts WHERE username = ?", (safe_username,)).fetchone()
        if row is None:
            return None

        expected = str(row["password_hash"])
        provided = _hash_password(password or "", str(row["salt"]))
        if not hmac.compare_digest(expected, provided):
            return None

        return {"admin_id": int(row["id"]), "username": str(row["username"])}


def create_admin_session(admin_id: int, days: int = 30) -> str:
    token = secrets.token_urlsafe(36)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=max(1, days))

    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO admin_sessions (token, admin_id, expires_at, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (token, int(admin_id), expires.isoformat(), now.isoformat()),
        )

    return token


def delete_admin_session(token: str) -> None:
    if not token:
        return
    with _get_conn() as conn:
        conn.execute("DELETE FROM admin_sessions WHERE token = ?", (token,))


def get_admin_by_session_token(token: str | None) -> dict | None:
    if not token:
        return None

    now = datetime.now(timezone.utc)
    with _get_conn() as conn:
        row = conn.execute(
            """
            SELECT s.token, s.admin_id, s.expires_at, a.id, a.username
            FROM admin_sessions s
            JOIN admin_accounts a ON a.id = s.admin_id
            WHERE s.token = ?
            """,
            (token,),
        ).fetchone()

        if row is None:
            return None

        expires = datetime.fromisoformat(str(row["expires_at"]))
        if expires < now:
            conn.execute("DELETE FROM admin_sessions WHERE token = ?", (token,))
            return None

        return {"admin_id": int(row["id"]), "username": str(row["username"])}


def require_admin_user(session_token: str | None = Cookie(default=None, alias=ADMIN_SESSION_COOKIE_NAME)) -> AdminUser:
    admin = get_admin_by_session_token(session_token)
    if admin is None:
        raise HTTPException(status_code=401, detail="Debes iniciar sesion como administrador")
    return AdminUser(admin_id=int(admin["admin_id"]), username=str(admin["username"]))