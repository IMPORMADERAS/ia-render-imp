import json
from pathlib import Path
from typing import Any

from ..config import settings


JOBS_PATH = Path(settings.data_dir) / "jobs.json"


def _load_jobs() -> dict[str, Any]:
    if not JOBS_PATH.exists():
        return {}
    return json.loads(JOBS_PATH.read_text(encoding="utf-8"))


def _save_jobs(jobs: dict[str, Any]) -> None:
    JOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    JOBS_PATH.write_text(json.dumps(jobs, indent=2), encoding="utf-8")


def create_job(job_id: str, payload: dict[str, Any]) -> None:
    jobs = _load_jobs()
    jobs[job_id] = payload
    _save_jobs(jobs)


def update_job(job_id: str, updates: dict[str, Any]) -> None:
    jobs = _load_jobs()
    if job_id not in jobs:
        return
    jobs[job_id].update(updates)
    _save_jobs(jobs)


def get_job(job_id: str) -> dict[str, Any] | None:
    jobs = _load_jobs()
    return jobs.get(job_id)


def get_next_sequence() -> int:
    jobs = _load_jobs()
    max_seq = 0

    for payload in jobs.values():
        try:
            seq = int(payload.get("sequence", 0))
        except (TypeError, ValueError):
            seq = 0
        if seq > max_seq:
            max_seq = seq

    if max_seq == 0:
        # Backward compatibility for jobs created before sequence support.
        return len(jobs) + 1
    return max_seq + 1


# ── Animation job storage ────────────────────────────────────────────────────

ANIMS_PATH = Path(settings.data_dir) / "animations.json"


def _load_anims() -> dict[str, Any]:
    if not ANIMS_PATH.exists():
        return {}
    return json.loads(ANIMS_PATH.read_text(encoding="utf-8"))


def _save_anims(anims: dict[str, Any]) -> None:
    ANIMS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ANIMS_PATH.write_text(json.dumps(anims, indent=2), encoding="utf-8")


def create_anim(anim_id: str, payload: dict[str, Any]) -> None:
    anims = _load_anims()
    anims[anim_id] = payload
    _save_anims(anims)


def update_anim(anim_id: str, updates: dict[str, Any]) -> None:
    anims = _load_anims()
    if anim_id not in anims:
        return
    anims[anim_id].update(updates)
    _save_anims(anims)


def get_anim(anim_id: str) -> dict[str, Any] | None:
    anims = _load_anims()
    return anims.get(anim_id)


# ── Music job storage ────────────────────────────────────────────────────────

MUSIC_PATH = Path(settings.data_dir) / "music_jobs.json"


def _load_music() -> dict[str, Any]:
    if not MUSIC_PATH.exists():
        return {}
    return json.loads(MUSIC_PATH.read_text(encoding="utf-8"))


def _save_music(items: dict[str, Any]) -> None:
    MUSIC_PATH.parent.mkdir(parents=True, exist_ok=True)
    MUSIC_PATH.write_text(json.dumps(items, indent=2), encoding="utf-8")


def create_music(music_id: str, payload: dict[str, Any]) -> None:
    items = _load_music()
    items[music_id] = payload
    _save_music(items)


def update_music(music_id: str, updates: dict[str, Any]) -> None:
    items = _load_music()
    if music_id not in items:
        return
    items[music_id].update(updates)
    _save_music(items)


def get_music(music_id: str) -> dict[str, Any] | None:
    items = _load_music()
    return items.get(music_id)


def list_user_generation_history(user_id: int, limit: int = 100) -> list[dict[str, Any]]:
    safe_limit = max(1, min(500, int(limit)))
    uid = int(user_id)

    items: list[dict[str, Any]] = []

    jobs = _load_jobs()
    for job_id, payload in jobs.items():
        if int(payload.get("billed_user_id") or 0) != uid:
            continue

        module = "img2img"
        if payload.get("material_names"):
            module = "materials"
        elif not payload.get("input_image"):
            module = "text2img"

        out_path = str(payload.get("output_image") or "")
        has_file = bool(out_path and Path(out_path).exists())

        items.append(
            {
                "id": str(job_id),
                "output_type": "job",
                "has_file": has_file,
                "module": module,
                "status": str(payload.get("status") or "unknown"),
                "amount_cop": int(payload.get("billed_amount_cop") or 0),
                "created_at": str(payload.get("started_at") or payload.get("updated_at") or ""),
                "updated_at": str(payload.get("updated_at") or ""),
                "meta": {
                    "sequence": payload.get("sequence"),
                    "prompt": payload.get("prompt"),
                },
            }
        )

    anims = _load_anims()
    for anim_id, payload in anims.items():
        if int(payload.get("billed_user_id") or 0) != uid:
            continue

        module = "influencer" if str(payload.get("kind") or "") == "influencer" else "img2vid"
        vid_path = str(payload.get("video_output") or "")
        has_file = bool(vid_path and Path(vid_path).exists())

        items.append(
            {
                "id": str(anim_id),
                "output_type": "anim",
                "has_file": has_file,
                "module": module,
                "status": str(payload.get("status") or "unknown"),
                "amount_cop": int(payload.get("billed_amount_cop") or 0),
                "created_at": str(payload.get("started_at") or payload.get("updated_at") or ""),
                "updated_at": str(payload.get("updated_at") or ""),
                "meta": {
                    "duration_seconds": payload.get("duration_seconds"),
                    "model": payload.get("model"),
                },
            }
        )

    music_items = _load_music()
    for music_id, payload in music_items.items():
        if int(payload.get("billed_user_id") or 0) != uid:
            continue

        aud_path = str(payload.get("audio_output") or "")
        has_file = bool(aud_path and Path(aud_path).exists())

        items.append(
            {
                "id": str(music_id),
                "output_type": "music",
                "has_file": has_file,
                "module": "music",
                "status": str(payload.get("status") or "unknown"),
                "amount_cop": int(payload.get("billed_amount_cop") or 0),
                "created_at": str(payload.get("started_at") or payload.get("updated_at") or ""),
                "updated_at": str(payload.get("updated_at") or ""),
                "meta": {
                    "duration_seconds": payload.get("duration_seconds"),
                    "mode": payload.get("mode"),
                },
            }
        )

    items.sort(key=lambda x: str(x.get("updated_at") or x.get("created_at") or ""), reverse=True)
    return items[:safe_limit]


