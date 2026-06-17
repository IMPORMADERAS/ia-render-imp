import json
from hmac import compare_digest
from hashlib import sha256
from urllib.parse import quote, urlparse, urlunparse
from uuid import uuid4

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, field_validator

from ..config import settings
from ..services.auth_wallet import (
    AuthenticatedUser,
    create_recharge_payment_intent,
    get_recharge_payment_intent,
    get_user_balance,
    list_pending_recharge_payment_intents,
    require_authenticated_user,
    send_payment_failed_notification,
    send_payment_success_notification,
    set_recharge_payment_status,
    settle_recharge_if_approved,
)
from ..services.pricing_store import get_pricing_config, get_wompi_coverage_factor

router = APIRouter(prefix="/payments", tags=["payments"])

FAILED_PAYMENT_STATUSES = {"DECLINED", "ERROR", "VOIDED", "FAILED", "CANCELLED"}


class WompiCheckoutRequest(BaseModel):
    amount_cop: int
    redirect_url: str = ""

    @field_validator("amount_cop")
    @classmethod
    def validate_amount(cls, value: int) -> int:
        if value < int(settings.wompi_min_recharge_cop):
            raise ValueError(f"El monto minimo es {settings.wompi_min_recharge_cop} COP")
        return value


class WompiConfirmRequest(BaseModel):
    reference: str
    transaction_id: str = ""


def _build_redirect_url(raw_url: str) -> str:
    candidate = (raw_url or "").strip()
    if not candidate:
        return ""

    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise HTTPException(status_code=400, detail="redirect_url invalida")

    sanitized = parsed._replace(query="", fragment="")
    return urlunparse(sanitized)


def _is_local_redirect(url: str) -> bool:
    if not url:
        return False
    host = (urlparse(url).hostname or "").strip().lower()
    return host in {"127.0.0.1", "localhost", "0.0.0.0"}


def _append_redirect_reference(base_url: str, reference: str) -> str:
    if not base_url:
        return ""
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}wompi_ref={quote(reference, safe='')}"


def _calculate_fees(amount_cop: int) -> dict[str, int]:
    pricing = get_pricing_config()
    payment_processing_fee = int(round(amount_cop * float(pricing.get("wompi_percent", 0.0265)) + float(pricing.get("wompi_fixed_fee", 700))))
    iva = int(round(payment_processing_fee * float(pricing.get("wompi_iva_rate", 0.19))))
    commercial_margin = int(round(amount_cop * 0.5))
    total_extra = payment_processing_fee + iva + commercial_margin
    return {
        "payment_processing_fee": payment_processing_fee,
        "iva": iva,
        "commercial_margin": commercial_margin,
        "total_extra": total_extra,
        "total_cop": amount_cop + total_extra,
    }


def _wompi_auth_header() -> dict[str, str]:
    token = (settings.wompi_private_key or "").strip()
    if not token:
        raise HTTPException(
            status_code=500,
            detail="Falta WOMPI_PRIVATE_KEY para consultar transacciones en Wompi",
        )
    if token.startswith("pub_"):
        raise HTTPException(
            status_code=500,
            detail="WOMPI_PRIVATE_KEY no es valido (debe iniciar por prv_)",
        )
    return {"Authorization": f"Bearer {token}"}


def _fetch_wompi_transaction_by_id(transaction_id: str) -> dict | None:
    if not transaction_id.strip():
        return None

    url = f"{settings.wompi_api_base_url.rstrip('/')}/transactions/{quote(transaction_id.strip(), safe='')}"
    last_status = 0
    last_detail = ""

    # Wompi allows fetching transaction detail by id without auth.
    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url)
        last_status = int(response.status_code)
        if response.status_code < 400:
            payload = response.json() if response.content else {}
            data = payload.get("data") if isinstance(payload, dict) else None
            return data if isinstance(data, dict) else None
        if response.status_code == 404:
            return None
        last_detail = response.text[:240]
    except Exception as exc:
        last_detail = str(exc)

    # Fallback to private-key auth for environments/accounts that require it.
    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_wompi_auth_header())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"No se pudo consultar Wompi: {exc}") from exc

    if response.status_code == 404:
        return None

    if response.status_code >= 400:
        detail = f"Wompi respondio {response.status_code} al consultar transaccion"
        if last_status:
            detail = (
                f"{detail} (intento publico previo: {last_status}"
                f"{', ' + last_detail if last_detail else ''})"
            )
        raise HTTPException(status_code=502, detail=detail)

    payload = response.json() if response.content else {}
    data = payload.get("data") if isinstance(payload, dict) else None
    return data if isinstance(data, dict) else None


