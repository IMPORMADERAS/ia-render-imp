from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/materials", tags=["materials"])

VALID_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".jfif"}


def _materials_root() -> Path:
    return Path(__file__).resolve().parents[3] / "Materiales"


@router.get("/library")
def list_materials() -> dict[str, list[dict[str, str]]]:
    root = _materials_root()
    if not root.exists() or not root.is_dir():
        raise HTTPException(status_code=404, detail="Carpeta Materiales no encontrada")

    items: list[dict[str, str]] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in VALID_EXTENSIONS:
            continue

        relative_path = path.relative_to(root).as_posix()
        parts = relative_path.split("/")
        brand = parts[0] if len(parts) > 1 else "General"
        items.append(
            {
                "name": path.stem,
                "brand": brand,
                "relative_path": relative_path,
                "url": f"/materiales/{quote(relative_path, safe='/')}",
            }
        )

    items.sort(key=lambda item: (str(item.get("brand") or "").lower(), str(item.get("name") or "").lower()))

    return {"materials": items}