def get_user_generation_download(user_id: int, output_type: str, output_id: str) -> tuple[Path, str]:
    """Returns (file_path, download_filename). Raises ValueError on ownership/not-found/unavailable."""
    uid = int(user_id)
    safe_id = str(output_id).strip()
    safe_type = str(output_type).strip().lower()

    if safe_type == "job":
        record = _load_jobs().get(safe_id)
        if record is None:
            raise ValueError("Generacion no encontrada")
        if int(record.get("billed_user_id") or 0) != uid:
            raise ValueError("No tienes permiso para descargar este archivo")
        raw_path = str(record.get("output_image") or "")
        if not raw_path:
            raise ValueError("Archivo no disponible: la generacion aun no ha terminado")
        p = Path(raw_path)
        if not p.exists():
            raise ValueError("Archivo expirado: Railway reinicio el contenedor. Vuelvelo a generar.")
        seq = record.get("sequence") or safe_id[:8]
        filename = f"IA-IMP-{seq}{p.suffix or '.png'}"
        return p, filename

    if safe_type == "anim":
        record = _load_anims().get(safe_id)
        if record is None:
            raise ValueError("Generacion no encontrada")
        if int(record.get("billed_user_id") or 0) != uid:
            raise ValueError("No tienes permiso para descargar este archivo")
        raw_path = str(record.get("video_output") or "")
        if not raw_path:
            raise ValueError("Archivo no disponible: el video aun no ha terminado")
        p = Path(raw_path)
        if not p.exists():
            raise ValueError("Archivo expirado: Railway reinicio el contenedor. Vuelvelo a generar.")
        filename = f"IA-IMP-video-{safe_id[:8]}.mp4"
        return p, filename

    if safe_type == "music":
        record = _load_music().get(safe_id)
        if record is None:
            raise ValueError("Generacion no encontrada")
        if int(record.get("billed_user_id") or 0) != uid:
            raise ValueError("No tienes permiso para descargar este archivo")
        raw_path = str(record.get("audio_output") or "")
        if not raw_path:
            raise ValueError("Archivo no disponible: el audio aun no ha terminado")
        p = Path(raw_path)
        if not p.exists():
            raise ValueError("Archivo expirado: Railway reinicio el contenedor. Vuelvelo a generar.")
        mode = str(record.get("mode") or "music")
        filename = f"IA-IMP-{mode}-{safe_id[:8]}.mp3"
        return p, filename

    raise ValueError("Tipo de generacion invalido")


def _safe_unlink(path_value: Any) -> bool:
    raw = str(path_value or "").strip()
    if not raw:
        return False

    try:
        target = Path(raw)
        if target.exists() and target.is_file():
            target.unlink()
            return True
    except Exception:
        return False

    return False


def delete_user_generation_data(user_id: int) -> dict[str, int]:
    uid = int(user_id)

    deleted_jobs = 0
    deleted_anims = 0
    deleted_music = 0
    deleted_files = 0

    jobs = _load_jobs()
    kept_jobs: dict[str, Any] = {}
    for job_id, payload in jobs.items():
        if int(payload.get("billed_user_id") or 0) != uid:
            kept_jobs[job_id] = payload
            continue

        deleted_jobs += 1
        deleted_files += int(_safe_unlink(payload.get("input_image")))
        deleted_files += int(_safe_unlink(payload.get("output_image")))

    if len(kept_jobs) != len(jobs):
        _save_jobs(kept_jobs)

    anims = _load_anims()
    kept_anims: dict[str, Any] = {}
    for anim_id, payload in anims.items():
        if int(payload.get("billed_user_id") or 0) != uid:
            kept_anims[anim_id] = payload
            continue

        deleted_anims += 1
        deleted_files += int(_safe_unlink(payload.get("source_image")))
        deleted_files += int(_safe_unlink(payload.get("source_video")))
        deleted_files += int(_safe_unlink(payload.get("video_output")))

    if len(kept_anims) != len(anims):
        _save_anims(kept_anims)

    music_items = _load_music()
    kept_music: dict[str, Any] = {}
    for music_id, payload in music_items.items():
        if int(payload.get("billed_user_id") or 0) != uid:
            kept_music[music_id] = payload
            continue

        deleted_music += 1
        deleted_files += int(_safe_unlink(payload.get("audio_output")))

    if len(kept_music) != len(music_items):
        _save_music(kept_music)

    return {
        "deleted_jobs": deleted_jobs,
        "deleted_anims": deleted_anims,
        "deleted_music": deleted_music,
        "deleted_files": deleted_files,
    }
