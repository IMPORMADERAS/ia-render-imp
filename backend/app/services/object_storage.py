from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any
from urllib.parse import quote

from ..config import settings


def is_object_storage_enabled() -> bool:
    return bool(
        settings.object_storage_enabled
        and (settings.object_storage_bucket or "").strip()
        and (settings.object_storage_access_key_id or "").strip()
        and (settings.object_storage_secret_access_key or "").strip()
    )


def _client():
    import boto3

    return boto3.client(
        "s3",
        region_name=(settings.object_storage_region or "").strip() or None,
        endpoint_url=(settings.object_storage_endpoint_url or "").strip() or None,
        aws_access_key_id=(settings.object_storage_access_key_id or "").strip() or None,
        aws_secret_access_key=(settings.object_storage_secret_access_key or "").strip() or None,
    )


def _bucket() -> str:
    bucket = (settings.object_storage_bucket or "").strip()
    if not bucket:
        raise RuntimeError("OBJECT_STORAGE_BUCKET no configurado")
    return bucket


def guess_media_type(file_path: str) -> str:
    return mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"


def upload_file(local_path: str, storage_key: str, media_type: str | None = None) -> dict[str, str]:
    if not is_object_storage_enabled():
        raise RuntimeError("Object storage no habilitado")

    safe_key = str(storage_key or "").strip().lstrip("/")
    if not safe_key:
        raise ValueError("storage_key requerido")

    path = Path(local_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Archivo local no encontrado: {local_path}")

    extra_args: dict[str, Any] = {}
    content_type = (media_type or guess_media_type(str(path))).strip()
    if content_type:
        extra_args["ContentType"] = content_type

    client = _client()
    with path.open("rb") as handle:
        client.upload_fileobj(handle, _bucket(), safe_key, ExtraArgs=extra_args or None)

    return {
        "storage_key": safe_key,
        "url": get_download_url(safe_key),
    }


def get_download_url(storage_key: str) -> str:
    if not is_object_storage_enabled():
        raise RuntimeError("Object storage no habilitado")

    safe_key = str(storage_key or "").strip().lstrip("/")
    if not safe_key:
        raise ValueError("storage_key requerido")

    public_base = (settings.object_storage_public_base_url or "").strip().rstrip("/")
    if public_base:
        return f"{public_base}/{quote(safe_key, safe='/')}"

    client = _client()
    return str(
        client.generate_presigned_url(
            "get_object",
            Params={"Bucket": _bucket(), "Key": safe_key},
            ExpiresIn=max(60, int(settings.object_storage_presign_expiry_seconds)),
        )
    )


def delete_file(storage_key: str) -> None:
    if not is_object_storage_enabled():
        return

    safe_key = str(storage_key or "").strip().lstrip("/")
    if not safe_key:
        return

    client = _client()
    client.delete_object(Bucket=_bucket(), Key=safe_key)
