from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ..config import settings
from ..services.rate_limit import client_ip_from_request, enforce_rate_limit, reset_rate_limit
from ..services.auth_wallet import (
    SESSION_COOKIE_NAME,
    AuthenticatedUser,
    authenticate_user,
    change_password,
    create_password_reset_notification,
    create_session,
    credit_balance,
    delete_user_account,
    delete_session,
    get_user_by_email,
    get_user_profile,
    get_recent_ledger,
    get_user_balance,
    register_user,
    require_authenticated_user,
    reset_password_from_token,
    send_password_reset_success_notification,
    send_registration_success_notification,
    update_user_profile,
)
from ..services.storage import delete_user_generation_data, get_user_generation_download, list_user_generation_history

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    password_confirm: str


class LoginRequest(BaseModel):
    login: str
    password: str


class RechargeRequest(BaseModel):
    amount_cop: int


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str


class RecoverPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_new_password: str


class UpdateProfileRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str = ""
    username: str


class DeleteAccountRequest(BaseModel):
    confirm: bool


def _session_cookie_max_age(days: int = 30) -> int:
    return max(1, days) * 24 * 60 * 60


def _set_auth_cookie(response: Response, token: str, days: int = 30) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.secure_cookies,
        max_age=_session_cookie_max_age(days),
        path="/",
    )


def _delete_auth_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE_NAME, path="/", secure=settings.secure_cookies, httponly=True, samesite="lax")


