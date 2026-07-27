from datetime import datetime, timezone
import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse

from ..config import settings
from ..services.admission_control import enforce_generation_capacity, release_generation_slot, reserve_generation_slot
from ..schemas import JobDetail
from ..services.auth_wallet import AuthenticatedUser, InsufficientBalanceError, credit_balance, debit_balance, require_authenticated_user
from ..services.billing import module_cost_img2img_cop, module_cost_materials_cop, module_cost_text2img_cop
from ..services.queue import QueueUnavailableError, enqueue_or_background
from ..services.storage import create_job, get_job, get_next_sequence, get_record_download_target, resolve_download_url, update_job
from ..services.worker_tasks import run_material_render_job, run_render_job, run_text_render_job

router = APIRouter(prefix="/jobs", tags=["jobs"])

VALID_LIGHTING_MODES = {"morning", "afternoon", "night"}


def normalize_lighting_mode(value: str | None) -> str:
    candidate = (value or "afternoon").strip().lower()
    return candidate if candidate in VALID_LIGHTING_MODES else "afternoon"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_job_sequence(job_id: str, job: dict) -> int:
    try:
        sequence = int(job.get("sequence", 0))
    except (TypeError, ValueError):
        sequence = 0

    if sequence > 0:
        return sequence

    sequence = get_next_sequence()
    job["sequence"] = sequence
    update_job(job_id, {"sequence": sequence, "updated_at": utc_now_iso()})
    return sequence


def _resolve_material_paths(material_names: list[str]) -> list[str]:
    root = Path(__file__).resolve().parents[3] / "Materiales"
    if not root.exists() or not root.is_dir():
        raise HTTPException(status_code=404, detail="Carpeta Materiales no encontrada")

    resolved: list[str] = []
    root_resolved = root.resolve()

    for raw_name in material_names:
        candidate = (root / raw_name).resolve()
        try:
            candidate.relative_to(root_resolved)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"Material invalido: {raw_name}") from exc

        if not candidate.exists() or not candidate.is_file():
            raise HTTPException(status_code=404, detail=f"Material no encontrado: {raw_name}")

        resolved.append(str(candidate))

    return resolved


def _normalize_material_names(raw_names: list[str]) -> list[str]:
    normalized: list[str] = []
    for raw in raw_names:
        candidate = str(raw or "").replace("\r", "\n")
        chunks = [part.strip() for part in candidate.replace(",", "\n").split("\n")]
        for chunk in chunks:
            if chunk:
                normalized.append(chunk)
    return normalized


@router.post("/render", response_model=dict)
async def create_render_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    prompt: str = Form(...),
    negative_prompt: str = Form("low quality, blurry, distorted geometry, cartoon"),
    style: str = Form("editorial"),
    lighting_mode: str = Form("afternoon"),
    quality: str = Form("balanced"),
    steps: int = Form(35),
    guidance_scale: float = Form(7.5),
    seed: int | None = Form(None),
    user: AuthenticatedUser = Depends(require_authenticated_user),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen.")

    enforce_generation_capacity("render", user.user_id)
    reserve_generation_slot("render", user.user_id)

    try:
        safe_lighting_mode = normalize_lighting_mode(lighting_mode)

        job_id = str(uuid4())
        sequence = get_next_sequence()
        ext = Path(file.filename or "input.png").suffix or ".png"
        normalized_ext = ext.lower()
        if normalized_ext == ".jpeg":
            normalized_ext = ".jpg"
        if normalized_ext not in {".png", ".jpg", ".webp"}:
            normalized_ext = ".png"

        input_path = Path(settings.input_dir) / f"{job_id}{ext}"
        output_path = Path(settings.output_dir) / f"{job_id}{normalized_ext}"

        input_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        content = await file.read()
        input_path.write_bytes(content)

        billed_amount = module_cost_img2img_cop()
        try:
            balance_after = debit_balance(user.user_id, billed_amount, "img2img", f"Generacion job {job_id}")
        except InsufficientBalanceError as exc:
            raise HTTPException(status_code=402, detail="Saldo insuficiente. Recarga tu cuenta para generar.") from exc

        create_job(
            job_id,
            {
                "job_id": job_id,
                "sequence": sequence,
                "status": "queued",
                "prompt": prompt,
                "style": style,
                "lighting_mode": safe_lighting_mode,
                "quality": quality,
                "input_image": str(input_path),
                "output_image": None,
                "error": None,
                "progress": 0,
                "stage": "En cola",
                "eta_seconds": 10,
                "elapsed_seconds": 0,
                "expected_total_seconds": 10,
                "model_mode": None,
                "started_at": None,
                "completed_at": None,
                "updated_at": utc_now_iso(),
                "billed_user_id": user.user_id,
                "billed_amount_cop": billed_amount,
                "balance_after_debit": balance_after,
            },
        )

        try:
            queue_task_id = enqueue_or_background(
                background_tasks,
                run_render_job,
                queue_name="render",
                job_id=job_id,
                user_id=user.user_id,
                billed_amount=billed_amount,
                input_image_path=str(input_path),
                output_image_path=str(output_path),
                prompt=prompt,
                negative_prompt=negative_prompt,
                style=style,
                lighting_mode=safe_lighting_mode,
                quality=quality,
                steps=steps,
                guidance_scale=guidance_scale,
                seed=seed,
            )
        except QueueUnavailableError as exc:
            try:
                credit_balance(user.user_id, billed_amount, "img2img_refund", f"Reembolso por cola no disponible {job_id}")
            except Exception:
                pass
            update_job(
                job_id,
                {
                    "status": "failed",
                    "error": str(exc),
                    "stage": "Cola no disponible",
                    "updated_at": utc_now_iso(),
                },
            )
            raise HTTPException(status_code=503, detail="Cola temporalmente no disponible. Intenta nuevamente en unos minutos.") from exc

        return {
            "job_id": job_id,
            "sequence": sequence,
            "status": "queued",
            "message": "Render en cola",
            "queue_task_id": queue_task_id,
        }
    except Exception:
        release_generation_slot("render", user.user_id)
        raise


