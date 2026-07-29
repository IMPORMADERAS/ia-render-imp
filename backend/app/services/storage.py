import json
import mimetypes
import sqlite3
from pathlib import Path
from typing import Any

from ..config import settings
from .object_storage import delete_file as delete_remote_file, get_download_url as get_remote_download_url
from .postgres_mirror import (
    get_generation_record as pg_get_generation_record,
    get_next_job_sequence as pg_get_next_job_sequence,
    init_postgres_mirror_schema,
    list_generation_records as pg_list_generation_records,
    mirror_upsert_generation_record,
)
from .primary_router import should_read_from_postgres, sqlite_fallback_enabled


DB_PATH = Path(settings.data_dir) / "generations.db"
JOBS_PATH = Path(settings.data_dir) / "jobs.json"
ANIMS_PATH = Path(settings.data_dir) / "animations.json"
MUSIC_PATH = Path(settings.data_dir) / "music_jobs.json"


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def _record_index_fields(payload: dict[str, Any]) -> tuple[int, str]:
    user_id = int(payload.get("billed_user_id") or 0)
    updated_at = str(payload.get("updated_at") or payload.get("completed_at") or payload.get("started_at") or "")
    return user_id, updated_at


def _upsert_record(table: str, record_id: str, payload: dict[str, Any]) -> None:
    user_id, updated_at = _record_index_fields(payload)
    payload_json = json.dumps(payload, ensure_ascii=False)
    use_postgres_primary = should_read_from_postgres("jobs", record_id)

    if use_postgres_primary:
        try:
            mirror_upsert_generation_record(table, str(record_id), int(user_id), str(updated_at), payload)
            if not sqlite_fallback_enabled():
                return
        except Exception:
            if not sqlite_fallback_enabled():
                raise

    with _get_conn() as conn:
        conn.execute(
            f"""
            INSERT INTO {table} (id, user_id, updated_at, payload_json)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                user_id=excluded.user_id,
                updated_at=excluded.updated_at,
                payload_json=excluded.payload_json
            """,
            (str(record_id), user_id, updated_at, payload_json),
        )

    if not use_postgres_primary:
        try:
            mirror_upsert_generation_record(table, str(record_id), int(user_id), str(updated_at), payload)
        except Exception:
            pass