@router.post("/register", response_model=dict)
def register(payload: RegisterRequest, response: Response):
    if payload.password != payload.password_confirm:
        raise HTTPException(status_code=400, detail="La confirmacion de contraseña no coincide")

    try:
        created = register_user(payload.first_name, payload.last_name, payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    token = create_session(int(created["user_id"]), days=30)
    _set_auth_cookie(response, token, days=30)
    try:
        send_registration_success_notification(created)
    except Exception:
        pass
    return {
        "authenticated": True,
        "user": created,
    }


@router.post("/login", response_model=dict)
def login(payload: LoginRequest, response: Response, request: Request):
    safe_login = (payload.login or "").strip().lower()
    rate_key = f"{client_ip_from_request(request)}:{safe_login}"
    enforce_rate_limit("auth-login", rate_key, max_attempts=6, window_seconds=300, block_seconds=900)

    user = authenticate_user(payload.login, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = create_session(int(user["user_id"]), days=30)
    reset_rate_limit("auth-login", rate_key)
    _set_auth_cookie(response, token, days=30)
    return {
        "authenticated": True,
        "user": user,
    }


@router.post("/recover-password", response_model=dict)
def recover_password(payload: RecoverPasswordRequest, request: Request):
    safe_email = (payload.email or "").strip().lower()
    rate_key = f"{client_ip_from_request(request)}:{safe_email}"
    enforce_rate_limit("auth-recover", rate_key, max_attempts=4, window_seconds=600, block_seconds=1800)

    try:
        user = get_user_by_email(payload.email)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if user is None:
        return {
            "ok": True,
            "message": "Si el email está registrado, te enviaremos instrucciones para recuperar tu contraseña.",
            "delivery": {"delivered": False, "mode": "skipped"},
        }

    result = create_password_reset_notification(user["email"], int(user["user_id"]), str(request.base_url))
    return {
        "ok": True,
        "message": "Te enviamos un correo con instrucciones para recuperar tu contraseña.",
        "delivery": result["delivery"],
    }


@router.post("/reset-password", response_model=dict)
def reset_password(payload: ResetPasswordRequest):
    if payload.new_password != payload.confirm_new_password:
        raise HTTPException(status_code=400, detail="La nueva contraseña y su confirmacion no coinciden")

    try:
        result = reset_password_from_token(payload.token, payload.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        send_password_reset_success_notification(str(result["email"]))
    except Exception:
        pass

    return {"ok": True, "email": result["email"]}


@router.post("/logout", response_model=dict)
def logout(
    response: Response,
    user: AuthenticatedUser = Depends(require_authenticated_user),
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
):
    del user
    # Remove persisted session token and clear browser cookie.
    delete_session(session_token or "")
    _delete_auth_cookie(response)
    return {"ok": True}


@router.get("/me", response_model=dict)
def me(user: AuthenticatedUser = Depends(require_authenticated_user)):
    profile = get_user_profile(user.user_id)
    return {
        "authenticated": True,
        "user": profile,
    }


@router.post("/recharge", response_model=dict)
def recharge(payload: RechargeRequest, user: AuthenticatedUser = Depends(require_authenticated_user)):
    amount = int(payload.amount_cop)
    if amount not in {5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000}:
        raise HTTPException(status_code=400, detail="Plan de recarga invalido")

    new_balance = credit_balance(
        user.user_id,
        amount,
        module="recharge",
        note=f"Recarga manual {amount} COP",
    )
    return {"ok": True, "balance_cop": new_balance}


@router.get("/ledger", response_model=dict)
def ledger(user: AuthenticatedUser = Depends(require_authenticated_user)):
    return {"items": get_recent_ledger(user.user_id, limit=100)}


@router.get("/generations", response_model=dict)
def generations(user: AuthenticatedUser = Depends(require_authenticated_user)):
    return {"items": list_user_generation_history(user.user_id, limit=200)}


@router.get("/account", response_model=dict)
def account_summary(user: AuthenticatedUser = Depends(require_authenticated_user)):
    profile = get_user_profile(user.user_id)
    return {
        "user": profile,
        "balance_cop": get_user_balance(user.user_id),
        "ledger": get_recent_ledger(user.user_id, limit=80),
        "generations": list_user_generation_history(user.user_id, limit=120),
    }


@router.post("/change-password", response_model=dict)
def update_password(payload: ChangePasswordRequest, user: AuthenticatedUser = Depends(require_authenticated_user)):
    if payload.new_password != payload.confirm_new_password:
        raise HTTPException(status_code=400, detail="La nueva contraseña y su confirmacion no coinciden")

    try:
        change_password(user.user_id, payload.current_password, payload.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"ok": True}


@router.patch("/profile", response_model=dict)
def update_profile(payload: UpdateProfileRequest, user: AuthenticatedUser = Depends(require_authenticated_user)):
    try:
        profile = update_user_profile(
            user.user_id,
            payload.first_name,
            payload.last_name,
            payload.email,
            payload.phone,
            payload.username,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"ok": True, "user": profile}


@router.get("/downloads/{output_type}/{output_id}")
def download_generation(
    output_type: str,
    output_id: str,
    user: AuthenticatedUser = Depends(require_authenticated_user),
):
    VALID_TYPES = {"job", "anim", "music"}
    if output_type not in VALID_TYPES:
        raise HTTPException(status_code=400, detail="Tipo de generacion invalido")

    try:
        file_path, filename = get_user_generation_download(user.user_id, output_type, output_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    import mimetypes as _mt
    media_type = _mt.guess_type(str(file_path))[0] or "application/octet-stream"
    return FileResponse(path=str(file_path), media_type=media_type, filename=filename)


@router.post("/delete-account", response_model=dict)
def delete_account(
    payload: DeleteAccountRequest,
    response: Response,
    user: AuthenticatedUser = Depends(require_authenticated_user),
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
):
    if not bool(payload.confirm):
        raise HTTPException(status_code=400, detail="Debes confirmar la eliminacion de la cuenta")

    storage_summary = delete_user_generation_data(user.user_id)
    account_summary = delete_user_account(user.user_id)

    delete_session(session_token or "")
    _delete_auth_cookie(response)

    return {
        "ok": True,
        "message": "Cuenta eliminada correctamente",
        "account": account_summary,
        "storage": storage_summary,
    }