@router.post("/render-text", response_model=dict)
async def create_text_render_job(
    background_tasks: BackgroundTasks,
    prompt: str = Form(...),
    negative_prompt: str = Form("low quality, blurry, distorted geometry, cartoon"),
    style: str = Form("editorial"),
    lighting_mode: str = Form("afternoon"),
    quality: str = Form("balanced"),
    steps: int = Form(35),
    guidance_scale: float = Form(7.5),
    seed: int | None = Form(None),
    user: AuthenticatedUser = Depends(require_authenticated_user),
):
    if not prompt.strip():
        raise HTTPException(status_code=400, detail="El prompt es obligatorio")

    enforce_generation_capacity("render", user.user_id)
    reserve_generation_slot("render", user.user_id)

    try:
        safe_lighting_mode = normalize_lighting_mode(lighting_mode)

        job_id = str(uuid4())
        sequence = get_next_sequence()
        output_path = Path(settings.output_dir) / f"{job_id}.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        billed_amount = module_cost_text2img_cop()
        try:
            balance_after = debit_balance(user.user_id, billed_amount, "text2img", f"Generacion texto job {job_id}")
        except InsufficientBalanceError as exc:
            raise HTTPException(status_code=402, detail="Saldo insuficiente. Recarga tu cuenta para generar.") from exc

        create_job(
            job_id,
            {
                "job_id": job_id,
                "sequence": sequence,
                "status": "queued",
                "prompt": prompt,
                "style": style,
                "lighting_mode": safe_lighting_mode,
                "quality": quality,
                "input_image": "",
                "output_image": None,
                "error": None,
                "progress": 0,
                "stage": "En cola",
                "eta_seconds": 10,
                "elapsed_seconds": 0,
                "expected_total_seconds": 10,
                "model_mode": None,
                "started_at": None,
                "completed_at": None,
                "updated_at": utc_now_iso(),
                "billed_user_id": user.user_id,
                "billed_amount_cop": billed_amount,
                "balance_after_debit": balance_after,
            },
        )

        try:
            queue_task_id = enqueue_or_background(
                background_tasks,
                run_text_render_job,
                queue_name="render",
                job_id=job_id,
                user_id=user.user_id,
                billed_amount=billed_amount,
                output_image_path=str(output_path),
                prompt=prompt,
                negative_prompt=negative_prompt,
                style=style,
                lighting_mode=safe_lighting_mode,
                quality=quality,
                steps=steps,
                guidance_scale=guidance_scale,
                seed=seed,
            )
        except QueueUnavailableError as exc:
            try:
                credit_balance(user.user_id, billed_amount, "text2img_refund", f"Reembolso por cola no disponible {job_id}")
            except Exception:
                pass
            update_job(
                job_id,
                {
                    "status": "failed",
                    "error": str(exc),
                    "stage": "Cola no disponible",
                    "updated_at": utc_now_iso(),
                },
            )
            raise HTTPException(status_code=503, detail="Cola temporalmente no disponible. Intenta nuevamente en unos minutos.") from exc

        return {
            "job_id": job_id,
            "sequence": sequence,
            "status": "queued",
            "message": "Generacion texto a imagen en cola",
            "queue_task_id": queue_task_id,
        }
    except Exception:
        release_generation_slot("render", user.user_id)
        raise


