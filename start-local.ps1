$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
  Write-Host "[setup] Creando entorno virtual..."
  python -m venv .venv
}

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

Write-Host "[setup] Actualizando pip..."
& $python -m pip install --upgrade pip

Write-Host "[setup] Instalando dependencias..."
& $python -m pip install -r backend/requirements.txt
Write-Host "[setup] Si quieres IA completa, luego ejecuta: $python -m pip install -r backend/requirements-ai.txt"

if (-not (Test-Path "backend/.env")) {
  Write-Host "[setup] Creando backend/.env desde ejemplo..."
  Copy-Item "backend/.env.example" "backend/.env"
}

Write-Host "[hint] Cloud pro: configura RENDER_PROVIDER=replicate y REPLICATE_API_TOKEN en backend/.env"

Write-Host "[run] Iniciando API en http://127.0.0.1:8000"
Write-Host "[run] Studio en http://127.0.0.1:8000/studio"
$reloadExclude = '.venv/*'
& $python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload --reload-exclude=$reloadExclude
