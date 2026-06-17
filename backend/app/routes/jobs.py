from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4
import mimetypes

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from ..config import settings
from ..schemas import JobDetail
from ..services.prompt_builder import build_arch_prompt, sanitize_negative_prompt
from ..services.renderer import renderer
from ..services.storage import create_job, get_job, get_next_sequence, update_job
from ..services.auth_wallet import AuthenticatedUser, InsufficientBalanceError, credit_balance, debit_balance, require_authenticated_user
from ..services.billing import module_cost_img2img_cop, module_cost_materials_cop, module_cost_text2img_cop

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

    def run_render() -> None:
        try:
            provider = settings.render_provider.lower().strip()
            base_eta = max(20, int(steps * 1.4))
            if provider == "replicate":
                base_eta = max(45, int(steps * 2.0))

            started_at = utc_now_iso()
            update_job(
                job_id,
                {
                    "status": "processing",
                    "progress": 15,
                    "stage": "Preparando render",
                    "eta_seconds": base_eta,
                    "expected_total_seconds": base_eta,
                    "started_at": started_at,
                    "updated_at": utc_now_iso(),
                },
            )

            full_prompt = build_arch_prompt(prompt, style, safe_lighting_mode)
            cleaned_negative_prompt = sanitize_negative_prompt(negative_prompt)
            update_job(
                job_id,
                {
                    "progress": 55,
                    "stage": f"Renderizando en {provider} ({quality})",
                    "updated_at": utc_now_iso(),
                },
            )

            render_meta = renderer.generate(
                input_image_path=str(input_path),
                output_image_path=str(output_path),
                prompt=full_prompt,
                negative_prompt=cleaned_negative_prompt,
                steps=steps,
                guidance_scale=guidance_scale,
                quality=quality,
                seed=seed,
            )

            duration = int(render_meta.get("duration_seconds", 1))
            mode = str(render_meta.get("mode", "fallback"))
            warning = render_meta.get("warning")
            stage = "Completado"
            if warning:
                stage = "Completado con fallback local"

            update_job(
                job_id,
                {
                    "status": "completed",
                    "output_image": str(output_path),
                    "progress": 100,
                    "stage": stage,
                    "eta_seconds": 0,
                    "elapsed_seconds": duration,
                    "expected_total_seconds": duration,
                    "model_mode": mode,
                    "warning": warning,
                    "completed_at": utc_now_iso(),
                    "updated_at": utc_now_iso(),
                },
            )
        except Exception as exc:
            try:
                credit_balance(user.user_id, billed_amount, "img2img_refund", f"Reembolso por fallo job {job_id}")
            except Exception:
                pass
            update_job(
                job_id,
                {
                    "status": "failed",
                    "error": str(exc),
                    "stage": "Fallo en render",
                    "eta_seconds": None,
                    "updated_at": utc_now_iso(),
                },
            )

    background_tasks.add_task(run_render)

    return {"job_id": job_id, "sequence": sequence, "status": "queued", "message": "Render en cola"}


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

    def run_render_text() -> None:
        try:
            started_at = utc_now_iso()
            base_eta = max(35, int(steps * 1.8))
            update_job(
                job_id,
                {
                    "status": "processing",
                    "progress": 15,
                    "stage": "Preparando texto a imagen",
                    "eta_seconds": base_eta,
                    "expected_total_seconds": base_eta,
                    "started_at": started_at,
                    "updated_at": utc_now_iso(),
                },
            )

            full_prompt = build_arch_prompt(prompt, style, safe_lighting_mode)
            cleaned_negative_prompt = sanitize_negative_prompt(negative_prompt)
            update_job(
                job_id,
                {
                    "progress": 55,
                    "stage": f"Generando imagen desde texto ({quality})",
                    "updated_at": utc_now_iso(),
                },
            )

            render_meta = renderer.generate_text_to_image(
                output_image_path=str(output_path),
                prompt=full_prompt,
                negative_prompt=cleaned_negative_prompt,
                steps=steps,
                guidance_scale=guidance_scale,
                quality=quality,
                seed=seed,
            )

            duration = int(render_meta.get("duration_seconds", 1))
            mode = str(render_meta.get("mode", "replicate_text"))

            update_job(
                job_id,
                {
                    "status": "completed",
                    "output_image": str(output_path),
                    "progress": 100,
                    "stage": "Completado",
                    "eta_seconds": 0,
                    "elapsed_seconds": duration,
                    "expected_total_seconds": duration,
                    "model_mode": mode,
                    "warning": None,
                    "completed_at": utc_now_iso(),
                    "updated_at": utc_now_iso(),
                },
            )
        except Exception as exc:
            try:
                credit_balance(user.user_id, billed_amount, "text2img_refund", f"Reembolso por fallo job {job_id}")
            except Exception:
                pass
            update_job(
                job_id,
                {
                    "status": "failed",
                    "error": str(exc),
                    "stage": "Fallo en texto a imagen",
                    "eta_seconds": None,
                    "updated_at": utc_now_iso(),
                },
            )

    background_tasks.add_task(run_render_text)

    return {
        "job_id": job_id,
        "sequence": sequence,
        "status": "queued",
        "message": "Generacion texto a imagen en cola",
    }


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

    if len(material_names) < 1 or len(material_names) > 2:
        raise HTTPException(status_code=400, detail="Selecciona entre 1 y 2 materiales")

    safe_mode = (material_mode or "mix").strip().lower()
    if safe_mode not in {"mix", "zones"}:
        raise HTTPException(status_code=400, detail="material_mode debe ser 'mix' o 'zones'")

    safe_lighting_mode = normalize_lighting_mode(lighting_mode)

    resolved_material_paths = _resolve_material_paths(material_names)

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
            "material_names": material_names,
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

    def run_material_render() -> None:
        try:
            started_at = utc_now_iso()
            base_eta = 70 if quality == "ultra" else 55
            update_job(
                job_id,
                {
                    "status": "processing",
                    "progress": 15,
                    "stage": "Preparando materiales",
                    "eta_seconds": base_eta,
                    "expected_total_seconds": base_eta,
                    "started_at": started_at,
                    "updated_at": utc_now_iso(),
                },
            )

            full_prompt = build_arch_prompt(prompt, style, safe_lighting_mode)
            if safe_mode == "mix":
                full_prompt = (
                    f"{full_prompt}. Usa los materiales de referencia para una mezcla equilibrada y realista en superficies arquitectonicas. "
                    "No alteres geometria, perspectiva ni composicion del modelado."
                )
            else:
                plan_text = material_plan.strip() or "Distribuye los materiales en zonas coherentes sin alterar la estructura principal"
                full_prompt = (
                    f"{full_prompt}. Aplica materiales por zonas segun esta instruccion: {plan_text}. "
                    "Conserva geometria, escala y encuadre original."
                )

            update_job(
                job_id,
                {
                    "progress": 55,
                    "stage": f"Aplicando {len(material_names)} materiales ({safe_mode})",
                    "updated_at": utc_now_iso(),
                },
            )

            render_meta = renderer.generate_material_edit(
                input_image_path=str(input_path),
                material_paths=resolved_material_paths,
                output_image_path=str(output_path),
                prompt=full_prompt,
                material_mode=safe_mode,
                material_plan=material_plan,
                quality=quality,
                seed=seed,
            )

            duration = int(render_meta.get("duration_seconds", 1))
            update_job(
                job_id,
                {
                    "status": "completed",
                    "output_image": str(output_path),
                    "progress": 100,
                    "stage": "Completado",
                    "eta_seconds": 0,
                    "elapsed_seconds": duration,
                    "expected_total_seconds": duration,
                    "model_mode": str(render_meta.get("mode", "replicate_materials")),
                    "warning": None,
                    "completed_at": utc_now_iso(),
                    "updated_at": utc_now_iso(),
                },
            )
        except Exception as exc:
            try:
                credit_balance(user.user_id, billed_amount, "materials_refund", f"Reembolso por fallo job {job_id}")
            except Exception:
                pass
            update_job(
                job_id,
                {
                    "status": "failed",
                    "error": str(exc),
                    "stage": "Fallo en materiales",
                    "eta_seconds": None,
                    "updated_at": utc_now_iso(),
                },
            )

    background_tasks.add_task(run_material_render)

    return {
        "job_id": job_id,
        "sequence": sequence,
        "status": "queued",
        "message": "Render con materiales en cola",
    }


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
    if not image_path:
        raise HTTPException(status_code=409, detail="Render aun no finaliza")

    path = Path(image_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Imagen no disponible")

    sequence = ensure_job_sequence(job_id, job)

    media_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    download_ext = path.suffix or ".png"

    return FileResponse(path=str(path), media_type=media_type, filename=f"IA-IMP-{sequence}{download_ext}")
