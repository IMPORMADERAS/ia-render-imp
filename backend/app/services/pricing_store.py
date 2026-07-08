from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from ..config import settings

PRICING_PATH = Path(settings.data_dir) / "pricing.json"

DEFAULT_PRICING: dict[str, Any] = {
    "usd_to_cop": 3602.817479,
    "pricing_margin_multiplier": 1.5,
    "wompi_percent": 0.0265,
    "wompi_fixed_fee": 700,
    "wompi_iva_rate": 0.19,
    "recharge_plans": [5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000],
    "module_usd": {
        "img2img": 0.04,
        "materials": 0.039,
        "text2img": 0.039,
        "influencer": 0.9,
        "chat": 0.01,
        "chat_image": 0.04,
    },
    "module_price_cop": {
        "chat_image": 250,
    },
    "music_duration_usd": {
        "8": 0.08,
        "15": 0.15,
        "30": 0.3,
    },
    "music_duration_cop": {},
    "video_engine_usd_per_second": {
        "kwaivgi/kling-v3-video": 0.224,
        "wan-video/wan-2.2-i2v-fast": 0.022,
        "wan-video/wan-2.5-i2v-fast": 0.068,
        "minimax/video-01-live": 0.1,
    },
    "video_price_cop": {},
    "display": {
        "img2img": "Imagen a Imagen (FLUX Kontext Pro)",
        "materials": "Materiales IA (Nano Banana)",
        "text2img": "Texto a Imagen (Nano Banana)",
        "influencer": "Influencer (p-video-animate 1080p, hasta 15s)",
        "music": "Musica IA (Music 2.6)",
        "chat": "Pachy IA (GPT-4o)",
        "chat_image": "Pachy IA (Imagen)",
    },
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_pricing_config() -> dict[str, Any]:
    if not PRICING_PATH.exists():
        return deepcopy(DEFAULT_PRICING)

    try:
        raw = json.loads(PRICING_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return deepcopy(DEFAULT_PRICING)
    except Exception:
        return deepcopy(DEFAULT_PRICING)

    return _deep_merge(DEFAULT_PRICING, raw)


def save_pricing_config(config: dict[str, Any]) -> dict[str, Any]:
    normalized = _deep_merge(DEFAULT_PRICING, config if isinstance(config, dict) else {})
    PRICING_PATH.parent.mkdir(parents=True, exist_ok=True)
    PRICING_PATH.write_text(json.dumps(normalized, indent=2, ensure_ascii=False), encoding="utf-8")
    return normalized


def get_pricing_config() -> dict[str, Any]:
    return load_pricing_config()


def get_wompi_coverage_factor(config: dict[str, Any] | None = None) -> float:
    pricing = config or get_pricing_config()
    plans = [int(value) for value in pricing.get("recharge_plans", []) if int(value) > 0]
    if not plans:
        plans = deepcopy(DEFAULT_PRICING["recharge_plans"])
    percent = float(pricing.get("wompi_percent", DEFAULT_PRICING["wompi_percent"]))
    fixed_fee = float(pricing.get("wompi_fixed_fee", DEFAULT_PRICING["wompi_fixed_fee"]))
    iva_rate = float(pricing.get("wompi_iva_rate", DEFAULT_PRICING["wompi_iva_rate"]))

    factor_sum = 0.0
    for amount in plans:
        fee = amount * percent + fixed_fee
        fee_with_iva = fee * (1 + iva_rate)
        net = amount - fee_with_iva
        factor_sum += amount / net if net > 0 else 1.0
    return factor_sum / len(plans)
