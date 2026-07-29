from pathlib import Path
from urllib.parse import quote

from fastapi import Depends, FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import ensure_directories, settings
from .routes.chat import router as chat_router
from .routes.jobs import router as jobs_router
from .routes.animate import router as animate_router
from .routes.music import router as music_router
from .routes.payments import router as payments_router
from .routes.materials import router as materials_router
from .routes.influencer import router as influencer_router
from .routes.intelligent_project import router as intelligent_project_router
from .routes.auth import router as auth_router
from .routes.admin import router as admin_router
from .services.auth_wallet import init_auth_wallet_db
from .services.auth_wallet import require_authenticated_user
from .services.admin_auth import init_admin_auth_db
from .services.metrics import MetricsTimer, module_from_request, record_api_request
from .services.pricing_store import get_pricing_config
from .services.storage import init_generation_storage_db

ensure_directories()
init_auth_wallet_db()
init_admin_auth_db()
init_generation_storage_db()

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    timer = MetricsTimer()
    module = module_from_request(request)
    status_code = 500
    try:
        response = await call_next(request)
        status_code = int(response.status_code)
        return response
    finally:
        record_api_request(module, status_code, timer.elapsed_ms())


static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

workspace_dir = Path(__file__).resolve().parents[2]
logo_dir = workspace_dir / "Logo"
if logo_dir.exists():
    app.mount("/brand", StaticFiles(directory=logo_dir), name="brand")

materials_dir = workspace_dir / "Materiales"
if materials_dir.exists():
    app.mount("/materiales", StaticFiles(directory=materials_dir), name="materiales")

contenido_dir = workspace_dir / "Contenido"
if contenido_dir.exists():
    app.mount("/contenido", StaticFiles(directory=contenido_dir), name="contenido")

studio_imp_dir = workspace_dir / "Studio IMP"
if studio_imp_dir.exists():
    app.mount("/studio-imp-static", StaticFiles(directory=studio_imp_dir), name="studio-imp-static")


@app.get("/")
def landing() -> FileResponse:
    return FileResponse(path=static_dir / "index.html")


@app.get("/studio", include_in_schema=False)
def studio() -> FileResponse:
    return FileResponse(path=static_dir / "studio.html")


@app.get("/documentacion", include_in_schema=False)
def documentation_page() -> FileResponse:
    return FileResponse(path=static_dir / "documentation.html")


@app.get("/que-es-iaimp", include_in_schema=False)
def what_is_iaimp_page() -> FileResponse:
    return FileResponse(path=static_dir / "que-es-iaimp.html")


@app.get("/terminos-y-condiciones", include_in_schema=False)
def terms_page() -> FileResponse:
    return FileResponse(path=static_dir / "terms.html")


@app.get("/politica-de-privacidad", include_in_schema=False)
def privacy_page() -> FileResponse:
    return FileResponse(path=static_dir / "privacy.html")


@app.get("/studio-imp", include_in_schema=False)
def studio_imp(_user=Depends(require_authenticated_user)) -> FileResponse:
    if not studio_imp_dir.exists():
        raise HTTPException(status_code=404, detail="Panel Studio IMP no encontrado")
    return FileResponse(path=studio_imp_dir / "index.html")


@app.get("/admin", include_in_schema=False)
def admin_page() -> FileResponse:
    return FileResponse(path=static_dir / "admin.html")


@app.get("/imp-logo", include_in_schema=False)
def brand_logo() -> FileResponse:
    candidate_dirs = [workspace_dir / "Logo", workspace_dir / "logo"]
    candidate_names = ["Logo.png", "logo.png", "Logo.jpg", "logo.jpg", "Logo.webp", "logo.webp"]

    for folder in candidate_dirs:
        if not folder.exists():
            continue
        for name in candidate_names:
            path = folder / name
            if path.exists():
                return FileResponse(path=path)

        for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
            first = next(folder.glob(ext), None)
            if first:
                return FileResponse(path=first)

    raise HTTPException(status_code=404, detail="Logo no encontrado")


@app.get("/examples/library", include_in_schema=False)
def examples_library() -> dict[str, list[dict[str, str]]]:
    candidate_dirs = [workspace_dir / "Contenido", workspace_dir / "contenido"]
    source_dir = next((path for path in candidate_dirs if path.exists()), None)
    if source_dir is None:
        return {"examples": []}

    image_ext = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    video_ext = {".mp4", ".mov", ".webm", ".m4v"}
    audio_ext = {".mp3", ".wav", ".ogg", ".m4a"}

    examples: list[dict[str, str]] = []
    for file_path in sorted(source_dir.rglob("*")):
        if not file_path.is_file():
            continue

        ext = file_path.suffix.lower()
        kind = ""
        if ext in image_ext:
            kind = "image"
        elif ext in video_ext:
            kind = "video"
        elif ext in audio_ext:
            kind = "audio"
        else:
            continue

        relative = file_path.relative_to(source_dir).as_posix()
        examples.append(
            {
                "name": file_path.name,
                "kind": kind,
                "url": f"/contenido/{quote(relative, safe='/')}",
            }
        )

    return {"examples": examples[:24]}


@app.get("/pricing/config", include_in_schema=False)
def pricing_config() -> dict:
    return {"pricing": get_pricing_config()}


app.include_router(jobs_router)
app.include_router(animate_router)
app.include_router(chat_router)
app.include_router(music_router)
app.include_router(payments_router)
app.include_router(materials_router)
app.include_router(influencer_router)
app.include_router(intelligent_project_router)
app.include_router(admin_router)
app.include_router(auth_router)