def _fetch_wompi_latest_transaction_by_reference(reference: str) -> dict | None:
    url = f"{settings.wompi_api_base_url.rstrip('/')}/transactions?reference={quote(reference, safe='')}"
    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_wompi_auth_header())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"No se pudo consultar Wompi: {exc}") from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Wompi respondio {response.status_code} al consultar referencia")

    payload = response.json() if response.content else {}
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, list) or not data:
        return None

    data.sort(key=lambda x: str(x.get("created_at") or ""), reverse=True)
    return data[0] if isinstance(data[0], dict) else None


def _validate_wompi_private_key_access() -> None:
    # Use a reference lookup because Wompi validates token here and returns 401/403 for invalid keys.
    url = f"{settings.wompi_api_base_url.rstrip('/')}/transactions?reference=IAIMP-HEALTHCHECK"
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, headers=_wompi_auth_header())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"No se pudo validar acceso a Wompi: {exc}") from exc

    if response.status_code in {401, 403}:
        raise HTTPException(
            status_code=500,
            detail="WOMPI_PRIVATE_KEY invalida o sin permisos para API (401/403)",
        )
    if response.status_code >= 500:
        raise HTTPException(status_code=502, detail=f"Wompi no disponible ({response.status_code})")


def _checksum_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    return str(value)


def _resolve_property(data: dict, dotted_path: str) -> str:
    current: object = data
    for part in dotted_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
            continue
        return ""
    return _checksum_value(current)


def _verify_wompi_event_checksum(payload: dict, header_checksum: str | None) -> bool:
    events_secret = (settings.wompi_events_key or "").strip()
    if not events_secret:
        raise HTTPException(status_code=500, detail="Falta WOMPI_EVENTS_KEY para validar eventos")

    signature = payload.get("signature") if isinstance(payload, dict) else None
    signature_dict = signature if isinstance(signature, dict) else {}
    properties = signature_dict.get("properties")
    properties_list = properties if isinstance(properties, list) else []

    data = payload.get("data") if isinstance(payload, dict) else None
    data_dict = data if isinstance(data, dict) else {}

    timestamp = payload.get("timestamp") if isinstance(payload, dict) else None
    if timestamp is None:
        return False

    payload_parts = []
    for prop in properties_list:
        if not isinstance(prop, str):
            continue
        payload_parts.append(_resolve_property(data_dict, prop))

    raw_string = "".join(payload_parts) + str(timestamp) + events_secret
    expected_checksum = sha256(raw_string.encode("utf-8")).hexdigest().upper()

    body_checksum = str(signature_dict.get("checksum") or "").strip().upper()
    header_checksum_clean = str(header_checksum or "").strip().upper()

    if body_checksum and header_checksum_clean and not compare_digest(body_checksum, header_checksum_clean):
        return False

    provided_checksum = header_checksum_clean or body_checksum
    if not provided_checksum:
        return False

    return compare_digest(expected_checksum, provided_checksum)


@router.post("/wompi/checkout", response_model=dict)
def create_wompi_checkout(payload: WompiCheckoutRequest, user: AuthenticatedUser = Depends(require_authenticated_user)):
    missing_keys: list[str] = []
    if not settings.wompi_public_key:
        missing_keys.append("WOMPI_PUBLIC_KEY")
    if not settings.wompi_integrity_key:
        missing_keys.append("WOMPI_INTEGRITY_KEY")
    if missing_keys:
        raise HTTPException(
            status_code=500,
            detail=f"Faltan credenciales de Wompi en backend/.env: {', '.join(missing_keys)}",
        )

    base_amount_cop = int(payload.amount_cop)
    fees = _calculate_fees(base_amount_cop)
    charge_amount_cop = base_amount_cop
    amount_in_cents = charge_amount_cop * 100
    reference = f"IAIMP-{uuid4().hex[:12].upper()}"
    currency = (settings.wompi_currency or "COP").strip().upper()
    redirect_url = _build_redirect_url(payload.redirect_url)

    # Wompi production checkout can reject localhost redirect URLs.
    # If prod keys are in use during local tests, omit redirect-url.
    if settings.wompi_public_key.strip().startswith("pub_prod_") and _is_local_redirect(redirect_url):
        redirect_url = ""

    if redirect_url:
        redirect_url = _append_redirect_reference(redirect_url, reference)

    signature_payload = f"{reference}{amount_in_cents}{currency}{settings.wompi_integrity_key}"
    signature = sha256(signature_payload.encode("utf-8")).hexdigest()

    query_parts = [
        ("public-key", settings.wompi_public_key),
        ("currency", currency),
        ("amount-in-cents", str(amount_in_cents)),
        ("reference", reference),
        ("signature:integrity", signature),
    ]
    if redirect_url:
        query_parts.append(("redirect-url", redirect_url))

    checkout_query = "&".join(f"{key}={quote(value, safe='')}" for key, value in query_parts)
    checkout_url = f"{settings.wompi_checkout_base_url}?{checkout_query}"

    create_recharge_payment_intent(
        user_id=user.user_id,
        reference=reference,
        amount_cop=charge_amount_cop,
        amount_in_cents=amount_in_cents,
        currency=currency,
        checkout_url=checkout_url,
    )

    return {
        "checkout_url": checkout_url,
        "reference": reference,
        "currency": currency,
        "amount_cop": charge_amount_cop,
        "base_amount_cop": base_amount_cop,
        "amount_in_cents": amount_in_cents,
        "fees": fees,
        "note": "Checkout generado para el valor exacto del plan.",
    }


