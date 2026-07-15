from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from ..config import settings
from ..services.animator import animator
from ..services.storage import create_anim, get_anim, get_job, update_anim
from ..services.auth_wallet import AuthenticatedUser, InsufficientBalanceError, credit_balance, debit_balance, require_authenticated_user
from ..services.billing import module_cost_i2v_cop

router = APIRouter(prefix="/animate", tags=["animate"])

VIDEO_DIR = Path(settings.data_dir) / "videos"
DEFAULT_I2V_MODEL = "kwaivgi/kling-v3-video"
SUPPORTED_I2V_MODELS = {
    "kwaivgi/kling-v3-video",
    "wan-video/wan-2.2-i2v-fast",
    "wan-video/wan-2.5-i2v-fast",
    "minimax/video-01-live",
}


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("", response_model=dict)
async def start_animation(
    background_tasks: BackgroundTasks,
    file: UploadFile | None = File(default=None),
    job_id: str | None = Form(default=None),
    prompt: str = Form(
        default="Camera slowly pans across the facade, gentle breeze in vegetation, cinematic sunset lighting"
    ),
    model: str = Form(default="kwaivgi/kling-v3-video"),
    duration_seconds: int = Form(default=5),
    user: AuthenticatedUser = Depends(require_authenticated_user),
):
    image_path: str | None = None

    if file is not None:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

        ext = Path(file.filename or "anim_input.png").suffix.lower() or ".png"
        if ext == ".jpeg":
            ext = ".jpg"
        if ext not in {".png", ".jpg", ".webp"}:
            ext = ".png"

        source_path = Path(settings.input_dir) / f"anim-{uuid4()}{ext}"
        source_path.parent.mkdir(parents=True, exist_ok=True)
        content = await file.read()
        source_path.write_bytes(content)
        image_path = str(source_path)
    else:
        if not job_id:
            raise HTTPException(status_code=400, detail="Debes enviar job_id o una imagen")

        job = get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job de render no encontrado")
        if job.get("status") != "completed":
            raise HTTPException(status_code=409, detail="El render aun no esta completado")

        output_image_path = job.get("output_image")
        if not output_image_path or not Path(output_image_path).exists():
            raise HTTPException(status_code=404, detail="Imagen de salida no disponible en disco")

        image_path = output_image_path

    requested_model = (model or "").strip()
    selected_model = requested_model if requested_model in SUPPORTED_I2V_MODELS else DEFAULT_I2V_MODEL

    anim_id = str(uuid4())
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    output_video_path = VIDEO_DIR / f"{anim_id}.mp4"

    requested_duration = max(3, min(15, int(duration_seconds)))
    billed_amount = module_cost_i2v_cop(selected_model, requested_duration)
    try:
        balance_after = debit_balance(user.user_id, billed_amount, "img2vid", f"Animacion {anim_id}")
    except InsufficientBalanceError as exc:
        raise HTTPException(status_code=402, detail="Saldo insuficiente. Recarga tu cuenta para generar video.") from exc

    create_anim(
        anim_id,
        {
            "anim_id": anim_id,
            "job_id": job_id,
            "status": "queued",
            "prompt": prompt,
            "model": selected_model,
            "duration_seconds": requested_duration,
            "source_image": image_path,
            "video_output": None,
            "error": None,
            "stage": "En cola",
            "progress": 0,
            "started_at": None,
            "completed_at": None,
            "updated_at": _utc(),
            "billed_user_id": user.user_id,
            "billed_amount_cop": billed_amount,
            "balance_after_debit": balance_after,
        },
    )

    def run_animation() -> None:
        try:
            update_anim(
                anim_id,
                {
                    "status": "processing",
                    "stage": "Generando video",
                    "progress": 15,
                    "started_at": _utc(),
                    "updated_at": _utc(),
                },
            )

            result = animator.animate_replicate(
                image_path=image_path,
                output_video_path=str(output_video_path),
                prompt=prompt,
                model=selected_model,
                duration_seconds=requested_duration,
            )

            duration = result.get("duration_seconds", 1)
            update_anim(
                anim_id,
                {
                    "status": "completed",
                    "video_output": str(output_video_path),
                    "progress": 100,
                    "stage": f"Video listo ({duration}s, clip {requested_duration}s)",
                    "completed_at": _utc(),
                    "updated_at": _utc(),
                },
            )
        except Exception as exc:
            try:
                credit_balance(user.user_id, billed_amount, "img2vid_refund", f"Reembolso por fallo anim {anim_id}")
            except Exception:
                pass
            update_anim(
                anim_id,
                {
                    "status": "failed",
                    "error": str(exc),
                    "stage": "Fallo en animacion",
                    "updated_at": _utc(),
                },
            )

    background_tasks.add_task(run_animation)
    return {"anim_id": anim_id, "status": "queued"}


@router.get("/{anim_id}", response_model=dict)
def get_animation_status(anim_id: str):
    anim = get_anim(anim_id)
    if anim is None:
        raise HTTPException(status_code=404, detail="Animacion no encontrada")
    return anim


@router.get("/{anim_id}/video")
def get_animation_video(anim_id: str):
    anim = get_anim(anim_id)
    if anim is None:
        raise HTTPException(status_code=404, detail="Animacion no encontrada")
    if anim.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Video aun no disponible")

    video_path = anim.get("video_output")
    if not video_path or not Path(video_path).exists():
        raise HTTPException(status_code=404, detail="Archivo de video no encontrado en disco")

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=f"IA-IMP-anim-{anim_id[:8]}.mp4",
    )
