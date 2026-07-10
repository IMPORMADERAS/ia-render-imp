import os
import tempfile
import urllib.request
from contextlib import ExitStack
from pathlib import Path
from threading import BoundedSemaphore
from time import perf_counter
from time import sleep
from typing import Optional

from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageStat

from ..config import settings

DEFAULT_IMG2IMG_MODEL = "black-forest-labs/flux-kontext-pro"
DEFAULT_MATERIALS_MODEL = "google/nano-banana"

class ArchitecturalRenderer:
    def __init__(self) -> None:
        self._pipeline = None
        max_concurrent = max(1, int(settings.replicate_max_concurrent_predictions))
        self._replicate_semaphore = BoundedSemaphore(max_concurrent)

    @staticmethod
    def _is_retryable_replicate_error(exc: Exception) -> bool:
        text = str(exc).lower()
        retry_patterns = [
            "status: 429",
            "request was throttled",
            "rate limit",
            "temporarily unavailable",
            "timeout",
            "connection",
            "director: unexpected error handling prediction",
        ]
        return any(pattern in text for pattern in retry_patterns)

    def _run_replicate(self, replicate_module, model: str, payload: dict) -> object:
        attempts = max(1, int(settings.replicate_retry_max_attempts))
        delay = max(0.4, float(settings.replicate_retry_initial_delay_seconds))
        last_error: Exception | None = None

        for attempt in range(1, attempts + 1):
            try:
                with self._replicate_semaphore:
                    return replicate_module.run(model, input=payload)
            except Exception as exc:
                last_error = exc
                if attempt >= attempts or not self._is_retryable_replicate_error(exc):
                    break
                sleep(delay)
                delay = min(delay * 2, 20.0)

        raise RuntimeError(f"Replicate fallo tras {attempts} intento(s): {last_error}")

    def _lazy_load_pipeline(self):
        if self._pipeline is not None:
            return self._pipeline

        try:
            import torch
            from diffusers import ControlNetModel, StableDiffusionXLControlNetImg2ImgPipeline

            dtype = torch.float16 if settings.use_gpu and torch.cuda.is_available() else torch.float32
            device = "cuda" if settings.use_gpu and torch.cuda.is_available() else "cpu"

            controlnet = ControlNetModel.from_pretrained(settings.controlnet_model_id, torch_dtype=dtype)
            pipe = StableDiffusionXLControlNetImg2ImgPipeline.from_pretrained(
                settings.hf_model_id,
                controlnet=controlnet,
                torch_dtype=dtype,
            )
            pipe = pipe.to(device)
            self._pipeline = pipe
            return self._pipeline
        except Exception:
            self._pipeline = "fallback"
            return self._pipeline

    def _prepare_control(self, image: Image.Image) -> Image.Image:
        edge = image.convert("RGB").filter(ImageFilter.FIND_EDGES)
        return edge

    def _safe_resize(self, image: Image.Image) -> Image.Image:
        w, h = image.size
        max_dim = max(w, h)
        if max_dim <= settings.max_image_size:
            return image

        ratio = settings.max_image_size / max_dim
        new_size = (int(w * ratio), int(h * ratio))
        return image.resize(new_size, Image.Resampling.LANCZOS)

    def _save_remote_output(self, output: object, output_image_path: str) -> None:
        target = Path(output_image_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        if hasattr(output, "read"):
            content = output.read()
            target.write_bytes(content)
            return

        if hasattr(output, "url"):
            remote_url = str(output.url)
            with urllib.request.urlopen(remote_url, timeout=120) as response:
                target.write_bytes(response.read())
            return

        remote_url = str(output)
        if remote_url.startswith("http://") or remote_url.startswith("https://"):
            with urllib.request.urlopen(remote_url, timeout=120) as response:
                target.write_bytes(response.read())
            return

        raise RuntimeError("No se pudo interpretar la salida remota del proveedor cloud")

    def _get_image_size_with_exif(self, image_path: str) -> tuple[int, int]:
        with Image.open(image_path) as raw:
            normalized = ImageOps.exif_transpose(raw)
            return normalized.size

    def _closest_aspect_ratio_token(self, width: int, height: int) -> str:
        ratio = max(0.0001, float(width) / float(height))
        candidates = {
            "1:1": 1.0,
            "4:3": 4 / 3,
            "3:4": 3 / 4,
            "3:2": 3 / 2,
            "2:3": 2 / 3,
            "16:9": 16 / 9,
            "9:16": 9 / 16,
            "21:9": 21 / 9,
            "9:21": 9 / 21,
        }
        return min(candidates.keys(), key=lambda key: abs(candidates[key] - ratio))

    def _material_palette_hint(self, material_paths: list[str]) -> str:
        hints: list[str] = []
        for raw_path in material_paths[:2]:
            name = Path(raw_path).stem.replace("-", " ").strip() or "material"
            try:
                with Image.open(raw_path) as img_raw:
                    img = ImageOps.exif_transpose(img_raw).convert("RGB")
                    img = img.resize((96, 96), Image.Resampling.BILINEAR)
                    palette = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=4).convert("RGB")
                    colors = palette.getcolors(maxcolors=96 * 96) or []
                    colors_sorted = sorted(colors, key=lambda item: item[0], reverse=True)
                    hexes: list[str] = []
                    for _, rgb in colors_sorted:
                        if not isinstance(rgb, tuple) or len(rgb) < 3:
                            continue
                        r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
                        hexes.append(f"#{r:02x}{g:02x}{b:02x}")
                        if len(hexes) >= 3:
                            break
                    if hexes:
                        hints.append(f"{name}: {', '.join(hexes)}")
                    else:
                        hints.append(name)
            except Exception:
                hints.append(name)
        return " | ".join(hints) if hints else ""

    def _photoreal_materials_polish(self, image_path: str, reference_image_path: str | None = None) -> None:
        target = Path(image_path)
        if not target.exists():
            return

        with Image.open(target) as raw:
            img = ImageOps.exif_transpose(raw).convert("RGB")

            if reference_image_path:
                ref_path = Path(reference_image_path)
                if ref_path.exists():
                    with Image.open(ref_path) as ref_raw:
                        ref = ImageOps.exif_transpose(ref_raw).convert("RGB").resize(img.size, Image.Resampling.LANCZOS)
                        gy, gcb, gcr = img.convert("YCbCr").split()
                        ry, _, _ = ref.convert("YCbCr").split()
                        blended_y = Image.blend(gy, ry, 0.58)
                        blended_y = ImageEnhance.Contrast(blended_y).enhance(1.06)
                        img = Image.merge("YCbCr", (blended_y, gcb, gcr)).convert("RGB")
                        # Recover natural scene response from the original capture
                        # while preserving edited materials from the generated image.
                        img = Image.blend(img, ref, 0.2)

            # Keep a subtle, realistic look: recover local contrast and crispness
            # without introducing artificial HDR or over-saturation.
            img = ImageOps.autocontrast(img, cutoff=0.6)
            img = ImageEnhance.Brightness(img).enhance(0.99)
            img = ImageEnhance.Contrast(img).enhance(1.08)
            img = ImageEnhance.Color(img).enhance(0.9)
            img = ImageEnhance.Sharpness(img).enhance(1.1)
            img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=2))

            # Adaptive gray-world normalization to reduce synthetic color cast.
            mean_r, mean_g, mean_b = ImageStat.Stat(img).mean[:3]
            target_mean = (mean_r + mean_g + mean_b) / 3.0
            fr = max(0.9, min(1.1, target_mean / max(1.0, mean_r)))
            fg = max(0.9, min(1.1, target_mean / max(1.0, mean_g)))
            fb = max(0.9, min(1.1, target_mean / max(1.0, mean_b)))

            r, g, b = img.split()
            r = r.point(lambda value: max(0, min(255, int(value * fr))))
            g = g.point(lambda value: max(0, min(255, int(value * fg))))
            b = b.point(lambda value: max(0, min(255, int(value * fb))))
            img = Image.merge("RGB", (r, g, b))

            img.save(target)

    def _realism_suffix(self, quality: str) -> str:
        base = (
            "Transform into a photorealistic architectural photograph. "
            "Use physically plausible materials, realistic global illumination, "
            "natural shadows, balanced exposure, real-world reflections, "
            "and subtle camera optics with clean dynamic range. "
            "Remove CAD/viewport look, remove flat color blocks, remove line-art appearance, "
            "and avoid stylized or illustrative rendering."
        )
        if quality == "ultra":
            return (
                f"{base} "
                "Prioritize high fidelity micro-details in textures, joints, edges, "
                "surface roughness variation, and true-to-life material depth."
            )
        if quality == "fast":
            return (
                f"{base} "
                "Keep the transformation realistic while preserving speed and stable geometry."
            )
        return (
            f"{base} "
            "Keep strong realism in materials and lighting while preserving architecture and framing."
        )

    def _enforce_reference_aspect_ratio(self, reference_image_path: str, generated_image_path: str) -> None:
        """Guarantee generated image keeps the same aspect ratio as reference image.

        IMPORTANT: this step is local-only (Pillow) to avoid triggering a second
        cloud generation/cost in Replicate for the same user request.
        """
        reference_path = Path(reference_image_path)
        generated_path = Path(generated_image_path)
        if not reference_path.exists() or not generated_path.exists():
            return

        with Image.open(reference_path) as ref_raw, Image.open(generated_path) as gen_raw:
            # Respect camera/phone EXIF orientation before comparing ratios.
            ref_img = ImageOps.exif_transpose(ref_raw)
            gen_img = ImageOps.exif_transpose(gen_raw)

            ref_w, ref_h = ref_img.size
            gen_w, gen_h = gen_img.size
            if ref_w <= 0 or ref_h <= 0 or gen_w <= 0 or gen_h <= 0:
                return

            target_ratio = ref_w / ref_h
            current_ratio = gen_w / gen_h

            # Ignore tiny floating-point deltas; keep file untouched.
            if abs(current_ratio - target_ratio) <= 0.005:
                return

            # Keep reference format (horizontal/vertical/square) without blurred side bars.
            corrected = ImageOps.fit(gen_img, (ref_w, ref_h), method=Image.Resampling.LANCZOS)
            corrected.save(generated_path)

    def _normalize_to_full_hd(self, reference_image_path: str, generated_image_path: str) -> None:
        """Upscale output to Full HD baseline while preserving reference aspect format."""
        reference_path = Path(reference_image_path)
        generated_path = Path(generated_image_path)
        if not reference_path.exists() or not generated_path.exists():
            return

        ref_w, ref_h = self._get_image_size_with_exif(str(reference_path))
        if ref_w <= 0 or ref_h <= 0:
            return

        target_short = 1080
        ref_ratio = float(ref_w) / float(ref_h)

        if abs(ref_ratio - 1.0) <= 0.02:
            target_w, target_h = target_short, target_short
        elif ref_ratio > 1.0:
            target_h = target_short
            target_w = int(round(target_h * ref_ratio))
        else:
            target_w = target_short
            target_h = int(round(target_w / ref_ratio))

        with Image.open(generated_path) as raw:
            output = ImageOps.exif_transpose(raw).convert("RGB")
            if output.width == target_w and output.height == target_h:
                return

            resized = output.resize((target_w, target_h), Image.Resampling.LANCZOS)
            resized.save(generated_path)

    def _generate_replicate(
        self,
        input_image_path: str,
        output_image_path: str,
        prompt: str,
        negative_prompt: str,
        steps: int,
        guidance_scale: float,
        quality: str,
        seed: Optional[int] = None,
        model_override: Optional[str] = None,
    ) -> dict[str, int | str]:
        started = perf_counter()

        if not settings.replicate_api_token:
            raise RuntimeError("Falta REPLICATE_API_TOKEN en backend/.env")

        os.environ["REPLICATE_API_TOKEN"] = settings.replicate_api_token

        import replicate

        ref_w, ref_h = self._get_image_size_with_exif(input_image_path)
        aspect_ratio_token = self._closest_aspect_ratio_token(ref_w, ref_h)

        with open(input_image_path, "rb") as image_file:
            if quality == "fast":
                run_steps = min(steps, 24)
            elif quality == "ultra":
                run_steps = max(steps, 50)
            else:
                run_steps = steps

            configured_model = str(model_override or settings.replicate_model or "").strip()
            model_id = (configured_model or DEFAULT_IMG2IMG_MODEL).lower()
            effective_model = configured_model or DEFAULT_IMG2IMG_MODEL
            boosted_prompt = f"{prompt} {self._realism_suffix(quality)}"

            if "flux-kontext" in model_id:
                output_format = "png" if quality == "ultra" else "jpg"
                prompt_upsampling = quality == "ultra"
                kontext_common = {
                    "prompt": boosted_prompt,
                    "aspect_ratio": aspect_ratio_token,
                    "output_format": output_format,
                    "prompt_upsampling": prompt_upsampling,
                    "safety_tolerance": 2,
                }
                if seed is not None:
                    kontext_common["seed"] = seed

                attempts = [
                    {**kontext_common, "input_image": image_file},
                    {"prompt": boosted_prompt, "input_image": image_file, "output_format": output_format},
                ]
            else:
                configured_field = settings.replicate_input_image_field.strip() or "input_image"
                common = {
                    "prompt": boosted_prompt,
                    "negative_prompt": negative_prompt,
                    "num_inference_steps": run_steps,
                    "guidance_scale": guidance_scale,
                }
                if seed is not None:
                    common["seed"] = seed

                attempts = [
                    {**common, configured_field: image_file},
                    {"prompt": boosted_prompt, "negative_prompt": negative_prompt, configured_field: image_file},
                    {**common, "input_image": image_file},
                    {**common, "image": image_file},
                    {"prompt": boosted_prompt, "input_image": image_file},
                    {"prompt": boosted_prompt, "image": image_file},
                ]

            last_error: Exception | None = None
            output: object | None = None

            for payload in attempts:
                image_file.seek(0)
                try:
                    output = self._run_replicate(replicate, effective_model, payload)
                    break
                except Exception as exc:
                    last_error = exc

            if output is None:
                raise RuntimeError(f"Replicate fallo: {last_error}")

            first_output = output
            if isinstance(output, list):
                if not output:
                    raise RuntimeError("Replicate no devolvio imagen")
                first_output = output[0]

            self._save_remote_output(first_output, output_image_path)

        duration = int(perf_counter() - started)
        return {"mode": "replicate", "duration_seconds": max(1, duration)}

    def _generate_replicate_text_to_image(
        self,
        output_image_path: str,
        prompt: str,
        negative_prompt: str,
        steps: int,
        guidance_scale: float,
        quality: str,
        seed: Optional[int] = None,
    ) -> dict[str, int | str]:
        started = perf_counter()

        if not settings.replicate_api_token:
            raise RuntimeError("Falta REPLICATE_API_TOKEN en backend/.env")

        os.environ["REPLICATE_API_TOKEN"] = settings.replicate_api_token

        import replicate

        primary_model = "google/nano-banana"
        fallback_model = "black-forest-labs/flux-schnell"
        used_model = primary_model

        temp_files: list[str] = []
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                Image.new("RGB", (1024, 1024), "white").save(tmp, format="PNG")
                temp_files.append(tmp.name)

            blank_reference = Path(temp_files[0])

            nano_payloads = [
                {
                    "prompt": (
                        f"{prompt} Keep exactly the same aspect ratio as the reference canvas. "
                        "Do not crop or pad the composition."
                    ),
                    "image_input": [blank_reference],
                    "aspect_ratio": "1:1",
                    "output_format": "png",
                    "prompt_upsampling": True,
                    "safety_tolerance": 2,
                },
                {
                    "prompt": (
                        f"{prompt} Keep exactly the same aspect ratio as the reference canvas. "
                        "Do not crop or pad the composition."
                    ),
                    "input_image": [blank_reference],
                    "aspect_ratio": "1:1",
                    "output_format": "png",
                    "prompt_upsampling": True,
                    "safety_tolerance": 2,
                },
            ]

            if quality == "fast":
                run_steps = 2
            elif quality == "ultra":
                run_steps = 4
            else:
                run_steps = 3

            requested_steps = max(1, min(4, int(steps)))
            run_steps = max(run_steps, requested_steps)

            flux_payloads = [
                {
                    "prompt": prompt,
                    "num_inference_steps": run_steps,
                    "output_format": "png",
                    "output_quality": 100,
                    "go_fast": quality == "fast",
                    "seed": seed,
                },
                {"prompt": prompt, "num_inference_steps": run_steps},
                {"prompt": prompt},
            ]

            if quality == "fast":
                flux_run_steps = 2
            elif quality == "ultra":
                flux_run_steps = 4
            else:
                flux_run_steps = 3

            flux_requested_steps = max(1, min(4, int(steps)))
            flux_run_steps = max(flux_run_steps, flux_requested_steps)

            last_error: Exception | None = None
            output: object | None = None

            for payload in nano_payloads:
                try:
                    output = self._run_replicate(replicate, primary_model, payload)
                    break
                except Exception as exc:
                    last_error = exc

            if output is None:
                for payload in flux_payloads:
                    clean_payload = dict(payload)
                    if clean_payload.get("seed") is None:
                        clean_payload.pop("seed", None)
                    clean_payload["num_inference_steps"] = flux_run_steps
                    try:
                        output = self._run_replicate(replicate, fallback_model, clean_payload)
                        used_model = fallback_model
                        break
                    except Exception as exc:
                        last_error = exc

            if output is None:
                raise RuntimeError(f"Replicate texto a imagen fallo: {last_error}")
        finally:
            for temp_path in temp_files:
                try:
                    Path(temp_path).unlink(missing_ok=True)
                except Exception:
                    pass

        first_output = output
        if isinstance(output, list):
            if not output:
                raise RuntimeError("Replicate no devolvio imagen")
            first_output = output[0]

        self._save_remote_output(first_output, output_image_path)

        duration = int(perf_counter() - started)
        return {"mode": used_model, "duration_seconds": max(1, duration)}

    def _generate_replicate_material_edit(
        self,
        input_image_path: str,
        material_paths: list[str],
        output_image_path: str,
        prompt: str,
        material_mode: str,
        material_plan: str,
        material_names: Optional[list[str]] = None,
        quality: str = "balanced",
        seed: Optional[int] = None,
    ) -> dict[str, int | str]:
        started = perf_counter()

        if not settings.replicate_api_token:
            raise RuntimeError("Falta REPLICATE_API_TOKEN en backend/.env")

        os.environ["REPLICATE_API_TOKEN"] = settings.replicate_api_token

        import replicate

        mode = (material_mode or "mix").strip().lower()
        if mode not in {"mix", "zones"}:
            mode = "mix"

        material_labels = [Path(path).stem for path in material_paths]
        declared_materials = [str(name).strip() for name in (material_names or []) if str(name).strip()]
        selected_label_source = declared_materials if declared_materials else material_labels
        base_prompt = prompt.strip()
        realism_suffix = self._realism_suffix(quality)

        selected_materials = ", ".join(selected_label_source) if selected_label_source else "selected references"
        palette_hint = self._material_palette_hint(material_paths)
        zone_text = material_plan.strip() if mode == "zones" else ""
        realism_guardrail = (
            "Output must look like a real architectural photograph of a built interior, "
            "with natural global illumination, realistic dynamic range, grounded contact shadows, "
            "physically plausible reflections, and subtle camera optics. "
            "Avoid CGI, flat shading, toon look, synthetic plastic appearance, and color cast contamination. "
            "Avoid green, cyan, or yellow dominant tint; keep neutral white balance and believable daylight colorimetry."
        )
        surface_scope = (
            "Apply selected materials only on carpentry/wood finish surfaces (cabinetry, wood cladding, shelves, and related wood trims). "
            "Keep glass, metals, refrigerators, floor terrazzo, tables, chairs, and white walls unchanged unless explicitly requested."
        )
        if mode == "mix":
            mode_directive = (
                "Blend all selected materials in a balanced and visible way across compatible carpentry surfaces. "
                "Do not collapse to a single material. If two materials are provided, both must remain clearly present."
            )
        else:
            mode_directive = (
                "Apply materials strictly by zones using the user's zone instructions. "
                "Respect zone boundaries and keep unmentioned zones unchanged."
            )

        material_prompt = (
            "Architectural material replacement from selected swatches. "
            f"Use ONLY these selected materials: {selected_materials}. "
            f"Palette hints from selected swatches: {palette_hint}. "
            "Do not invent extra colors or unselected finishes. "
            f"{mode_directive} "
            f"{surface_scope} "
            "Keep geometry, perspective, framing, and scene elements unchanged. "
            f"{('Zone instructions: ' + zone_text + '. ') if zone_text else ''}"
            f"User direction: {base_prompt}. {realism_suffix} {realism_guardrail}"
        )

        output: object | None = None
        used_model = DEFAULT_MATERIALS_MODEL
        last_error: Exception | None = None

        def prepare_input_path(path: str, temp_files: list[str]) -> str:
            suffix = Path(path).suffix.lower()
            if suffix != ".jfif":
                return path

            with Image.open(path) as img:
                converted = img.convert("RGB")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    converted.save(tmp, format="PNG")
                    temp_files.append(tmp.name)
                    return tmp.name

        temp_files: list[str] = []
        try:
            prepared_paths = [
                prepare_input_path(input_image_path, temp_files),
                *[prepare_input_path(path, temp_files) for path in material_paths],
            ]

            ref_w, ref_h = self._get_image_size_with_exif(prepared_paths[0])
            aspect_ratio_token = self._closest_aspect_ratio_token(ref_w, ref_h)
            capture_suffix = Path(prepared_paths[0]).suffix.lower()
            output_format = "png" if capture_suffix == ".png" else "jpg"

            with ExitStack() as stack:
                opened_inputs = [stack.enter_context(open(path, "rb")) for path in prepared_paths]

                base_payload = {
                    "prompt": (
                        f"{material_prompt} Keep exactly the same framing and scene coverage as reference image 1. "
                        "Do not crop, do not zoom, and do not remove scene elements from reference image 1."
                    ),
                    "aspect_ratio": aspect_ratio_token,
                    "output_format": output_format,
                }
                if seed is not None:
                    base_payload["seed"] = int(seed)

                payload_attempts = [
                    {**base_payload, "image_input": opened_inputs},
                    {**base_payload, "input_image": opened_inputs},
                    {**base_payload, "image_input": opened_inputs[0]},
                    {**base_payload, "input_image": opened_inputs[0]},
                ]

                for payload in payload_attempts:
                    try:
                        for handle in opened_inputs:
                            handle.seek(0)
                        output = self._run_replicate(replicate, DEFAULT_MATERIALS_MODEL, payload)
                        used_model = DEFAULT_MATERIALS_MODEL
                        break
                    except Exception as exc:
                        last_error = exc

            if output is None:
                raise RuntimeError(f"El modelo de materiales no devolvio salida: {last_error}")
        finally:
            for temp_path in temp_files:
                try:
                    Path(temp_path).unlink(missing_ok=True)
                except Exception:
                    pass

        first_output = output
        if isinstance(output, list):
            if not output:
                raise RuntimeError("Replicate no devolvio imagen")
            first_output = output[0]

        self._save_remote_output(first_output, output_image_path)
        flux_refine_prompt = (
            "Photoreal refinement pass while preserving the material replacement exactly as applied. "
            f"Keep ONLY selected materials visible: {selected_materials}. "
            "Do not change material identities, do not swap colors, and do not introduce unselected finishes. "
            "Keep geometry, composition, perspective, and object positions unchanged. "
            "Enhance only realism: natural interior lighting, believable reflections, lens response, depth, and texture micro-detail."
        )
        refined_output_path = str(
            Path(output_image_path).with_name(
                f"{Path(output_image_path).stem}-flux-refine{Path(output_image_path).suffix}"
            )
        )
        try:
            self._generate_replicate(
                input_image_path=output_image_path,
                output_image_path=refined_output_path,
                prompt=flux_refine_prompt,
                negative_prompt=(
                    "cartoon, cgi, viewport, flat shading, color cast, wrong material colors, "
                    "unselected materials, blurry, distorted geometry"
                ),
                steps=20 if quality == "fast" else 24 if quality == "balanced" else 32,
                guidance_scale=6.2 if quality != "ultra" else 6.8,
                quality="balanced" if quality == "fast" else quality,
                seed=seed,
                model_override=DEFAULT_IMG2IMG_MODEL,
            )
            Path(refined_output_path).replace(output_image_path)
        finally:
            try:
                Path(refined_output_path).unlink(missing_ok=True)
            except Exception:
                pass

        duration = int(perf_counter() - started)
        return {
            "mode": "replicate_materials_nano_flux",
            "duration_seconds": max(1, duration),
            "material_count": len(material_paths),
            "model": f"{used_model}+{DEFAULT_IMG2IMG_MODEL}",
            "output_format": output_format,
        }

    def _generate_local(
        self,
        input_image_path: str,
        output_image_path: str,
        prompt: str,
        negative_prompt: str,
        steps: int,
        guidance_scale: float,
        quality: str = "balanced",
        seed: Optional[int] = None,
    ) -> dict[str, int | str]:
        started = perf_counter()
        with Image.open(input_image_path) as source_raw:
            # Normalize orientation so local generation follows the visual input orientation.
            source = ImageOps.exif_transpose(source_raw).convert("RGB")
        source = self._safe_resize(source)

        pipeline = self._lazy_load_pipeline()
        if pipeline == "fallback":
            # Fallback visual enhancement when AI model is not available.
            boosted = source.filter(ImageFilter.DETAIL)
            boosted.save(output_image_path)
            duration = int(perf_counter() - started)
            return {"mode": "fallback", "duration_seconds": max(1, duration)}

        import torch

        generator = None
        if seed is not None:
            generator = torch.Generator(device=pipeline.device).manual_seed(seed)

        control_image = self._prepare_control(source)

        if quality == "fast":
            run_steps = min(steps, 24)
            run_guidance = min(guidance_scale, 7.0)
            run_strength = 0.58
        elif quality == "ultra":
            run_steps = max(steps, 50)
            run_guidance = max(5.8, min(guidance_scale, 8.0))
            run_strength = 0.48
        else:
            run_steps = steps
            run_guidance = guidance_scale
            run_strength = 0.65

        result = pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=source,
            control_image=control_image,
            strength=run_strength,
            num_inference_steps=run_steps,
            guidance_scale=run_guidance,
            generator=generator,
        )

        final = result.images[0]

        if quality == "ultra":
            # Small detail enhancement pass for better material crispness.
            final = final.filter(ImageFilter.DETAIL).filter(ImageFilter.SHARPEN)

        Path(output_image_path).parent.mkdir(parents=True, exist_ok=True)
        final.save(output_image_path)
        self._enforce_reference_aspect_ratio(input_image_path, output_image_path)
        self._normalize_to_full_hd(input_image_path, output_image_path)
        duration = int(perf_counter() - started)
        return {"mode": "ai", "duration_seconds": max(1, duration)}

    def generate(
        self,
        input_image_path: str,
        output_image_path: str,
        prompt: str,
        negative_prompt: str,
        steps: int,
        guidance_scale: float,
        quality: str = "balanced",
        seed: Optional[int] = None,
        model_override: Optional[str] = None,
    ) -> dict[str, int | str]:
        provider = settings.render_provider.lower().strip()
        if provider == "replicate":
            try:
                return self._generate_replicate(
                    input_image_path=input_image_path,
                    output_image_path=output_image_path,
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    steps=steps,
                    guidance_scale=guidance_scale,
                    quality=quality,
                    seed=seed,
                    model_override=model_override,
                )
            except Exception as exc:
                if not settings.fallback_to_local_on_cloud_error:
                    raise RuntimeError(f"Replicate fallo (modo estricto, sin fallback local): {exc}") from exc

                local_meta = self._generate_local(
                    input_image_path=input_image_path,
                    output_image_path=output_image_path,
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    steps=steps,
                    guidance_scale=guidance_scale,
                    quality=quality,
                    seed=seed,
                )
                local_meta["mode"] = "fallback_local_after_cloud_error"
                local_meta["warning"] = f"Replicate fallo y se uso local automaticamente: {exc}"
                return local_meta

        return self._generate_local(
            input_image_path=input_image_path,
            output_image_path=output_image_path,
            prompt=prompt,
            negative_prompt=negative_prompt,
            steps=steps,
            guidance_scale=guidance_scale,
            quality=quality,
            seed=seed,
        )

    def generate_text_to_image(
        self,
        output_image_path: str,
        prompt: str,
        negative_prompt: str,
        steps: int,
        guidance_scale: float,
        quality: str = "balanced",
        seed: Optional[int] = None,
    ) -> dict[str, int | str]:
        provider = settings.render_provider.lower().strip()
        if provider != "replicate":
            raise RuntimeError("Texto a imagen requiere RENDER_PROVIDER=replicate")

        return self._generate_replicate_text_to_image(
            output_image_path=output_image_path,
            prompt=prompt,
            negative_prompt=negative_prompt,
            steps=steps,
            guidance_scale=guidance_scale,
            quality=quality,
            seed=seed,
        )

    def generate_material_edit(
        self,
        input_image_path: str,
        material_paths: list[str],
        output_image_path: str,
        prompt: str,
        material_mode: str,
        material_plan: str,
        material_names: Optional[list[str]] = None,
        quality: str = "balanced",
        seed: Optional[int] = None,
    ) -> dict[str, int | str]:
        provider = settings.render_provider.lower().strip()
        if provider != "replicate":
            raise RuntimeError("Edicion con materiales requiere RENDER_PROVIDER=replicate")

        return self._generate_replicate_material_edit(
            input_image_path=input_image_path,
            material_paths=material_paths,
            output_image_path=output_image_path,
            prompt=prompt,
            material_mode=material_mode,
            material_plan=material_plan,
            material_names=material_names,
            quality=quality,
            seed=seed,
        )


renderer = ArchitecturalRenderer()