@router.post("/render-materials", response_model=dict)
async def create_material_render_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    prompt: str = Form(...),
    material_mode: str = Form("mix"),
    material_plan: str = Form(""),
    material_names: list[str] = Form(default=[]),
    style: str = Form("editorial"),
    lighting_mode: str = Form("afternoon"),
    quality: str = Form("balanced"),
    seed: int | None = Form(None),
    user: AuthenticatedUser = Depends(require_authenticated_user),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen.")

    if not prompt.strip():
        raise HTTPException(status_code=400, detail="El prompt es obligatorio")

    enforce_generation_capacity("render", user.user_id)
    reserve_generation_slot("render", user.user_id)

    try:
        normalized_material_names = _normalize_material_names(material_names)

        if len(normalized_material_names) < 1 or len(normalized_material_names) > 2:
            raise HTTPException(status_code=400, detail="Selecciona entre 1 y 2 materiales")

        safe_mode = (material_mode or "mix").strip().lower()
        if safe_mode not in {"mix", "zones"}:
            raise HTTPException(status_code=400, detail="material_mode debe ser 'mix' o 'zones'")

        safe_lighting_mode = normalize_lighting_mode(lighting_mode)
        resolved_material_paths = _resolve_material_paths(normalized_material_names)

        job_id = str(uuid4())
        sequence = get_next_sequence()
        ext = Path(file.filename or "input.png").suffix or ".png"
        normalized_ext = ext.lower()
        if normalized_ext == ".jpeg":
            normalized_ext = ".jpg"
        if normalized_ext not in {".png", ".jpg", ".webp"}:
            normalized_ext = ".png"

        input_path = Path(settings.input_dir) / f"{job_id}{ext}"
        output_path = Path(settings.output_dir) / f"{job_id}{normalized_ext}"

        input_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        content = await file.read()
        input_path.write_bytes(content)

        billed_amount = module_cost_materials_cop()
        try:
            balance_after = debit_balance(user.user_id, billed_amount, "materials", f"Generacion materiales job {job_id}")
        except InsufficientBalanceError as exc:
            raise HTTPException(status_code=402, detail="Saldo insuficiente. Recarga tu cuenta para generar.") from exc

        create_job(
            job_id,
            {
                "job_id": job_id,
                "sequence": sequence,
                "status": "queued",
                "prompt": prompt,
                "style": style,
                "lighting_mode": safe_lighting_mode,
                "quality": quality,
                "input_image": str(input_path),
                "output_image": None,
                "material_names": normalized_material_names,
                "material_mode": safe_mode,
                "material_plan": material_plan,
                "error": None,
                "progress": 0,
                "stage": "En cola",
                "eta_seconds": 10,
                "elapsed_seconds": 0,
                "expected_total_seconds": 10,
                "model_mode": None,
                "started_at": None,
                "completed_at": None,
                "updated_at": utc_now_iso(),
                "billed_user_id": user.user_id,
                "billed_amount_cop": billed_amount,
                "balance_after_debit": balance_after,
            },
        )

        try:
            queue_task_id = enqueue_or_background(
                background_tasks,
                run_material_render_job,
                queue_name="render",
                job_id=job_id,
                user_id=user.user_id,
                billed_amount=billed_amount,
                input_image_path=str(input_path),
                output_image_path=str(output_path),
                prompt=prompt,
                style=style,
                lighting_mode=safe_lighting_mode,
                quality=quality,
                material_mode=safe_mode,
                material_plan=material_plan,
                material_names=normalized_material_names,
                material_paths=resolved_material_paths,
                seed=seed,
            )
        except QueueUnavailableError as exc:
            try:
                credit_balance(user.user_id, billed_amount, "materials_refund", f"Reembolso por cola no disponible {job_id}")
            except Exception:
                pass
            update_job(
                job_id,
                {
                    "status": "failed",
                    "error": str(exc),
                    "stage": "Cola no disponible",
                    "updated_at": utc_now_iso(),
                },
            )
            raise HTTPException(status_code=503, detail="Cola temporalmente no disponible. Intenta nuevamente en unos minutos.") from exc

        return {
            "job_id": job_id,
            "sequence": sequence,
            "status": "queued",
            "message": "Render con materiales en cola",
            "queue_task_id": queue_task_id,
        }
    except Exception:
        release_generation_slot("render", user.user_id)
        raise


@router.get("/{job_id}", response_model=JobDetail)
def get_render_job(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job no encontrado")

    ensure_job_sequence(job_id, job)
    return job


@router.get("/{job_id}/image")
def get_render_image(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job no encontrado")

    image_path = job.get("output_image")
    if not image_path and not job.get("output_storage_key") and not job.get("output_storage_url"):
        raise HTTPException(status_code=409, detail="Render aun no finaliza")

    path = Path(image_path) if image_path else None
    if not path or not path.exists():
        target = get_record_download_target(job, "job", job_id)
        remote_url = resolve_download_url(target.get("storage_key") or "", target.get("storage_url") or "")
        if remote_url:
            return RedirectResponse(url=remote_url, status_code=307)
        raise HTTPException(status_code=404, detail="Imagen no disponible")

    sequence = ensure_job_sequence(job_id, job)

    media_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    download_ext = path.suffix or ".png"

    return FileResponse(path=str(path), media_type=media_type, filename=f"IA-IMP-{sequence}{download_ext}")
