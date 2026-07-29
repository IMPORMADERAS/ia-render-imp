from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ..config import settings
from ..services.admission_control import enforce_generation_capacity, release_generation_slot, reserve_generation_slot
from ..services.auth_wallet import AuthenticatedUser, InsufficientBalanceError, credit_balance, debit_balance, require_authenticated_user
from ..services.billing import intelligent_project_cost_cop
from ..services.queue import QueueUnavailableError, enqueue_or_background
from ..services.storage import create_job, get_job, get_next_sequence, update_job
from ..services.worker_tasks import run_intelligent_project_job

VIDEO_DIR = Path(settings.data_dir) / "videos"
REPORT_DIR = Path(settings.data_dir) / "projects"

router = APIRouter(prefix="/intelligent-project", tags=["intelligent-project"])


class IntelligentProjectRequest(BaseModel):
    prompt: str = Field(..., min_length=8, max_length=900)
    material_names: list[str] = Field(default_factory=list)
    include_video: bool = True
    duration_seconds: int = Field(default=5, ge=3, le=15)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_material_names(raw_names: list[str]) -> list[str]:
    normalized: list[str] = []
    for raw in raw_names:
        candidate = str(raw or "").replace("\r", "\n")
        chunks = [part.strip() for part in candidate.replace(",", "\n").split("\n")]
        for chunk in chunks:
            if chunk:
                normalized.append(chunk)
    return normalized[:2]


def _load_project_job_owned(job_id: str, user_id: int) -> dict:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    if int(job.get("billed_user_id") or 0) != int(user_id):
        raise HTTPException(status_code=403, detail="No tienes permiso para este proyecto")
    if str(job.get("project_module") or "") != "intelligent_project":
        raise HTTPException(status_code=404, detail="Proyecto inteligente no encontrado")
    return job


@router.post("/run", response_model=dict)
def run_intelligent_project(
    payload: IntelligentProjectRequest,
    background_tasks: BackgroundTasks,
    user: AuthenticatedUser = Depends(require_authenticated_user),
):
    enforce_generation_capacity("render", user.user_id)
    reserve_generation_slot("render", user.user_id)

    try:
        project_id = str(uuid4())
        sequence = get_next_sequence()
        billed_amount = intelligent_project_cost_cop()

        image_output = Path(settings.output_dir) / f"{project_id}.png"
        video_output = VIDEO_DIR / f"{project_id}.mp4"
        report_output = REPORT_DIR / f"{project_id}.pdf"

        image_output.parent.mkdir(parents=True, exist_ok=True)
        video_output.parent.mkdir(parents=True, exist_ok=True)
        report_output.parent.mkdir(parents=True, exist_ok=True)

        safe_materials = _normalize_material_names(payload.material_names)
        if not safe_materials:
            raise HTTPException(status_code=400, detail="Selecciona al menos 1 material del catalogo")
        safe_strategy = "selected"

        try:
            balance_after = debit_balance(user.user_id, billed_amount, "intelligent_project", f"Proyecto inteligente {project_id}")
        except InsufficientBalanceError as exc:
            raise HTTPException(status_code=402, detail="Saldo insuficiente. Recarga tu cuenta para continuar.") from exc

        create_job(
            project_id,
            {
                "job_id": project_id,
                "sequence": sequence,
                "status": "queued",
                "prompt": payload.prompt,
                "style": "intelligent_project",
                "input_image": "",
                "output_image": None,
                "output_video": None,
                "report_pdf": None,
                "selected_material_names": [],
                "quantities": [],
                "material_strategy": safe_strategy,
                "material_names_requested": safe_materials,
                "include_video": bool(payload.include_video),
                "duration_seconds": int(payload.duration_seconds),
                "error": None,
                "progress": 0,
                "stage": "En cola",
                "eta_seconds": 25,
                "elapsed_seconds": 0,
                "expected_total_seconds": 25,
                "model_mode": "intelligent_project",
                "started_at": None,
                "completed_at": None,
                "updated_at": _now_iso(),
                "project_module": "intelligent_project",
                "billed_user_id": user.user_id,
                "billed_amount_cop": billed_amount,
                "balance_after_debit": balance_after,
            },
        )

        try:
            queue_task_id = enqueue_or_background(
                background_tasks,
                run_intelligent_project_job,
                queue_name="intelligent_project",
                job_id=project_id,
                user_id=user.user_id,
                billed_amount=billed_amount,
                output_image_path=str(image_output),
                output_video_path=str(video_output),
                report_pdf_path=str(report_output),
                prompt=payload.prompt,
                material_names=safe_materials,
                include_video=bool(payload.include_video),
                duration_seconds=int(payload.duration_seconds),
            )
        except QueueUnavailableError as exc:
            try:
                credit_balance(user.user_id, billed_amount, "intelligent_project_refund", f"Reembolso por cola no disponible {project_id}")
            except Exception:
                pass
            update_job(
                project_id,
                {
                    "status": "failed",
                    "error": str(exc),
                    "stage": "Cola no disponible",
                    "updated_at": _now_iso(),
                },
            )
            raise HTTPException(status_code=503, detail="Cola temporalmente no disponible. Intenta de nuevo en unos minutos.") from exc

        return {
            "job_id": project_id,
            "sequence": sequence,
            "status": "queued",
            "billed_amount": billed_amount,
            "message": "Proyecto Inteligente en cola",
            "queue_task_id": queue_task_id,
        }
    except Exception:
        release_generation_slot("render", user.user_id)
        raise


@router.get("/{job_id}", response_model=dict)
def intelligent_project_status(
    job_id: str,
    user: AuthenticatedUser = Depends(require_authenticated_user),
):
    job = _load_project_job_owned(job_id, user.user_id)
    return {
        "job_id": str(job.get("job_id") or job_id),
        "status": str(job.get("status") or "queued"),
        "progress": int(job.get("progress") or 0),
        "stage": str(job.get("stage") or "En cola"),
        "error": job.get("error"),
        "output_image": job.get("output_image"),
        "output_video": job.get("output_video"),
        "report_pdf": job.get("report_pdf"),
        "selected_material_names": job.get("selected_material_names") or [],
        "quantities": job.get("quantities") or [],
        "report_download_url": f"/intelligent-project/{job_id}/report",
        "video_download_url": f"/intelligent-project/{job_id}/video",
    }


@router.get("/{job_id}/video", include_in_schema=False)
def intelligent_project_video_download(
    job_id: str,
    user: AuthenticatedUser = Depends(require_authenticated_user),
):
    job = _load_project_job_owned(job_id, user.user_id)
    raw_path = str(job.get("output_video") or "").strip()
    if not raw_path:
        raise HTTPException(status_code=404, detail="Video no disponible")
    target = Path(raw_path)
    if not target.exists():
        raise HTTPException(status_code=404, detail="Video expirado o no encontrado")
    return FileResponse(path=target, media_type="video/mp4", filename=f"IA-IMP-proyecto-{job_id[:8]}.mp4")


@router.get("/{job_id}/report", include_in_schema=False)
def intelligent_project_report_download(
    job_id: str,
    user: AuthenticatedUser = Depends(require_authenticated_user),
):
    job = _load_project_job_owned(job_id, user.user_id)
    raw_path = str(job.get("report_pdf") or "").strip()
    if not raw_path:
        raise HTTPException(status_code=404, detail="PDF no disponible")
    target = Path(raw_path)
    if not target.exists():
        raise HTTPException(status_code=404, detail="PDF expirado o no encontrado")
    return FileResponse(path=target, media_type="application/pdf", filename=f"IA-IMP-proyecto-{job_id[:8]}.pdf")