@router.post("/wompi/confirm", response_model=dict)
def confirm_wompi_payment(payload: WompiConfirmRequest, user: AuthenticatedUser = Depends(require_authenticated_user)):
    reference = (payload.reference or "").strip()
    if not reference:
        raise HTTPException(status_code=400, detail="Referencia requerida")

    intent = get_recharge_payment_intent(reference)
    if intent is None:
        raise HTTPException(status_code=404, detail="Referencia de recarga no encontrada")
    if int(intent["user_id"]) != int(user.user_id):
        raise HTTPException(status_code=403, detail="Esta referencia no pertenece a tu cuenta")

    tx = None
    transaction_id = (payload.transaction_id or "").strip()
    if transaction_id:
        tx = _fetch_wompi_transaction_by_id(transaction_id)
    if tx is None:
        tx = _fetch_wompi_latest_transaction_by_reference(reference)
    if tx is None:
        return {"ok": False, "credited": False, "status": "PENDING", "message": "Pago aun no disponible en Wompi"}

    tx_reference = str(tx.get("reference") or "").strip()
    tx_status = str(tx.get("status") or "").strip().upper()
    tx_id = str(tx.get("id") or transaction_id)
    tx_amount_in_cents = int(tx.get("amount_in_cents") or 0)

    if tx_reference != reference:
        raise HTTPException(status_code=400, detail="La transaccion no coincide con la referencia esperada")

    raw_payload = json.dumps(tx, ensure_ascii=True)
    set_recharge_payment_status(reference, tx_status or "PENDING", tx_id, raw_payload)

    if tx_status != "APPROVED":
        if tx_status in FAILED_PAYMENT_STATUSES:
            try:
                send_payment_failed_notification(
                    user_id=int(intent["user_id"]),
                    reference=reference,
                    amount_cop=int(intent["amount_cop"]),
                    status=tx_status,
                    transaction_id=tx_id,
                )
            except Exception:
                pass
        return {
            "ok": True,
            "credited": False,
            "status": tx_status or "PENDING",
            "message": "La transaccion aun no esta aprobada",
        }

    expected_in_cents = int(intent["amount_in_cents"])
    if tx_amount_in_cents < expected_in_cents:
        raise HTTPException(status_code=400, detail="Monto aprobado menor al plan solicitado")

    settled = settle_recharge_if_approved(reference=reference, transaction_id=tx_id, gateway_payload=raw_payload)
    if not bool(settled.get("already_applied")):
        try:
            send_payment_success_notification(
                user_id=int(intent["user_id"]),
                reference=reference,
                amount_cop=int(intent["amount_cop"]),
                balance_cop=int(settled.get("balance_cop") or 0),
                transaction_id=tx_id,
            )
        except Exception:
            pass
    return {
        "ok": True,
        "credited": True,
        "already_applied": bool(settled.get("already_applied")),
        "balance_cop": int(settled.get("balance_cop") or 0),
        "status": "APPROVED",
    }


