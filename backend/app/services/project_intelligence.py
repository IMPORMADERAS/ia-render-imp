from __future__ import annotations

import random
import re
from pathlib import Path
from typing import Any

from ..config import settings
from .pricing_store import get_pricing_config

MATERIALS_ROOT = Path(__file__).resolve().parents[3] / "Materiales"
PROJECTS_DIR = Path(settings.data_dir) / "projects"
DEFAULT_BRAND_M2_RATES: dict[str, int] = {
    "duratex": 83000,
    "arauco": 65500,
}


def _material_candidates() -> list[Path]:
    if not MATERIALS_ROOT.exists() or not MATERIALS_ROOT.is_dir():
        return []

    allowed = {".png", ".jpg", ".jpeg", ".webp"}
    return [p for p in MATERIALS_ROOT.rglob("*") if p.is_file() and p.suffix.lower() in allowed]


def _safe_in_materials(path: Path) -> bool:
    try:
        path.resolve().relative_to(MATERIALS_ROOT.resolve())
        return True
    except Exception:
        return False


def resolve_material_paths(material_names: list[str]) -> list[str]:
    resolved: list[str] = []
    for raw_name in material_names:
        candidate = (MATERIALS_ROOT / str(raw_name or "").strip()).resolve()
        if not _safe_in_materials(candidate):
            continue
        if candidate.exists() and candidate.is_file():
            resolved.append(str(candidate))
    return resolved


def pick_project_materials(strategy: str, requested_names: list[str], limit: int = 2) -> tuple[list[str], list[str]]:
    safe_limit = max(1, min(2, int(limit)))

    if str(strategy or "").strip().lower() == "selected":
        selected_paths = resolve_material_paths(requested_names)[:safe_limit]
        if selected_paths:
            names = [str(Path(p).relative_to(MATERIALS_ROOT).as_posix()) for p in selected_paths]
            return names, selected_paths

    candidates = _material_candidates()
    if not candidates:
        return [], []

    sample = random.sample(candidates, k=min(safe_limit, len(candidates)))
    names = [str(path.relative_to(MATERIALS_ROOT).as_posix()) for path in sample]
    paths = [str(path) for path in sample]
    return names, paths


def parse_room_dimensions(prompt: str) -> tuple[float, float]:
    text = str(prompt or "")
    match = re.search(r"(\d+(?:[\.,]\d+)?)\s*[x×]\s*(\d+(?:[\.,]\d+)?)", text)
    if not match:
        return 4.0, 3.0

    try:
        width = float(match.group(1).replace(",", "."))
        depth = float(match.group(2).replace(",", "."))
    except Exception:
        return 4.0, 3.0

    width = max(1.0, min(50.0, width))
    depth = max(1.0, min(50.0, depth))
    return width, depth


def _parse_room_height(prompt: str, default_height: float = 2.4) -> float:
    text = str(prompt or "").lower()
    match = re.search(r"(?:alto|altura)\s*(?:de)?\s*(\d+(?:[\.,]\d+)?)", text)
    if not match:
        return default_height
    try:
        height = float(match.group(1).replace(",", "."))
    except Exception:
        return default_height
    return max(2.0, min(4.0, height))


def _room_profile(prompt: str) -> str:
    text = str(prompt or "").lower()
    if any(key in text for key in ["baño", "bano", "ducha", "lavamanos"]):
        return "bathroom"
    if any(key in text for key in ["cocina", "isla", "encimera"]):
        return "kitchen"
    if any(key in text for key in ["tv", "television", "mueble tv", "entertainment", "rack"]):
        return "tv_furniture"
    if any(key in text for key in ["closet", "vestier", "walk-in", "armario", "ropero"]):
        return "closet"
    if any(key in text for key in ["oficina", "office", "escritorio", "cowork"]):
        return "office"
    if any(key in text for key in ["sala", "living", "comedor", "estar"]):
        return "living"
    if any(key in text for key in ["fachada", "exterior", "terraza", "balcon", "balcón"]):
        return "exterior"
    return "generic"


