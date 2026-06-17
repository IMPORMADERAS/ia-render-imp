from collections import Counter

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from ..services.admin_auth import (
    ADMIN_SESSION_COOKIE_NAME,
    AdminUser,
    authenticate_admin,
    create_admin_session,
    delete_admin_session,
    require_admin_user,
)
from ..services.auth_wallet import list_all_users, set_user_balance
from ..services.storage import list_user_generation_history
from ..services.pricing_store import get_pricing_config, save_pricing_config

router = APIRouter(prefix="/admin-api", tags=["admin"])


class AdminLoginRequest(BaseModel):
    login: str
    password: str


class AdminBalanceRequest(BaseModel):
    balance_cop: int
    note: str = "Saldo ajustado por administrador"


class PricingConfigRequest(BaseModel):
    pricing: dict


def _session_cookie_max_age(days: int = 30) -> int:
    return max(1, days) * 24 * 60 * 60


def _summarize_generations(items: list[dict]) -> dict[str, int]:
    summary: Counter[str] = Counter()
    for item in items:
        module = str(item.get("module") or "unknown")
        summary[module] += 1
    return dict(summary)


def _build_user_snapshot(user: dict, detail_limit: int = 500) -> dict:
    generations = list_user_generation_history(int(user["user_id"]), limit=detail_limit)
    summary = _summarize_generations(generations)
    total = sum(summary.values())
    return {
        "user": user,
        "balance_cop": int(user.get("balance_cop") or 0),
        "generation_total": total,
        "generation_by_module": summary,
        "generations": generations,
    }


@router.post("/login", response_model=dict)
def login(payload: AdminLoginRequest, response: Response):
    admin = authenticate_admin(payload.login, payload.password)
    if admin is None:
        raise HTTPException(status_code=401, detail="Usuario o contraseña de administrador incorrectos")

    token = create_admin_session(int(admin["admin_id"]), days=30)
    response.set_cookie(
        key=ADMIN_SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=_session_cookie_max_age(30),
    )
    return {"authenticated": True, "admin": admin}


@router.post("/logout", response_model=dict)
def logout(
    response: Response,
    admin: AdminUser = Depends(require_admin_user),
    session_token: str | None = Cookie(default=None, alias=ADMIN_SESSION_COOKIE_NAME),
):
    del admin
    delete_admin_session(session_token or "")
    response.delete_cookie(ADMIN_SESSION_COOKIE_NAME)
    return {"ok": True}


@router.get("/me", response_model=dict)
def me(admin: AdminUser = Depends(require_admin_user)):
    return {"authenticated": True, "admin": {"admin_id": admin.admin_id, "username": admin.username}}


@router.get("/users", response_model=dict)
def users(admin: AdminUser = Depends(require_admin_user)):
    del admin
    snapshots = []
    for user in list_all_users():
        generations = list_user_generation_history(int(user["user_id"]), limit=500)
        summary = _summarize_generations(generations)
        snapshots.append(
            {
                "user": user,
                "balance_cop": int(user.get("balance_cop") or 0),
                "generation_total": sum(summary.values()),
                "generation_by_module": summary,
                "last_generation_at": generations[0]["updated_at"] if generations else "",
            }
        )

    return {"items": snapshots}


@router.get("/users/{user_id}", response_model=dict)
def user_detail(user_id: int, admin: AdminUser = Depends(require_admin_user)):
    del admin
    user = next((item for item in list_all_users() if int(item["user_id"]) == int(user_id)), None)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return _build_user_snapshot(user, detail_limit=500)


@router.patch("/users/{user_id}/balance", response_model=dict)
def update_balance(user_id: int, payload: AdminBalanceRequest, admin: AdminUser = Depends(require_admin_user)):
    del admin
    try:
        new_balance = set_user_balance(int(user_id), int(payload.balance_cop), note=payload.note)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"ok": True, "balance_cop": new_balance}


@router.get("/pricing", response_model=dict)
def pricing(admin: AdminUser = Depends(require_admin_user)):
    del admin
    return {"pricing": get_pricing_config()}


@router.patch("/pricing", response_model=dict)
def update_pricing(payload: PricingConfigRequest, admin: AdminUser = Depends(require_admin_user)):
    del admin
    try:
        updated = save_pricing_config(payload.pricing)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, "pricing": updated}