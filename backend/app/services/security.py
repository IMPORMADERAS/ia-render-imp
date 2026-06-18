import re


DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "Admin1234!"
PASSWORD_MIN_LENGTH = 10


def password_strength_error(password: str) -> str | None:
    value = (password or "").strip()
    if len(value) < PASSWORD_MIN_LENGTH:
        return f"La contraseña debe tener al menos {PASSWORD_MIN_LENGTH} caracteres"
    if not re.search(r"[a-z]", value):
        return "La contraseña debe incluir al menos una letra minúscula"
    if not re.search(r"[A-Z]", value):
        return "La contraseña debe incluir al menos una letra mayúscula"
    if not re.search(r"\d", value):
        return "La contraseña debe incluir al menos un numero"
    return None


def ensure_strong_password(password: str) -> None:
    error = password_strength_error(password)
    if error:
        raise ValueError(error)


def insecure_admin_credentials(username: str, password: str) -> bool:
    return (username or "").strip().lower() == DEFAULT_ADMIN_USERNAME and (password or "") == DEFAULT_ADMIN_PASSWORD