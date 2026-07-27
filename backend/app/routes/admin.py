from collections import Counter

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from ..config import settings
from ..services.rate_limit import client_ip_from_request, enforce_rate_limit, reset_rate_limit
from ..services.admin_auth import (
    ADMIN_SESSION_COOKIE_NAME,
    AdminUser,
    authenticate_admin,
    create_admin_session,
    delete_admin_session,
    require_admin_user,
)
from ..services.auth_wallet import list_all_users, set_user_balance
from ..services.capacity_advisor import get_capacity_advice
from ..services.consistency import get_consistency_report
from ..services.metrics import get_metrics_snapshot
from ..services.primary_router import module_cutover_config
from ..services.postgres_mirror import get_postgres_mirror_health
from ..services.queue import get_queue_health_metrics
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


def _set_admin_cookie(response: Response, token: str, days: int = 30) -> None:
    response.set_cookie(
        key=ADMIN_SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.secure_cookies,
        max_age=_session_cookie_max_age(days),
        path="/",
    )


def _delete_admin_cookie(response: Response) -> None:
    response.delete_cookie(ADMIN_SESSION_COOKIE_NAME, path="/", secure=settings.secure_cookies, httponly=True, samesite="lax")


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
def login(payload: AdminLoginRequest, response: Response, request: Request):
    safe_login = (payload.login or "").strip().lower()
    rate_key = f"{client_ip_from_request(request)}:{safe_login}"
    enforce_rate_limit("admin-login", rate_key, max_attempts=5, window_seconds=600, block_seconds=1800)

    admin = authenticate_admin(payload.login, payload.password)
    if admin is None:
        raise HTTPException(status_code=401, detail="Usuario o contraseña de administrador incorrectos")

    token = create_admin_session(int(admin["admin_id"]), days=30)
    reset_rate_limit("admin-login", rate_key)
    _set_admin_cookie(response, token, days=30)
    return {"authenticated": True, "admin": admin}


@router.post("/logout", response_model=dict)
def logout(
    response: Response,
    admin: AdminUser = Depends(require_admin_user),
    session_token: str | None = Cookie(default=None, alias=ADMIN_SESSION_COOKIE_NAME),
):
    del admin
    delete_admin_session(session_token or "")
    _delete_admin_cookie(response)
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


@router.get("/infra/health", response_model=dict)
def infra_health(admin: AdminUser = Depends(require_admin_user)):
    del admin
    queue_health = get_queue_health_metrics()
    pg_health = get_postgres_mirror_health()
    return {
        "ok": bool(queue_health.get("redis_ok") or not queue_health.get("redis_configured")),
        "queue": queue_health,
        "postgres_mirror": pg_health,
    }


@router.get("/infra/cutover", response_model=dict)
def infra_cutover(admin: AdminUser = Depends(require_admin_user)):
    del admin
    modules = [
        module_cutover_config("auth"),
        module_cutover_config("wallet"),
        module_cutover_config("jobs"),
    ]
    return {"modules": modules}


@router.get("/infra/consistency", response_model=dict)
def infra_consistency(admin: AdminUser = Depends(require_admin_user)):
    del admin
    return get_consistency_report()


@router.get("/infra/metrics", response_model=dict)
def infra_metrics(admin: AdminUser = Depends(require_admin_user)):
    del admin
    return get_metrics_snapshot()


@router.get("/infra/advice", response_model=dict)
def infra_advice(admin: AdminUser = Depends(require_admin_user)):
    del admin
    return get_capacity_advice()