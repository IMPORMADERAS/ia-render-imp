from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException
from fastapi.responses import FileResponse

from ..config import settings
from ..services.music_generator import music_generator
from ..services.storage import create_music, get_music, update_music
from ..services.auth_wallet import AuthenticatedUser, InsufficientBalanceError, credit_balance, debit_balance, require_authenticated_user
from ..services.billing import module_cost_music_cop

router = APIRouter(prefix="/music", tags=["music"])

MUSIC_DIR = Path(settings.data_dir) / "music"


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("/generate", response_model=dict)
async def generate_music(
    background_tasks: BackgroundTasks,
    mode: str = Form(default="instrumental"),
    genre: str = Form(default="cinematic electronic"),
    mood: str = Form(default="uplifting and emotional"),
    instruments: str = Form(default="synths, drums, bass"),
    user_taste: str = Form(default="modern production, clear mix"),
    duration_seconds: int = Form(default=180),
    bpm: int | None = Form(default=None),
    language: str = Form(default="es"),
    theme: str = Form(default="resiliencia y crecimiento"),
    custom_lyrics: str = Form(default=""),
    seed: int | None = Form(default=None),
    user: AuthenticatedUser = Depends(require_authenticated_user),
):
    safe_mode = (mode or "instrumental").strip().lower()
    if safe_mode not in {"instrumental", "song"}:
        raise HTTPException(status_code=400, detail="mode debe ser 'instrumental' o 'song'")

    safe_duration = max(8, min(180, int(duration_seconds)))
    music_id = str(uuid4())

    billed_amount = module_cost_music_cop(safe_duration)
    try:
        balance_after = debit_balance(user.user_id, billed_amount, "music", f"Generacion musica {music_id}")
    except InsufficientBalanceError as exc:
        raise HTTPException(status_code=402, detail="Saldo insuficiente. Recarga tu cuenta para generar audio.") from exc

    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    output_path = MUSIC_DIR / f"{music_id}.mp3"

    create_music(
        music_id,
        {
            "music_id": music_id,
            "status": "queued",
            "mode": safe_mode,
            "genre": genre,
            "mood": mood,
            "instruments": instruments,
            "user_taste": user_taste,
            "duration_seconds": safe_duration,
            "bpm": bpm,
            "language": language,
            "theme": theme,
            "custom_lyrics": custom_lyrics,
            "audio_output": None,
            "error": None,
            "stage": "En cola",
            "progress": 0,
            "model": None,
            "started_at": None,
            "completed_at": None,
            "updated_at": _utc(),
            "billed_user_id": user.user_id,
            "billed_amount_cop": billed_amount,
            "balance_after_debit": balance_after,
        },
    )

    def run_music() -> None:
        try:
            update_music(
                music_id,
                {
                    "status": "processing",
                    "stage": "Generando audio",
                    "progress": 20,
                    "started_at": _utc(),
                    "updated_at": _utc(),
                },
            )

            result = music_generator.generate_replicate(
                output_audio_path=str(output_path),
                mode=safe_mode,
                genre=genre,
                mood=mood,
                instruments=instruments,
                user_taste=user_taste,
                duration_seconds=safe_duration,
                bpm=bpm,
                language=language,
                theme=theme,
                custom_lyrics=custom_lyrics,
                seed=seed,
            )

            elapsed = int(result.get("duration_seconds", 1))
            update_music(
                music_id,
                {
                    "status": "completed",
                    "audio_output": str(output_path),
                    "progress": 100,
                    "stage": f"Audio listo ({elapsed}s)",
                    "model": str(result.get("model", "")),
                    "completed_at": _utc(),
                    "updated_at": _utc(),
                },
            )
        except Exception as exc:
            try:
                credit_balance(user.user_id, billed_amount, "music_refund", f"Reembolso por fallo musica {music_id}")
            except Exception:
                pass
            update_music(
                music_id,
                {
                    "status": "failed",
                    "error": str(exc),
                    "stage": "Fallo en generacion musical",
                    "updated_at": _utc(),
                },
            )

    background_tasks.add_task(run_music)
    return {"music_id": music_id, "status": "queued"}


@router.get("/{music_id}", response_model=dict)
def get_music_status(music_id: str):
    music = get_music(music_id)
    if music is None:
        raise HTTPException(status_code=404, detail="Audio no encontrado")
    return music


@router.get("/{music_id}/audio")
def get_music_audio(music_id: str):
    music = get_music(music_id)
    if music is None:
        raise HTTPException(status_code=404, detail="Audio no encontrado")
    if music.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Audio aun no disponible")

    audio_path = music.get("audio_output")
    if not audio_path or not Path(audio_path).exists():
        raise HTTPException(status_code=404, detail="Archivo de audio no encontrado")

    mode = music.get("mode", "music")
    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        filename=f"IA-IMP-{mode}-{music_id[:8]}.mp3",
    )
