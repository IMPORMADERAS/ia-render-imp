from .styles import STYLE_PROMPTS


LIGHTING_PROMPTS = {
    "morning": "soft morning sunlight, fresh daylight, gentle shadows",
    "afternoon": "balanced afternoon daylight, bright neutral exposure, clear details",
    "night": "night scene with realistic artificial lighting, visible details in shadows, controlled highlights",
}


def build_arch_prompt(base_prompt: str, style: str, lighting_mode: str = "afternoon") -> str:
    style_text = STYLE_PROMPTS.get(style, STYLE_PROMPTS["editorial"])
    lighting_text = LIGHTING_PROMPTS.get(lighting_mode, LIGHTING_PROMPTS["afternoon"])
    return (
        "ultra realistic architectural visualization converted into real photo look, physically based rendering, "
        "global illumination, path-traced look, architectural photography composition, "
        "well-exposed image, soft ambient bounce light, "
        "high dynamic range, detailed materials, realistic shadows without underexposure, "
        "remove viewport/cad style, remove technical line-art look, remove flat shaded surfaces, "
        "remove schematic appearance, remove drawing-like outlines, "
        "produce a believable built-space photograph with natural depth and camera optics, "
        f"{lighting_text}, {style_text}, {base_prompt}"
    )


def sanitize_negative_prompt(negative_prompt: str) -> str:
    blocked = {
        "photorealistic",
        "photo realistic",
        "realistic",
        "ultra realistic",
        "high quality",
        "4k",
    }
    terms = [part.strip() for part in negative_prompt.split(",") if part.strip()]
    cleaned = [term for term in terms if term.lower() not in blocked]

    if not cleaned:
        return "low quality, blurry, distorted geometry, cartoon, watermark, text artifacts"
    return ", ".join(cleaned)