def _coverage_profile(profile: str) -> dict[str, float]:
    profiles: dict[str, dict[str, float]] = {
        "bathroom": {
            "floor_ratio": 0.76,
            "walls_ratio": 0.26,
            "ceiling_ratio": 0.00,
            "detail_m2": 0.90,
            "waste_factor": 1.06,
        },
        "kitchen": {
            "floor_ratio": 0.68,
            "walls_ratio": 0.28,
            "ceiling_ratio": 0.03,
            "detail_m2": 1.60,
            "waste_factor": 1.06,
        },
        "tv_furniture": {
            "floor_ratio": 0.20,
            "walls_ratio": 0.10,
            "ceiling_ratio": 0.00,
            "detail_m2": 2.40,
            "waste_factor": 1.08,
        },
        "closet": {
            "floor_ratio": 0.25,
            "walls_ratio": 0.14,
            "ceiling_ratio": 0.00,
            "detail_m2": 2.20,
            "waste_factor": 1.08,
        },
        "office": {
            "floor_ratio": 0.35,
            "walls_ratio": 0.16,
            "ceiling_ratio": 0.02,
            "detail_m2": 1.60,
            "waste_factor": 1.07,
        },
        "living": {
            "floor_ratio": 0.42,
            "walls_ratio": 0.20,
            "ceiling_ratio": 0.02,
            "detail_m2": 1.80,
            "waste_factor": 1.07,
        },
        "exterior": {
            "floor_ratio": 0.50,
            "walls_ratio": 0.18,
            "ceiling_ratio": 0.00,
            "detail_m2": 2.00,
            "waste_factor": 1.10,
        },
        "generic": {
            "floor_ratio": 0.45,
            "walls_ratio": 0.19,
            "ceiling_ratio": 0.02,
            "detail_m2": 1.40,
            "waste_factor": 1.07,
        },
    }
    return profiles.get(profile, profiles["generic"])


def _material_brand(material_name: str) -> str:
    token = str(material_name or "").strip().split("/")[0].strip().lower()
    return token or "general"


def _brand_rate_cop_per_m2(brand: str) -> int:
    pricing = get_pricing_config()
    configured = pricing.get("material_brand_price_cop_m2", {}) if isinstance(pricing, dict) else {}
    try:
        value = int(round(float(configured.get(brand, DEFAULT_BRAND_M2_RATES.get(brand, 0)))))
        return max(0, value)
    except Exception:
        return int(DEFAULT_BRAND_M2_RATES.get(brand, 0))


def _distribution_weights(prompt: str, count: int) -> list[float]:
    if count <= 1:
        return [1.0]

    profile = _room_profile(prompt)

    if profile == "bathroom":
        return [0.20, 0.80]
    if profile == "kitchen":
        return [0.38, 0.62]
    if profile in {"tv_furniture", "closet"}:
        return [0.65, 0.35]
    if profile == "office":
        return [0.55, 0.45]
    if profile == "living":
        return [0.48, 0.52]
    if profile == "exterior":
        return [0.45, 0.55]
    return [0.46, 0.54]


def _estimate_render_application_factor(render_image_path: str | None) -> float:
    if not render_image_path:
        return 0.74

    image_path = Path(str(render_image_path).strip())
    if not image_path.exists() or not image_path.is_file():
        return 0.74

    try:
        from PIL import Image

        image = Image.open(str(image_path)).convert("RGB").resize((512, 512))
        pixels = list(image.getdata())
        width, height = image.size

        # Luminance and saturation approximations for textured-coverage inference.
        luminance: list[int] = []
        saturation_like: list[float] = []
        for r, g, b in pixels:
            y = int((0.299 * r) + (0.587 * g) + (0.114 * b))
            luminance.append(y)
            mx = max(r, g, b)
            mn = min(r, g, b)
            sat = 0.0 if mx == 0 else (mx - mn) / mx
            saturation_like.append(sat)

        # Edge density from first-order gradients.
        edge_hits = 0
        total_checks = 0
        for row in range(height - 1):
            row_offset = row * width
            next_offset = (row + 1) * width
            for col in range(width - 1):
                idx = row_offset + col
                right = idx + 1
                down = next_offset + col
                gx = abs(luminance[idx] - luminance[right])
                gy = abs(luminance[idx] - luminance[down])
                grad = gx + gy
                if grad > 26:
                    edge_hits += 1
                total_checks += 1

        edge_density = (edge_hits / total_checks) if total_checks else 0.0
        mean_saturation = (sum(saturation_like) / len(saturation_like)) if saturation_like else 0.0

        # Map visual complexity into a conservative applied-surface factor.
        factor = 0.56 + (edge_density * 0.65) + (mean_saturation * 0.30)
        return max(0.62, min(0.95, factor))
    except Exception:
        return 0.74


