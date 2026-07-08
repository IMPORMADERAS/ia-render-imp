from .pricing_store import get_pricing_config, get_wompi_coverage_factor


def _pricing() -> dict:
    return get_pricing_config()


def _to_int_cop(value, fallback: int = 0) -> int:
    try:
        amount = int(round(float(value)))
    except (TypeError, ValueError):
        return int(fallback)
    return max(0, amount)


def _module_usd(key: str, fallback: float) -> float:
    pricing = _pricing()
    return float(pricing.get("module_usd", {}).get(key, fallback))


def _music_usd(duration_seconds: int) -> float:
    pricing = _pricing()
    durations = pricing.get("music_duration_usd", {})
    seconds = str(max(8, min(30, int(duration_seconds))))
    if seconds in durations:
        return float(durations[seconds])
    if int(seconds) <= 8:
        return 0.08
    if int(seconds) <= 15:
        return 0.15
    return 0.3


def _video_usd_per_second(model: str) -> float:
    pricing = _pricing()
    engines = pricing.get("video_engine_usd_per_second", {})
    return float(engines.get(model, engines.get("kwaivgi/kling-v3-video", 0.224)))


def _margin_multiplier() -> float:
    return float(_pricing().get("pricing_margin_multiplier", 1.5))


def _usd_to_cop_rate() -> float:
    return float(_pricing().get("usd_to_cop", 3602.817479))


def _wompi_coverage_multiplier() -> float:
    return get_wompi_coverage_factor(_pricing())


def usd_to_cop_with_margin(usd: float) -> float:
    return float(usd) * _margin_multiplier() * _wompi_coverage_multiplier() * _usd_to_cop_rate()


def to_psychological_cop(raw_cop: float) -> int:
    if raw_cop <= 0:
        return 0
    if raw_cop < 1000:
        return int(((raw_cop + 9) // 10) * 10)

    if raw_cop < 10000:
        step = 100
        ceiling = int(((raw_cop + (step - 1)) // step) * step)
        candidate = ceiling - 10
        return candidate if candidate >= raw_cop else ceiling + 90

    step = 1000
    ceiling = int(((raw_cop + (step - 1)) // step) * step)
    candidate = ceiling - 100
    return candidate if candidate >= raw_cop else ceiling + 900


def module_cost_img2img_cop() -> int:
    pricing = _pricing()
    module_prices = pricing.get("module_price_cop", {})
    if "img2img" in module_prices:
        return _to_int_cop(module_prices.get("img2img"))
    return to_psychological_cop(usd_to_cop_with_margin(_module_usd("img2img", 0.04)))


def module_cost_materials_cop() -> int:
    pricing = _pricing()
    module_prices = pricing.get("module_price_cop", {})
    if "materials" in module_prices:
        return _to_int_cop(module_prices.get("materials"))
    return to_psychological_cop(usd_to_cop_with_margin(_module_usd("materials", 0.039)))


def module_cost_text2img_cop() -> int:
    pricing = _pricing()
    module_prices = pricing.get("module_price_cop", {})
    if "text2img" in module_prices:
        return _to_int_cop(module_prices.get("text2img"))
    return to_psychological_cop(usd_to_cop_with_margin(_module_usd("text2img", 0.039)))


def module_cost_influencer_cop() -> int:
    pricing = _pricing()
    module_prices = pricing.get("module_price_cop", {})
    if "influencer" in module_prices:
        return _to_int_cop(module_prices.get("influencer"))
    return to_psychological_cop(usd_to_cop_with_margin(_module_usd("influencer", 0.9)))


def module_cost_music_cop(duration_seconds: int) -> int:
    pricing = _pricing()
    music_prices = pricing.get("music_duration_cop", {})
    seconds = str(max(8, min(30, int(duration_seconds))))
    if seconds in music_prices:
        return _to_int_cop(music_prices.get(seconds))
    return to_psychological_cop(usd_to_cop_with_margin(_music_usd(duration_seconds)))


def module_cost_i2v_cop(model: str, duration_seconds: int) -> int:
    pricing = _pricing()
    video_prices = pricing.get("video_price_cop", {})
    seconds = str(max(3, min(15, int(duration_seconds))))
    model_prices = video_prices.get(model, {}) if isinstance(video_prices, dict) else {}
    if isinstance(model_prices, dict) and seconds in model_prices:
        return _to_int_cop(model_prices.get(seconds))

    per_second = _video_usd_per_second(model)
    usd = per_second * int(seconds)
    return to_psychological_cop(usd_to_cop_with_margin(usd))


def module_cost_chat_cop() -> int:
    # Conservative fixed charge per chat request to keep ledger simple.
    pricing = _pricing()
    module_prices = pricing.get("module_price_cop", {})
    if "chat" in module_prices:
        return _to_int_cop(module_prices.get("chat"))
    return to_psychological_cop(usd_to_cop_with_margin(_module_usd("chat", 0.01)))


def module_cost_chat_image_cop() -> int:
    pricing = _pricing()
    module_prices = pricing.get("module_price_cop", {})
    if "chat_image" in module_prices:
        return _to_int_cop(module_prices.get("chat_image"))
    return to_psychological_cop(usd_to_cop_with_margin(_module_usd("chat_image", 0.04)))
