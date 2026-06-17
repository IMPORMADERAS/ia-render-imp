from datetime import datetime, timezone
from pathlib import Path
import re
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from ..config import settings
from ..services.animator import animator
from ..services.storage import create_anim, get_anim, update_anim
from ..services.auth_wallet import AuthenticatedUser, InsufficientBalanceError, credit_balance, debit_balance, require_authenticated_user
from ..services.billing import module_cost_influencer_cop

router = APIRouter(prefix="/influencer", tags=["influencer"])

VIDEO_DIR = Path(settings.data_dir) / "influencer_videos"
REALISTIC_INFLUENCER_RESOLUTION = "1080p"
REALISTIC_INFLUENCER_FPS = "24"


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "si", "on"}


def _looks_like_real_person_request(text: str) -> bool:
    normalized = text.strip().lower()
    if not normalized:
        return False
    pattern = r"\b(famos[oa]s?|celebridad|actor|actriz|cantante|deportista|politic[oa]|persona real|de la farandula)\b"
    return re.search(pattern, normalized) is not None


def _build_realistic_influencer_instruction(user_instruction: str) -> str:
    base = (
        "Photorealistic talking-head video, natural skin texture, true-to-life facial proportions, "
        "accurate lip-sync, subtle micro-expressions, stable gaze, clean face tracking, "
        "cinematic lighting, realistic shadow roll-off, natural color grading, no cartoon look, "
        "no plastic skin, no warped facial geometry."
    )
    extra = (user_instruction or "").strip()
    if not extra:
        return base
    return f"{base} Direction: {extra}"


@router.post("/create", response_model=dict)
async def create_influencer_video(
    background_tasks: BackgroundTasks,
    reference_image: UploadFile = File(...),
    source_video: UploadFile = File(...),
    instruction_prompt: str = Form(""),
    character_mode: str = Form("original"),
    resolution: str = Form("720p"),
    target_fps: str = Form("original"),
    turbo: str = Form("false"),
    consent_confirmed: str = Form("false"),
    user: AuthenticatedUser = Depends(require_authenticated_user),
):
    if not reference_image.content_type or not reference_image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="La referencia debe ser una imagen")

    if not source_video.content_type or not source_video.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="El archivo de conduccion debe ser un video")

    if not _as_bool(consent_confirmed):
        raise HTTPException(
            status_code=400,
            detail="Debes confirmar que tienes derechos/consentimiento y que no suplantas a terceros",
        )

    if (character_mode or "").strip().lower() != "original":
        raise HTTPException(status_code=400, detail="Solo se permiten personajes creados/originales")

    if _looks_like_real_person_request(instruction_prompt):
        raise HTTPException(
            status_code=400,
            detail="No se permite generar influencers basados en famosos o personas reales",
        )

    realistic_instruction_prompt = _build_realistic_influencer_instruction(instruction_prompt)
    safe_resolution = REALISTIC_INFLUENCER_RESOLUTION
    safe_target_fps = REALISTIC_INFLUENCER_FPS

    image_ext = Path(reference_image.filename or "reference.png").suffix.lower() or ".png"
    if image_ext == ".jpeg":
        image_ext = ".jpg"
    if image_ext not in {".png", ".jpg", ".webp"}:
        image_ext = ".png"

    video_ext = Path(source_video.filename or "source.mp4").suffix.lower() or ".mp4"
    if video_ext not in {".mp4", ".mov", ".webm"}:
        video_ext = ".mp4"

    influencer_id = str(uuid4())

    billed_amount = module_cost_influencer_cop()
    try:
        balance_after = debit_balance(user.user_id, billed_amount, "influencer", f"Generacion influencer {influencer_id}")
    except InsufficientBalanceError as exc:
        raise HTTPException(status_code=402, detail="Saldo insuficiente. Recarga tu cuenta para generar influencer.") from exc

    image_path = Path(settings.input_dir) / f"influencer-ref-{influencer_id}{image_ext}"
    video_path = Path(settings.input_dir) / f"influencer-src-{influencer_id}{video_ext}"

    image_path.parent.mkdir(parents=True, exist_ok=True)
    video_path.parent.mkdir(parents=True, exist_ok=True)

    image_path.write_bytes(await reference_image.read())
    video_path.write_bytes(await source_video.read())

    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    output_video_path = VIDEO_DIR / f"{influencer_id}.mp4"

    create_anim(
        influencer_id,
        {
            "anim_id": influencer_id,
            "kind": "influencer",
            "status": "queued",
            "stage": "En cola",
            "progress": 0,
            "source_image": str(image_path),
            "source_video": str(video_path),
            "video_output": None,
            "error": None,
            "resolution": safe_resolution,
            "target_fps": safe_target_fps,
            "requested_resolution": resolution,
            "requested_target_fps": target_fps,
            "realism_mode": "strict",
            "started_at": None,
            "completed_at": None,
            "updated_at": _utc(),
            "billed_user_id": user.user_id,
            "billed_amount_cop": billed_amount,
            "balance_after_debit": balance_after,
        },
    )

    def run_influencer() -> None:
        try:
            update_anim(
                influencer_id,
                {
                    "status": "processing",
                    "stage": "Procesando expresion y lip-sync (realismo estricto)",
                    "progress": 15,
                    "started_at": _utc(),
                    "updated_at": _utc(),
                },
            )

            result = animator.animate_influencer_replicate(
                source_video_path=str(video_path),
                reference_image_path=str(image_path),
                output_video_path=str(output_video_path),
                instruction_prompt=realistic_instruction_prompt,
                resolution=safe_resolution,
                target_fps=safe_target_fps,
                turbo=_as_bool(turbo),
            )

            update_anim(
                influencer_id,
                {
                    "status": "completed",
                    "stage": "Video influencer listo (realismo estricto)",
                    "progress": 100,
                    "video_output": str(output_video_path),
                    "model": result.get("model", settings.replicate_influencer_model),
                    "duration_seconds": result.get("duration_seconds", 1),
                    "completed_at": _utc(),
                    "updated_at": _utc(),
                },
            )
        except Exception as exc:
            try:
                credit_balance(user.user_id, billed_amount, "influencer_refund", f"Reembolso por fallo influencer {influencer_id}")
            except Exception:
                pass
            update_anim(
                influencer_id,
                {
                    "status": "failed",
                    "stage": "Fallo en influencer",
                    "progress": 0,
                    "error": str(exc),
                    "updated_at": _utc(),
                },
            )

    background_tasks.add_task(run_influencer)
    return {"influencer_id": influencer_id, "status": "queued"}


@router.get("/{influencer_id}", response_model=dict)
def get_influencer_status(influencer_id: str):
    item = get_anim(influencer_id)
    if item is None or item.get("kind") != "influencer":
        raise HTTPException(status_code=404, detail="Influencer no encontrado")
    return item


@router.get("/{influencer_id}/video")
def get_influencer_video(influencer_id: str):
    item = get_anim(influencer_id)
    if item is None or item.get("kind") != "influencer":
        raise HTTPException(status_code=404, detail="Influencer no encontrado")

    if item.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Video aun no disponible")

    video_path = item.get("video_output")
    if not video_path or not Path(video_path).exists():
        raise HTTPException(status_code=404, detail="Archivo de video no encontrado")

    return FileResponse(path=video_path, media_type="video/mp4", filename=f"IA-IMP-influencer-{influencer_id[:8]}.mp4")