def _get_record(table: str, record_id: str) -> dict[str, Any] | None:
    with _get_conn() as conn:
        row = conn.execute(f"SELECT payload_json FROM {table} WHERE id = ?", (str(record_id),)).fetchone()
    if row is None:
        return None
    try:
        data = json.loads(str(row["payload_json"] or "{}"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _iter_records(table: str, user_id: int | None = None) -> list[tuple[str, dict[str, Any]]]:
    query = f"SELECT id, payload_json FROM {table}"
    params: tuple[Any, ...] = ()
    if user_id is not None:
        query += " WHERE user_id = ?"
        params = (int(user_id),)

    with _get_conn() as conn:
        rows = conn.execute(query, params).fetchall()

    items: list[tuple[str, dict[str, Any]]] = []
    for row in rows:
        try:
            payload = json.loads(str(row["payload_json"] or "{}"))
        except Exception:
            continue
        if isinstance(payload, dict):
            items.append((str(row["id"]), payload))
    return items


def _asset_exists(payload: dict[str, Any], path_key: str, storage_key_key: str, storage_url_key: str) -> bool:
    raw_path = str(payload.get(path_key) or "").strip()
    if raw_path and Path(raw_path).exists():
        return True

    if str(payload.get(storage_key_key) or "").strip():
        return True
    if str(payload.get(storage_url_key) or "").strip():
        return True
    return False


def _migrate_legacy_json_file(table: str, file_path: Path) -> None:
    if not file_path.exists():
        return
    try:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return
    if not isinstance(raw, dict):
        return

    for record_id, payload in raw.items():
        if not isinstance(payload, dict):
            continue
        _upsert_record(table, str(record_id), payload)


def init_generation_storage_db() -> None:
    try:
        init_postgres_mirror_schema()
    except Exception:
        pass

    with _get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS jobs (
              id TEXT PRIMARY KEY,
              user_id INTEGER NOT NULL DEFAULT 0,
              updated_at TEXT NOT NULL DEFAULT '',
              payload_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS anims (
              id TEXT PRIMARY KEY,
              user_id INTEGER NOT NULL DEFAULT 0,
              updated_at TEXT NOT NULL DEFAULT '',
              payload_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS music_jobs (
              id TEXT PRIMARY KEY,
              user_id INTEGER NOT NULL DEFAULT 0,
              updated_at TEXT NOT NULL DEFAULT '',
              payload_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS storage_migrations (
              migration_key TEXT PRIMARY KEY,
              done_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_jobs_user_updated ON jobs(user_id, updated_at DESC);
            CREATE INDEX IF NOT EXISTS idx_anims_user_updated ON anims(user_id, updated_at DESC);
            CREATE INDEX IF NOT EXISTS idx_music_user_updated ON music_jobs(user_id, updated_at DESC);
            """
        )

        done = {
            str(row["migration_key"])
            for row in conn.execute("SELECT migration_key FROM storage_migrations").fetchall()
        }

    migrations = [
        ("jobs-json-to-sqlite-v1", "jobs", JOBS_PATH),
        ("anims-json-to-sqlite-v1", "anims", ANIMS_PATH),
        ("music-json-to-sqlite-v1", "music_jobs", MUSIC_PATH),
    ]

    for key, table, path in migrations:
        if key in done:
            continue
        _migrate_legacy_json_file(table, path)
        with _get_conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO storage_migrations (migration_key, done_at) VALUES (?, datetime('now'))",
                (key,),
            )


def create_job(job_id: str, payload: dict[str, Any]) -> None:
    _upsert_record("jobs", job_id, payload)


def update_job(job_id: str, updates: dict[str, Any]) -> None:
    current = get_job(job_id)
    if current is None:
        return
    current.update(updates)
    _upsert_record("jobs", job_id, current)


def get_job(job_id: str) -> dict[str, Any] | None:
    if should_read_from_postgres("jobs", job_id):
        try:
            payload = pg_get_generation_record("jobs", str(job_id))
            if payload is not None:
                return payload
            if not sqlite_fallback_enabled():
                return None
        except Exception:
            if not sqlite_fallback_enabled():
                return None
    return _get_record("jobs", job_id)


def get_next_sequence() -> int:
    if should_read_from_postgres("jobs", "next-sequence"):
        try:
            seq = pg_get_next_job_sequence()
            if seq is not None:
                return int(seq)
            if not sqlite_fallback_enabled():
                return 1
        except Exception:
            if not sqlite_fallback_enabled():
                return 1

    max_seq = 0
    for _, payload in _iter_records("jobs"):
        try:
            seq = int(payload.get("sequence", 0))
        except (TypeError, ValueError):
            seq = 0
        if seq > max_seq:
            max_seq = seq
    return max_seq + 1 if max_seq > 0 else 1


def create_anim(anim_id: str, payload: dict[str, Any]) -> None:
    _upsert_record("anims", anim_id, payload)


def update_anim(anim_id: str, updates: dict[str, Any]) -> None:
    current = get_anim(anim_id)
    if current is None:
        return
    current.update(updates)
    _upsert_record("anims", anim_id, current)


def get_anim(anim_id: str) -> dict[str, Any] | None:
    if should_read_from_postgres("jobs", anim_id):
        try:
            payload = pg_get_generation_record("anims", str(anim_id))
            if payload is not None:
                return payload
            if not sqlite_fallback_enabled():
                return None
        except Exception:
            if not sqlite_fallback_enabled():
                return None
    return _get_record("anims", anim_id)


def create_music(music_id: str, payload: dict[str, Any]) -> None:
    _upsert_record("music_jobs", music_id, payload)


def update_music(music_id: str, updates: dict[str, Any]) -> None:
    current = get_music(music_id)
    if current is None:
        return
    current.update(updates)
    _upsert_record("music_jobs", music_id, current)


def get_music(music_id: str) -> dict[str, Any] | None:
    if should_read_from_postgres("jobs", music_id):
        try:
            payload = pg_get_generation_record("music_jobs", str(music_id))
            if payload is not None:
                return payload
            if not sqlite_fallback_enabled():
                return None
        except Exception:
            if not sqlite_fallback_enabled():
                return None
    return _get_record("music_jobs", music_id)


def list_user_generation_history(user_id: int, limit: int = 100) -> list[dict[str, Any]]:
    safe_limit = max(1, min(500, int(limit)))
    uid = int(user_id)

    items: list[dict[str, Any]] = []

    if should_read_from_postgres("jobs", uid):
        try:
            job_records = pg_list_generation_records("jobs", uid, limit=safe_limit)
            anim_records = pg_list_generation_records("anims", uid, limit=safe_limit)
            music_records = pg_list_generation_records("music_jobs", uid, limit=safe_limit)
        except Exception:
            if not sqlite_fallback_enabled():
                return []
            job_records = []
            anim_records = []
            music_records = []

        if job_records or anim_records or music_records or not sqlite_fallback_enabled():
            for job_id, payload in job_records:
                if int(payload.get("billed_user_id") or 0) != uid:
                    continue

                module = "img2img"
                if str(payload.get("project_module") or "") == "intelligent_project":
                    module = "intelligent_project"
                elif payload.get("material_names"):
                    module = "materials"
                elif not payload.get("input_image"):
                    module = "text2img"

                out_path = str(payload.get("output_image") or "")
                image_available = _asset_exists(payload, "output_image", "output_storage_key", "output_storage_url")
                video_available = _asset_exists(payload, "output_video", "video_storage_key", "video_storage_url")
                report_available = _asset_exists(payload, "report_pdf", "report_storage_key", "report_storage_url")
                has_file = image_available or video_available or report_available

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
                            "has_image": image_available,
                            "has_video": video_available,
                            "has_report": report_available,
                        },
                    }
                )

            for anim_id, payload in anim_records:
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

            for music_id, payload in music_records:
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

    for job_id, payload in _iter_records("jobs", user_id=uid):
        if int(payload.get("billed_user_id") or 0) != uid:
            continue

        module = "img2img"
        if str(payload.get("project_module") or "") == "intelligent_project":
            module = "intelligent_project"
        elif payload.get("material_names"):
            module = "materials"
        elif not payload.get("input_image"):
            module = "text2img"

        out_path = str(payload.get("output_image") or "")
        image_available = _asset_exists(payload, "output_image", "output_storage_key", "output_storage_url")
        video_available = _asset_exists(payload, "output_video", "video_storage_key", "video_storage_url")
        report_available = _asset_exists(payload, "report_pdf", "report_storage_key", "report_storage_url")
        has_file = image_available or video_available or report_available

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
                    "has_image": image_available,
                    "has_video": video_available,
                    "has_report": report_available,
                },
            }
        )

    for anim_id, payload in _iter_records("anims", user_id=uid):
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

    for music_id, payload in _iter_records("music_jobs", user_id=uid):
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


def _job_asset_target(record: dict[str, Any], output_id: str, asset: str) -> tuple[str, str, str, str]:
    safe_asset = str(asset or "image").strip().lower()
    seq = record.get("sequence") or str(output_id)[:8]

    if safe_asset == "video":
        return (
            str(record.get("output_video") or ""),
            str(record.get("video_storage_key") or ""),
            str(record.get("video_storage_url") or ""),
            f"IA-IMP-proyecto-video-{str(output_id)[:8]}.mp4",
        )

    if safe_asset == "report":
        return (
            str(record.get("report_pdf") or ""),
            str(record.get("report_storage_key") or ""),
            str(record.get("report_storage_url") or ""),
            f"IA-IMP-proyecto-reporte-{str(output_id)[:8]}.pdf",
        )

    return (
        str(record.get("output_image") or ""),
        str(record.get("output_storage_key") or ""),
        str(record.get("output_storage_url") or ""),
        f"IA-IMP-{seq}{Path(str(record.get('output_image') or '')).suffix or '.png'}",
    )


def get_user_generation_download(user_id: int, output_type: str, output_id: str, asset: str = "image") -> tuple[Path, str]:
    """Returns (file_path, download_filename). Raises ValueError on ownership/not-found/unavailable."""
    uid = int(user_id)
    safe_id = str(output_id).strip()
    safe_type = str(output_type).strip().lower()

    if safe_type == "job":
        record = get_job(safe_id)
        if record is None:
            raise ValueError("Generacion no encontrada")
        if int(record.get("billed_user_id") or 0) != uid:
            raise ValueError("No tienes permiso para descargar este archivo")
        raw_path, _storage_key, _storage_url, filename = _job_asset_target(record, safe_id, asset)
        if not raw_path:
            raise ValueError("Archivo no disponible: la generacion aun no ha terminado")
        p = Path(raw_path)
        if not p.exists():
            raise ValueError("Archivo expirado: Railway reinicio el contenedor. Vuelvelo a generar.")
        return p, filename

    if safe_type == "anim":
        record = get_anim(safe_id)
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
        record = get_music(safe_id)
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


def get_record_download_target(record: dict[str, Any], output_type: str, output_id: str, asset: str = "image") -> dict[str, Any]:
    safe_type = str(output_type).strip().lower()

    if safe_type == "job":
        raw_path, storage_key, storage_url, filename = _job_asset_target(record, output_id, asset)
        media_type = "application/octet-stream"
        if raw_path:
            media_type = mimetypes.guess_type(raw_path)[0] or media_type
        return {"local_path": raw_path, "storage_key": storage_key, "storage_url": storage_url, "filename": filename, "media_type": media_type}

    if safe_type == "anim":
        raw_path = str(record.get("video_output") or "")
        storage_key = str(record.get("video_storage_key") or "")
        storage_url = str(record.get("video_storage_url") or "")
        return {"local_path": raw_path, "storage_key": storage_key, "storage_url": storage_url, "filename": f"IA-IMP-video-{str(output_id)[:8]}.mp4", "media_type": "video/mp4"}

    if safe_type == "music":
        raw_path = str(record.get("audio_output") or "")
        storage_key = str(record.get("audio_storage_key") or "")
        storage_url = str(record.get("audio_storage_url") or "")
        mode = str(record.get("mode") or "music")
        return {"local_path": raw_path, "storage_key": storage_key, "storage_url": storage_url, "filename": f"IA-IMP-{mode}-{str(output_id)[:8]}.mp3", "media_type": "audio/mpeg"}

    raise ValueError("Tipo de generacion invalido")


def resolve_download_url(storage_key: str, storage_url: str) -> str:
    safe_url = str(storage_url or "").strip()
    if safe_url:
        return safe_url
    safe_key = str(storage_key or "").strip()
    if safe_key:
        return get_remote_download_url(safe_key)
    return ""


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


def _safe_remote_delete(storage_key: Any) -> bool:
    raw = str(storage_key or "").strip()
    if not raw:
        return False
    try:
        delete_remote_file(raw)
        return True
    except Exception:
        return False


def delete_user_generation_data(user_id: int) -> dict[str, int]:
    uid = int(user_id)

    deleted_jobs = 0
    deleted_anims = 0
    deleted_music = 0
    deleted_files = 0

    job_rows = _iter_records("jobs", user_id=uid)
    for job_id, payload in job_rows:
        if int(payload.get("billed_user_id") or 0) != uid:
            continue

        deleted_jobs += 1
        deleted_files += int(_safe_unlink(payload.get("input_image")))
        deleted_files += int(_safe_unlink(payload.get("output_image")))
        deleted_files += int(_safe_remote_delete(payload.get("output_storage_key")))

    with _get_conn() as conn:
        conn.execute("DELETE FROM jobs WHERE user_id = ?", (uid,))

    anim_rows = _iter_records("anims", user_id=uid)
    for anim_id, payload in anim_rows:
        if int(payload.get("billed_user_id") or 0) != uid:
            continue

        deleted_anims += 1
        deleted_files += int(_safe_unlink(payload.get("source_image")))
        deleted_files += int(_safe_unlink(payload.get("source_video")))
        deleted_files += int(_safe_unlink(payload.get("video_output")))
        deleted_files += int(_safe_remote_delete(payload.get("video_storage_key")))

    with _get_conn() as conn:
        conn.execute("DELETE FROM anims WHERE user_id = ?", (uid,))

    music_rows = _iter_records("music_jobs", user_id=uid)
    for music_id, payload in music_rows:
        if int(payload.get("billed_user_id") or 0) != uid:
            continue

        deleted_music += 1
        deleted_files += int(_safe_unlink(payload.get("audio_output")))
        deleted_files += int(_safe_remote_delete(payload.get("audio_storage_key")))

    with _get_conn() as conn:
        conn.execute("DELETE FROM music_jobs WHERE user_id = ?", (uid,))

    return {
        "deleted_jobs": deleted_jobs,
        "deleted_anims": deleted_anims,
        "deleted_music": deleted_music,
        "deleted_files": deleted_files,
    }


init_generation_storage_db()
