# IA Render Arquitectonico (Base Propia)

Motor de IA orientado a renderizado arquitectonico a partir de capturas de modelados (SketchUp, Revit, Blender, Rhino, etc.).

## Que incluye esta base

- API en FastAPI para subir capturas y lanzar renders.
- Pipeline preparado para `img2img + ControlNet` (estructura real para ultra realismo).
- Cola de trabajos en background (sin bloquear peticiones).
- Almacenamiento local de entradas/salidas por `job_id`.
- Punto de extension para entrenamiento/fine-tuning (LoRA) con tu estilo arquitectonico.

## Arquitectura

```mermaid
flowchart LR
    U[Cliente Web/Desktop] --> API[FastAPI API]
    API --> ST[(Storage local / S3)]
    API --> Q[Background Jobs]
    Q --> R[Render Engine\nSDXL + ControlNet]
    R --> ST
    ST --> API
```

## Casos de uso

- Subes una captura de masa/modelado en gris o viewport.
- Agregas prompt de materiales, iluminacion y entorno.
- El motor genera un render fotorealista y guarda variantes.

## Stack

- Python 3.11+
- FastAPI
- Diffusers + Transformers + PyTorch
- Pillow / OpenCV

## Inicio rapido

1. Crear entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r backend/requirements.txt
```

Opcional (motor IA completo con modelos pesados):

```powershell
pip install -r backend/requirements-ai.txt
```

Opcional (motor cloud pro via Replicate):

```powershell
pip install -r backend/requirements.txt
```

3. Configurar variables:

```powershell
copy backend/.env.example backend/.env
```

Si quieres modo cloud pro (opcion 1), en `backend/.env` configura:

```env
RENDER_PROVIDER=replicate
REPLICATE_API_TOKEN=tu_token
REPLICATE_MODEL=black-forest-labs/flux-kontext-pro
REPLICATE_INPUT_IMAGE_FIELD=input_image
FALLBACK_TO_LOCAL_ON_CLOUD_ERROR=true
```

4. Iniciar API:

```powershell
uvicorn backend.app.main:app --reload --port 8000
```

Si quieres habilitar cola distribuida (recomendado para produccion), activa en `backend/.env`:

```env
JOBS_QUEUE_ENABLED=true
REDIS_URL=redis://localhost:6379/0
RQ_QUEUES=default,render,intelligent_project,video,music,influencer,chat,thumbnail
```

Para migracion incremental de persistencia critica (dual-write SQLite + Postgres mirror):

```env
POSTGRES_MIRROR_ENABLED=true
POSTGRES_DSN=postgresql://usuario:password@host:5432/database
POSTGRES_PRIMARY_AUTH_ENABLED=true
POSTGRES_PRIMARY_WALLET_ENABLED=true
POSTGRES_PRIMARY_JOBS_ENABLED=true
POSTGRES_PRIMARY_AUTH_PERCENT=10
POSTGRES_PRIMARY_WALLET_PERCENT=10
POSTGRES_PRIMARY_JOBS_PERCENT=10
SQLITE_FALLBACK_ENABLED=true
RENDER_QUEUE_BACKLOG_LIMIT=250
VIDEO_QUEUE_BACKLOG_LIMIT=80
MUSIC_QUEUE_BACKLOG_LIMIT=120
INFLUENCER_QUEUE_BACKLOG_LIMIT=40
RENDER_USER_ACTIVE_LIMIT=3
VIDEO_USER_ACTIVE_LIMIT=1
MUSIC_USER_ACTIVE_LIMIT=2
INFLUENCER_USER_ACTIVE_LIMIT=1
OBJECT_STORAGE_ENABLED=false
OBJECT_STORAGE_BUCKET=
OBJECT_STORAGE_REGION=
OBJECT_STORAGE_ENDPOINT_URL=
OBJECT_STORAGE_ACCESS_KEY_ID=
OBJECT_STORAGE_SECRET_ACCESS_KEY=
OBJECT_STORAGE_PUBLIC_BASE_URL=
OBJECT_STORAGE_PRESIGN_EXPIRY_SECONDS=3600
BENCHMARK_MODE_ENABLED=false
BENCHMARK_JOB_DURATION_SECONDS=1
```

Los limites anteriores aplican rechazo temprano cuando la plataforma entra en saturacion, evitando que una cola infinita degrade todo el servicio.

Si activas object storage, los outputs generados se suben a S3/R2 y las descargas siguen funcionando aunque Railway reinicie el contenedor local.

Backfill inicial (una vez) de historico SQLite hacia Postgres mirror:

```powershell
python backend/scripts/backfill_postgres_mirror.py
```

Smoke test basico de endpoints de infraestructura admin:

```powershell
python backend/scripts/load_test_smoke.py --base-url http://127.0.0.1:8000 --requests 100 --concurrency 20 --cookie "iaimp_admin_session=TU_COOKIE"
```

Load test mixto de negocio usando benchmark mode para evitar costo real de inferencia:

```powershell
python backend/scripts/load_test_business_mix.py --base-url http://127.0.0.1:8000 --users 50 --requests 500 --concurrency 50 --include-animate
```

Para simular tambien influencer, activa benchmark mode y agrega `--include-influencer`.

Y levanta un worker adicional:

```powershell
python backend/worker.py
```

Para entorno local completo con API + Worker + Redis:

```powershell
docker compose up --build
```

5. Abrir Swagger:

- http://127.0.0.1:8000/docs

6. Abrir Studio web:

- http://127.0.0.1:8000/studio

## Modo Cloud Pro (Replicate)

- No depende de tu GPU local.
- Da un salto notable de calidad frente al fallback local.
- Permite iterar rapido mientras entrenas tu IA propia.

Pasos:
- Crea token en Replicate.
- Pegalo en `REPLICATE_API_TOKEN`.
- Deja `RENDER_PROVIDER=replicate`.
- Reinicia la API.

Si Replicate falla (cuota, billing o red), con `FALLBACK_TO_LOCAL_ON_CLOUD_ERROR=true` el job se completa automaticamente en local y queda registrado como fallback.

## Endpoints clave

- `POST /jobs/render` -> sube captura y crea render.
- `GET /jobs/{job_id}` -> estado del render.
- `GET /jobs/{job_id}/image` -> imagen final.
- `GET /studio` -> interfaz visual de subida y previsualizacion.
- `GET /admin-api/infra/health` -> salud de Redis/RQ y estado de Postgres mirror (requiere sesion admin).
- `GET /admin-api/infra/cutover` -> configuracion activa de porcentaje por modulo (auth, wallet, jobs).
- `GET /admin-api/infra/consistency` -> comparativo de conteos SQLite vs Postgres mirror para decidir apagado de fallback.
- `GET /admin-api/infra/metrics` -> throughput, errores, latencia promedio y rechazos por modulo.

## Como convertir esto en "IA propia"

1. Crear dataset propio:
- Pares `captura_modelado -> render_final` de tus proyectos.
- Etiquetas consistentes: estilo, hora del dia, materialidad, clima, camara.

2. Fine-tuning (LoRA recomendado):
- Base: SDXL.
- Condicionamiento: ControlNet (canny/depth/lineart) para respetar geometria.
- Entrenar LoRA con tu dataset para tu identidad visual.

3. Inference en produccion:
- Cargar base SDXL + ControlNet + LoRA propia.
- Versionar modelos (`model_registry`).
- Medir calidad con revision humana + metricas de preferencia.

## Siguiente fase recomendada

- Frontend para arrastrar capturas y ver comparativas.
- Manejo de multi-variantes por semilla.
- Exportacion por lote para entregables.
- Persistencia con Postgres y almacenamiento S3.

## Nota

Esta base funciona como arquitectura lista para evolucionar a produccion. El realismo "ultra" depende de:
- calidad de dataset,
- buen fine-tuning,
- GPU adecuada (ideal 16GB+ VRAM),
- prompt engineering y post-proceso.

Para pruebas locales rapidas sin descargar modelos pesados, el sistema usa fallback visual y mantiene todo el flujo API/Studio operativo.
# ia-render-imp

# ia-render-imp


