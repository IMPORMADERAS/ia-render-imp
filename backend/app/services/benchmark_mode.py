from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from ..config import settings


PNG_BG = "#103522"
PNG_FG = "#dfffe9"


def is_benchmark_mode_enabled() -> bool:
    return bool(settings.benchmark_mode_enabled)


def benchmark_duration_seconds() -> int:
    try:
        return max(1, int(settings.benchmark_job_duration_seconds))
    except (TypeError, ValueError):
        return 1


def write_placeholder_image(output_path: str, label: str) -> None:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1024, 1024), PNG_BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((48, 48, 976, 976), outline=PNG_FG, width=6)
    draw.text((84, 120), f"IA-IMP benchmark\n{label}", fill=PNG_FG)
    image.save(target, format="PNG")


def write_placeholder_binary(output_path: str, header: bytes, label: str) -> None:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = header + f"IA-IMP benchmark {label}".encode("utf-8")
    target.write_bytes(payload)