@router.post("/wompi/sync", response_model=dict)
def sync_wompi_pending_payments(user: AuthenticatedUser = Depends(require_authenticated_user)):
    pending_intents = list_pending_recharge_payment_intents(user.user_id, limit=40)
    credited_count = 0
    reviewed = 0
    details: list[dict] = []

    for intent in pending_intents:
        reference = str(intent.get("reference") or "").strip()
        if not reference:
            continue
        reviewed += 1

        try:
            tx = _fetch_wompi_latest_transaction_by_reference(reference)
        except HTTPException as exc:
            details.append({"reference": reference, "status": "ERROR", "message": str(exc.detail)})
            continue

        if tx is None:
            details.append({"reference": reference, "status": "PENDING"})
            continue

        tx_reference = str(tx.get("reference") or "").strip()
        tx_status = str(tx.get("status") or "").strip().upper() or "PENDING"
        tx_id = str(tx.get("id") or "")
        tx_amount_in_cents = int(tx.get("amount_in_cents") or 0)

        if tx_reference != reference:
            details.append({"reference": reference, "status": "MISMATCH"})
            continue

        raw_payload = json.dumps(tx, ensure_ascii=True)
        set_recharge_payment_status(reference, tx_status, tx_id, raw_payload)

        if tx_status != "APPROVED":
            if tx_status in FAILED_PAYMENT_STATUSES:
                try:
                    send_payment_failed_notification(
                        user_id=int(intent["user_id"]),
                        reference=reference,
                        amount_cop=int(intent["amount_cop"]),
                        status=tx_status,
                        transaction_id=tx_id,
                    )
                except Exception:
                    pass
            details.append({"reference": reference, "status": tx_status})
            continue

        expected_in_cents = int(intent.get("amount_in_cents") or 0)
        if tx_amount_in_cents < expected_in_cents:
            details.append({"reference": reference, "status": "APPROVED_SHORT"})
            continue

        settled = settle_recharge_if_approved(reference=reference, transaction_id=tx_id, gateway_payload=raw_payload)
        if not bool(settled.get("already_applied")):
            credited_count += 1
            try:
                send_payment_success_notification(
                    user_id=int(intent["user_id"]),
                    reference=reference,
                    amount_cop=int(intent["amount_cop"]),
                    balance_cop=int(settled.get("balance_cop") or 0),
                    transaction_id=tx_id,
                )
            except Exception:
                pass
        details.append({
            "reference": reference,
            "status": "APPROVED",
            "already_applied": bool(settled.get("already_applied")),
        })

    return {
        "ok": True,
        "reviewed": reviewed,
        "credited_count": credited_count,
        "balance_cop": int(get_user_balance(user.user_id)),
        "details": details,
    }


@router.post("/wompi/webhook", response_model=dict, include_in_schema=False)
async def wompi_events_webhook(
    request: Request,
    x_event_checksum: str | None = Header(default=None, alias="X-Event-Checksum"),
):
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Payload JSON invalido: {exc}") from exc

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Payload JSON invalido")

    if not _verify_wompi_event_checksum(payload, x_event_checksum):
        raise HTTPException(status_code=401, detail="Checksum de evento Wompi invalido")

    event_name = str(payload.get("event") or "").strip().lower()
    if event_name != "transaction.updated":
        return {"ok": True, "ignored": True, "event": event_name or "unknown"}

    data = payload.get("data")
    tx = data.get("transaction") if isinstance(data, dict) else None
    if not isinstance(tx, dict):
        return {"ok": True, "ignored": True, "reason": "Sin transaction en data"}

    reference = str(tx.get("reference") or "").strip()
    if not reference:
        return {"ok": True, "ignored": True, "reason": "Sin referencia"}

    intent = get_recharge_payment_intent(reference)
    if intent is None:
        return {"ok": True, "ignored": True, "reference": reference, "reason": "Referencia no corresponde a recarga local"}

    tx_status = str(tx.get("status") or "").strip().upper() or "PENDING"
    tx_id = str(tx.get("id") or "")
    tx_amount_in_cents = int(tx.get("amount_in_cents") or 0)
    raw_payload = json.dumps(tx, ensure_ascii=True)

    set_recharge_payment_status(reference, tx_status, tx_id, raw_payload)

    if tx_status != "APPROVED":
        if tx_status in FAILED_PAYMENT_STATUSES:
            try:
                send_payment_failed_notification(
                    user_id=int(intent["user_id"]),
                    reference=reference,
                    amount_cop=int(intent["amount_cop"]),
                    status=tx_status,
                    transaction_id=tx_id,
                )
            except Exception:
                pass
        return {"ok": True, "credited": False, "status": tx_status, "reference": reference}

    expected_in_cents = int(intent.get("amount_in_cents") or 0)
    if tx_amount_in_cents < expected_in_cents:
        return {"ok": True, "credited": False, "status": "APPROVED_SHORT", "reference": reference}

    settled = settle_recharge_if_approved(reference=reference, transaction_id=tx_id, gateway_payload=raw_payload)
    if not bool(settled.get("already_applied")):
        try:
            send_payment_success_notification(
                user_id=int(intent["user_id"]),
                reference=reference,
                amount_cop=int(intent["amount_cop"]),
                balance_cop=int(settled.get("balance_cop") or 0),
                transaction_id=tx_id,
            )
        except Exception:
            pass
    return {
        "ok": True,
        "credited": True,
        "reference": reference,
        "already_applied": bool(settled.get("already_applied")),
        "balance_cop": int(settled.get("balance_cop") or 0),
    }