def estimate_material_quantities(
    prompt: str,
    material_names: list[str],
    *,
    render_image_path: str | None = None,
) -> list[dict[str, Any]]:
    width, depth = parse_room_dimensions(prompt)
    height = _parse_room_height(prompt)
    profile = _room_profile(prompt)
    coverage = _coverage_profile(profile)
    floor_m2 = width * depth
    perimeter = 2.0 * (width + depth)
    walls_m2 = perimeter * height
    ceiling_m2 = floor_m2

    floor_ratio = float(coverage["floor_ratio"])
    walls_ratio = float(coverage["walls_ratio"])
    ceiling_ratio = float(coverage["ceiling_ratio"])
    detail_m2 = float(coverage["detail_m2"])
    waste_factor = float(coverage["waste_factor"])
    application_factor = _estimate_render_application_factor(render_image_path)

    # Approximation focused on actually clad areas, not full room skin coverage.
    base_textured_m2 = (floor_m2 * floor_ratio) + (walls_m2 * walls_ratio) + (ceiling_m2 * ceiling_ratio) + detail_m2
    total_textured_m2 = max(1.0, base_textured_m2 * waste_factor * application_factor)

    names = material_names[:2] if material_names else ["General"]
    weights = _distribution_weights(prompt, len(names))
    zones = [
        "Mobiliario y zonas focales",
        "Muros, revestimientos y paños principales",
    ]

    rows: list[dict[str, Any]] = []
    for idx, name in enumerate(names):
        weight = weights[idx] if idx < len(weights) else (1.0 / max(1, len(names)))
        m2_value = round(total_textured_m2 * weight, 2)
        brand = _material_brand(name)
        rate = _brand_rate_cop_per_m2(brand)
        subtotal = int(round(m2_value * rate))
        rows.append(
            {
                "material": name,
                "brand": brand,
                "zona": zones[idx] if idx < len(zones) else "Aplicacion mixta",
                "m2_estimados": m2_value,
                "price_cop_m2": rate,
                "subtotal_cop": subtotal,
            }
        )

    return rows


def project_total_m2(quantities: list[dict[str, Any]]) -> float:
    total = 0.0
    for row in quantities or []:
        try:
            total += float(row.get("m2_estimados") or 0)
        except Exception:
            continue
    return round(total, 2)


def summarize_brand_totals(quantities: list[dict[str, Any]]) -> dict[str, dict[str, float | int]]:
    summary: dict[str, dict[str, float | int]] = {}
    for row in quantities or []:
        brand = str(row.get("brand") or "general").strip().lower()
        m2_value = float(row.get("m2_estimados") or 0)
        subtotal = int(row.get("subtotal_cop") or 0)
        if brand not in summary:
            summary[brand] = {"m2_total": 0.0, "subtotal_cop": 0}
        summary[brand]["m2_total"] = round(float(summary[brand]["m2_total"]) + m2_value, 2)
        summary[brand]["subtotal_cop"] = int(summary[brand]["subtotal_cop"]) + subtotal
    return summary


def project_total_budget_cop(quantities: list[dict[str, Any]]) -> int:
    total = 0
    for row in quantities or []:
        total += int(row.get("subtotal_cop") or 0)
    return int(total)


def _find_logo_candidate() -> Path | None:
    root = Path(__file__).resolve().parents[3]
    candidates = [
        root / "backend" / "app" / "static" / "logo.png",
        root / "Logo" / "Logo.png",
        root / "Logo" / "logo.png",
        root / "Logo" / "Logo.jpg",
        root / "Logo" / "logo.jpg",
        root / "Logo" / "Logo.webp",
        root / "Logo" / "logo.webp",
    ]
    for path in candidates:
        if path.exists() and path.is_file():
            return path
    return None


