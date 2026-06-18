# Guia de despliegue: GitHub + Railway + subdominio Hostinger

Objetivo:
- Subir este proyecto a GitHub.
- Desplegarlo en Railway.
- Publicarlo con dominio personalizado en:
  - iaimp.impormaderasltda.com

---

## 1. Preparar y subir el repositorio a GitHub

### 1.1 Crear repositorio en GitHub
1. En GitHub, crea un repositorio nuevo (ejemplo: ia-render-imp).
2. No agregues README automatico si ya tienes uno local.

### 1.2 Inicializar git localmente (si aun no existe)
Ejecuta en la raiz del proyecto:

    git init
    git add .
    git commit -m "chore: base proyecto IA Render"

### 1.3 Conectar remoto y subir
Reemplaza TU_USUARIO y TU_REPO:

    git branch -M main
    git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
    git push -u origin main

Si ya tienes remoto configurado:

    git push

---

## 2. Desplegar en Railway

Este proyecto ya tiene Dockerfile en backend/Dockerfile, asi que usaremos despliegue por Docker.

### 2.1 Crear proyecto en Railway
1. Entra a Railway.
2. New Project.
3. Deploy from GitHub Repo.
4. Selecciona tu repositorio.

### 2.2 Configuracion de build
En la configuracion del servicio:
1. Builder: Dockerfile.
2. Dockerfile Path: backend/Dockerfile
3. Root Directory: dejar vacio (raiz del repo).

### 2.3 Variables de entorno en Railway
En Variables, agrega al menos:

    APP_ENV=production
    ADMIN_USERNAME=tu_admin_seguro
    ADMIN_PASSWORD=tu_password_admin_seguro
    RENDER_PROVIDER=replicate
    REPLICATE_API_TOKEN=TU_TOKEN_REPLICATE
    REPLICATE_MODEL=black-forest-labs/flux-kontext-pro
    REPLICATE_INPUT_IMAGE_FIELD=input_image
    FALLBACK_TO_LOCAL_ON_CLOUD_ERROR=true
    USE_GPU=false

Si usaras pagos Wompi, agrega tambien:

    WOMPI_PUBLIC_KEY=...
    WOMPI_PRIVATE_KEY=...
    WOMPI_EVENTS_KEY=...
    WOMPI_INTEGRITY_KEY=...
    WOMPI_CURRENCY=COP

Si usaras correo para recuperacion de clave, agrega SMTP:

    SMTP_HOST=...
    SMTP_PORT=587
    SMTP_USERNAME=...
    SMTP_PASSWORD=...
    SMTP_FROM_EMAIL=...
    SMTP_USE_TLS=true

Notas importantes:
- En Railway no hay GPU por defecto, por eso USE_GPU=false.
- Si usas RENDER_PROVIDER=local en Railway, el rendimiento sera limitado.
- Para produccion, recomienda RENDER_PROVIDER=replicate.
- En produccion no dejes credenciales admin por defecto. La app ahora exige `ADMIN_USERNAME` y `ADMIN_PASSWORD` configurados y cookies seguras sobre HTTPS.

### 2.4 Volumen persistente (recomendado)
El proyecto guarda datos en backend/data. En Railway el filesystem del contenedor es efimero.

Para no perder data:
1. En Railway, agrega un Volume.
2. Montalo en:

    /app/backend/data

### 2.5 Puerto
No necesitas fijar PORT manualmente porque Dockerfile ya expone 8000 y el CMD usa ese puerto.

### 2.6 Deploy
1. Trigger Deploy (o redeploy automatico al hacer push).
2. Espera estado Healthy.
3. Abre la URL publica temporal de Railway y valida:
   - /studio
   - /docs

---

## 3. Configurar dominio personalizado en Railway

### 3.1 Agregar dominio
1. En Railway, abre tu servicio.
2. Settings -> Domains.
3. Add Domain.
4. Escribe:

    iaimp.impormaderasltda.com

5. Railway te mostrara el target DNS (normalmente CNAME a algo tipo xxxx.up.railway.app).

Guarda exactamente ese target.

---

## 4. Configurar DNS en Hostinger

### 4.1 Ir al DNS Zone Editor
1. En Hostinger, entra al dominio impormaderasltda.com.
2. DNS Zone Editor.

### 4.2 Crear o ajustar registro
Crea un registro CNAME:
- Type: CNAME
- Name/Host: iaimp
- Target/Points to: el valor que te dio Railway (ejemplo: xxxx.up.railway.app)
- TTL: 300 (o default)

Importante:
- Si existe un A o AAAA para iaimp, borralo para evitar conflicto.
- No uses redireccion web de Hostinger para este subdominio.

### 4.3 Esperar propagacion
Puede tardar de 5 minutos a 24 horas (normalmente menos de 1 hora).

---

## 5. Verificar SSL y acceso final

1. Regresa a Railway -> Domains.
2. Espera estado Verified/Active.
3. Prueba:

    https://iaimp.impormaderasltda.com/studio

4. Verifica candado SSL activo.

---

## 6. Flujo de actualizaciones

Cada vez que cambies codigo:

    git add .
    git commit -m "feat: tu cambio"
    git push

Railway redeploya automaticamente desde GitHub.

---

## 7. Checklist rapido

- Repositorio en GitHub subido.
- Servicio Railway creado desde GitHub.
- Dockerfile Path en backend/Dockerfile.
- Variables de entorno cargadas.
- Volume montado en /app/backend/data.
- Dominio agregado en Railway: iaimp.impormaderasltda.com.
- CNAME creado en Hostinger para iaimp.
- SSL activo y URL final funcionando.

---

## 8. Troubleshooting

### Error 502 o app no inicia
- Revisa logs de Railway.
- Confirma que el deploy uso backend/Dockerfile.
- Confirma que no falta REPLICATE_API_TOKEN si RENDER_PROVIDER=replicate.

### Dominio no verifica
- Confirma CNAME exacto (sin espacios ni typo).
- Elimina registros A/AAAA en conflicto para iaimp.
- Espera propagacion DNS.

### App funciona pero pierde datos
- Falta Volume o esta montado en ruta incorrecta.
- Debe montarse en /app/backend/data.

---

Si quieres, como siguiente paso puedo crearte tambien un archivo de checklist operativo de produccion (monitoring, backups, alertas y rotacion de secrets) para dejarlo listo para uso real.