def write_architectural_project_pdf(
    *,
    file_path: str,
    project_id: str,
    prompt: str,
    selected_materials: list[str],
    quantities: list[dict[str, Any]],
    render_image_path: str,
) -> str:
    target = Path(file_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfgen import canvas
    except Exception as exc:
        raise RuntimeError("No se pudo generar el PDF de diseño: falta reportlab en el entorno") from exc

    page_w, page_h = A4
    c = canvas.Canvas(str(target), pagesize=A4)

    def fmt_cop(value: int | float) -> str:
        amount = int(round(float(value or 0)))
        return f"$ {amount:,} COP".replace(",", ".")

    def fmt_cop_short(value: int | float) -> str:
        amount = int(round(float(value or 0)))
        return f"$ {amount:,}".replace(",", ".")

    def display_material_name(value: str) -> str:
        raw = str(value or "Material")
        if "/" in raw:
            raw = raw.split("/", 1)[1]
        return raw[:20]

    bg = colors.HexColor("#0f1115")
    panel = colors.HexColor("#171b21")
    accent = colors.HexColor("#22c55e")
    line = colors.HexColor("#26303d")
    text = colors.HexColor("#ecf2f8")
    muted = colors.HexColor("#aab6c6")

    c.setFillColor(bg)
    c.rect(0, 0, page_w, page_h, stroke=0, fill=1)

    margin = 34
    content_w = page_w - (margin * 2)

    # Header band
    c.setFillColor(panel)
    c.roundRect(margin, page_h - 128, content_w, 94, 10, stroke=0, fill=1)

    logo_path = _find_logo_candidate()
    if logo_path is not None:
        try:
            logo_img = ImageReader(str(logo_path))
            c.drawImage(logo_img, page_w - margin - 78, page_h - 116, width=54, height=54, preserveAspectRatio=True, mask="auto")
        except Exception:
            pass

    c.setFillColor(text)
    c.setFont("Helvetica-Bold", 17)
    c.drawString(margin + 18, page_h - 74, "IA-IMP · Proyecto Inteligente")
    c.setFillColor(muted)
    c.setFont("Helvetica", 10)
    c.drawString(margin + 18, page_h - 92, f"Proyecto ID: {project_id}")

    # Concept block
    c.setFillColor(panel)
    c.roundRect(margin, page_h - 236, content_w, 90, 10, stroke=0, fill=1)
    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin + 14, page_h - 162, "CONCEPTO DEL PROYECTO")
    c.setFillColor(text)
    c.setFont("Helvetica", 10)

    concept = str(prompt or "").strip() or "Sin descripción"
    words = concept.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if c.stringWidth(trial, "Helvetica", 10) <= (content_w - 28):
            current = trial
        else:
            lines.append(current)
            current = word
        if len(lines) >= 3:
            break
    if current and len(lines) < 3:
        lines.append(current)

    y = page_h - 180
    for ln in lines[:3]:
        c.drawString(margin + 14, y, ln)
        y -= 14

    # Render frame
    render_top = page_h - 255
    render_h = 240
    c.setFillColor(panel)
    c.roundRect(margin, render_top - render_h, content_w, render_h, 10, stroke=0, fill=1)
    c.setStrokeColor(line)
    c.roundRect(margin + 12, render_top - render_h + 12, content_w - 24, render_h - 24, 8, stroke=1, fill=0)
    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin + 18, render_top - 20, "RENDER GENERADO")

    render_path = Path(str(render_image_path or "").strip())
    if render_path.exists() and render_path.is_file():
        try:
            render_img = ImageReader(str(render_path))
            box_x = margin + 18
            box_y = render_top - render_h + 22
            box_w = content_w - 36
            box_h = render_h - 48
            c.drawImage(
                render_img,
                box_x,
                box_y,
                width=box_w,
                height=box_h,
                preserveAspectRatio=True,
                anchor="c",
                mask="auto",
            )
        except Exception:
            c.setFillColor(muted)
            c.setFont("Helvetica", 10)
            c.drawString(margin + 20, render_top - 46, "No se pudo incrustar la imagen del render.")
    else:
        c.setFillColor(muted)
        c.setFont("Helvetica", 10)
        c.drawString(margin + 20, render_top - 46, "Render no disponible")

    # Materials + quantities table
    table_y = render_top - render_h - 18
    table_h = 230
    c.setFillColor(panel)
    c.roundRect(margin, table_y - table_h, content_w, table_h, 10, stroke=0, fill=1)
    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin + 14, table_y - 20, "MATERIALES Y CANTIDADES ESTIMADAS")

    total_m2 = project_total_m2(quantities)
    total_budget = project_total_budget_cop(quantities)
    brand_totals = summarize_brand_totals(quantities)

    x_material = margin + 16
    x_brand = margin + 186
    x_m2 = margin + 360
    x_rate = margin + 450
    x_subtotal = margin + content_w - 18

    c.setFillColor(text)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x_material, table_y - 40, "Material")
    c.drawString(x_brand, table_y - 40, "Marca")
    c.drawRightString(x_m2, table_y - 40, "m²")
    c.drawRightString(x_rate, table_y - 40, "$/m²")
    c.drawRightString(x_subtotal, table_y - 40, "Subtotal")
    c.setStrokeColor(line)
    c.line(margin + 14, table_y - 45, margin + content_w - 14, table_y - 45)

    row_y = table_y - 62
    c.setFont("Helvetica", 9)
    if quantities:
        for row in quantities[:4]:
            material = display_material_name(str(row.get("material") or "Material"))
            brand = str(row.get("brand") or "general").upper()
            value = float(row.get("m2_estimados") or 0)
            price_m2 = int(row.get("price_cop_m2") or 0)
            subtotal = int(row.get("subtotal_cop") or 0)
            c.setFillColor(text)
            c.drawString(x_material, row_y, material)
            c.setFillColor(muted)
            c.drawString(x_brand, row_y, brand)
            c.setFillColor(text)
            c.drawRightString(x_m2, row_y, f"{value:.2f}")
            c.drawRightString(x_rate, row_y, fmt_cop_short(price_m2))
            c.drawRightString(x_subtotal, row_y, fmt_cop_short(subtotal))
            row_y -= 18
    else:
        c.setFillColor(muted)
        c.drawString(margin + 16, row_y, "Sin cantidades disponibles")
        row_y -= 18

    c.setStrokeColor(line)
    c.line(margin + 14, row_y - 2, margin + content_w - 14, row_y - 2)

    row_y -= 14
    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin + 16, row_y, "Totales por marca")
    row_y -= 14
    c.setFont("Helvetica", 9)
    c.setFillColor(text)
    for brand, values in brand_totals.items():
        brand_name = str(brand or "general").capitalize()
        brand_m2 = float(values.get("m2_total") or 0)
        brand_cop = int(values.get("subtotal_cop") or 0)
        c.drawString(margin + 16, row_y, f"Total de metros {brand_name}/Diseño")
        c.drawRightString(x_m2, row_y, f"{brand_m2:.2f} m²")
        c.drawRightString(x_subtotal, row_y, fmt_cop(brand_cop))
        row_y -= 14

    c.setStrokeColor(line)
    c.line(margin + 14, row_y - 2, margin + content_w - 14, row_y - 2)
    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin + 16, row_y - 18, "TOTAL ESTIMADO")
    c.drawRightString(x_m2, row_y - 18, f"{total_m2:.2f} m²")
    c.drawRightString(x_subtotal, row_y - 18, fmt_cop(total_budget))

    # Footer
    c.setFillColor(muted)
    c.setFont("Helvetica", 7.6)
    c.drawString(
        margin,
        24,
        "IMPORMADERAS vende laminas completas: Duratex 183 x 244 cm y Arauco 215 x 244 cm; esta estimacion en m2 es solo orientativa.",
    )
    c.drawString(
        margin,
        14,
        "La IA es una herramienta de apoyo: revisa siempre medidas, despieces y costos finales con criterio tecnico y comercial.",
    )

    c.showPage()
    c.save()
    return str(target)
