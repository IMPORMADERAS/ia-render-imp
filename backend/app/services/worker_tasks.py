from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ..config import settings
from .admission_control import release_generation_slot
from .animator import animator
from .auth_wallet import credit_balance
from .benchmark_mode import benchmark_duration_seconds, is_benchmark_mode_enabled, write_placeholder_binary, write_placeholder_image
from .metrics import record_job_outcome
from .music_generator import music_generator
from .object_storage import guess_media_type, is_object_storage_enabled, upload_file
from .prompt_builder import build_arch_prompt, sanitize_negative_prompt
from .renderer import renderer
from .storage import update_anim, update_job, update_music


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _upload_asset_if_enabled(local_path: str, storage_key: str) -> dict[str, str] | None:
    if not is_object_storage_enabled():
        return None
    try:
        return upload_file(local_path, storage_key, media_type=guess_media_type(local_path))
    except Exception:
        return None


def run_render_job(
    *,
    job_id: str,
    user_id: int,
    billed_amount: int,
    input_image_path: str,
    output_image_path: str,
    prompt: str,
    negative_prompt: str,
    style: str,
    lighting_mode: str,
    quality: str,
    steps: int,
    guidance_scale: float,
    seed: int | None,
) -> None:
    try:
        if is_benchmark_mode_enabled():
            write_placeholder_image(output_image_path, "render")
            duration = benchmark_duration_seconds()
            remote_asset = _upload_asset_if_enabled(output_image_path, f"jobs/{job_id}{Path(output_image_path).suffix or '.png'}")
            update_job(
                job_id,
                {
                    "status": "completed",
                    "output_image": output_image_path,
                    "progress": 100,
                    "stage": "Benchmark completado",
                    "eta_seconds": 0,
                    "elapsed_seconds": duration,
                    "expected_total_seconds": duration,
                    "model_mode": "benchmark",
                    "warning": "Resultado sintetico de benchmark mode",
                    "output_storage_key": (remote_asset or {}).get("storage_key"),
                    "output_storage_url": (remote_asset or {}).get("url"),
                    "completed_at": _utc_now_iso(),
                    "updated_at": _utc_now_iso(),
                },
            )
            record_job_outcome("render", "completed", duration)
            return

        provider = settings.render_provider.lower().strip()
        base_eta = max(20, int(steps * 1.4))
        if provider == "replicate":
            base_eta = max(45, int(steps * 2.0))

        started_at = _utc_now_iso()
        update_job(
            job_id,
            {
                "status": "processing",
                "progress": 15,
                "stage": "Preparando render",
                "eta_seconds": base_eta,
                "expected_total_seconds": base_eta,
                "started_at": started_at,
                "updated_at": _utc_now_iso(),
            },
        )

        full_prompt = build_arch_prompt(prompt, style, lighting_mode)
        cleaned_negative_prompt = sanitize_negative_prompt(negative_prompt)
        update_job(
            job_id,
            {
                "progress": 55,
                "stage": f"Renderizando en {provider} ({quality})",
                "updated_at": _utc_now_iso(),
            },
        )

        render_meta = renderer.generate(
            input_image_path=input_image_path,
            output_image_path=output_image_path,
            prompt=full_prompt,
            negative_prompt=cleaned_negative_prompt,
            steps=steps,
            guidance_scale=guidance_scale,
            quality=quality,
            seed=seed,
            model_override="black-forest-labs/flux-kontext-pro",
        )

        duration = int(render_meta.get("duration_seconds", 1))
        mode = str(render_meta.get("mode", "fallback"))
        warning = render_meta.get("warning")
        stage = "Completado"
        if warning:
            stage = "Completado con fallback local"

        remote_asset = _upload_asset_if_enabled(output_image_path, f"jobs/{job_id}{Path(output_image_path).suffix or '.png'}")

        update_job(
            job_id,
            {
                "status": "completed",
                "output_image": output_image_path,
                "progress": 100,
                "stage": stage,
                "eta_seconds": 0,
                "elapsed_seconds": duration,
                "expected_total_seconds": duration,
                "model_mode": mode,
                "warning": warning,
                "output_storage_key": (remote_asset or {}).get("storage_key"),
                "output_storage_url": (remote_asset or {}).get("url"),
                "completed_at": _utc_now_iso(),
                "updated_at": _utc_now_iso(),
            },
        )
        record_job_outcome("render", "completed", duration)
    except Exception as exc:
        try:
            credit_balance(int(user_id), int(billed_amount), "img2img_refund", f"Reembolso por fallo job {job_id}")
        except Exception:
            pass
        update_job(
            job_id,
            {
                "status": "failed",
                "error": str(exc),
                "stage": "Fallo en render",
                "eta_seconds": None,
                "updated_at": _utc_now_iso(),
            },
        )
        record_job_outcome("render", "failed", 0)
    finally:
        release_generation_slot("render", int(user_id))


def run_text_render_job(
    *,
    job_id: str,
    user_id: int,
    billed_amount: int,
    output_image_path: str,
    prompt: str,
    negative_prompt: str,
    style: str,
    lighting_mode: str,
    quality: str,
    steps: int,
    guidance_scale: float,
    seed: int | None,
) -> None:
    try:
        if is_benchmark_mode_enabled():
            write_placeholder_image(output_image_path, "text2img")
            duration = benchmark_duration_seconds()
            remote_asset = _upload_asset_if_enabled(output_image_path, f"jobs/{job_id}{Path(output_image_path).suffix or '.png'}")
            update_job(
                job_id,
                {
                    "status": "completed",
                    "output_image": output_image_path,
                    "progress": 100,
                    "stage": "Benchmark completado",
                    "eta_seconds": 0,
                    "elapsed_seconds": duration,
                    "expected_total_seconds": duration,
                    "model_mode": "benchmark",
                    "warning": "Resultado sintetico de benchmark mode",
                    "output_storage_key": (remote_asset or {}).get("storage_key"),
                    "output_storage_url": (remote_asset or {}).get("url"),
                    "completed_at": _utc_now_iso(),
                    "updated_at": _utc_now_iso(),
                },
            )
            record_job_outcome("render", "completed", duration)
            return

        started_at = _utc_now_iso()
        base_eta = max(35, int(steps * 1.8))
        update_job(
            job_id,
            {
                "status": "processing",
                "progress": 15,
                "stage": "Preparando texto a imagen",
                "eta_seconds": base_eta,
                "expected_total_seconds": base_eta,
                "started_at": started_at,
                "updated_at": _utc_now_iso(),
            },
        )

        full_prompt = build_arch_prompt(prompt, style, lighting_mode)
        cleaned_negative_prompt = sanitize_negative_prompt(negative_prompt)
        update_job(
            job_id,
            {
                "progress": 55,
                "stage": f"Generando imagen desde texto ({quality})",
                "updated_at": _utc_now_iso(),
            },
        )

        render_meta = renderer.generate_text_to_image(
            output_image_path=output_image_path,
            prompt=full_prompt,
            negative_prompt=cleaned_negative_prompt,
            steps=steps,
            guidance_scale=guidance_scale,
            quality=quality,
            seed=seed,
        )

        duration = int(render_meta.get("duration_seconds", 1))
        mode = str(render_meta.get("mode", "replicate_text"))
        remote_asset = _upload_asset_if_enabled(output_image_path, f"jobs/{job_id}{Path(output_image_path).suffix or '.png'}")

        update_job(
            job_id,
            {
                "status": "completed",
                "output_image": output_image_path,
                "progress": 100,
                "stage": "Completado",
                "eta_seconds": 0,
                "elapsed_seconds": duration,
                "expected_total_seconds": duration,
                "model_mode": mode,
                "warning": None,
                "output_storage_key": (remote_asset or {}).get("storage_key"),
                "output_storage_url": (remote_asset or {}).get("url"),
                "completed_at": _utc_now_iso(),
                "updated_at": _utc_now_iso(),
            },
        )
        record_job_outcome("render", "completed", duration)
    except Exception as exc:
        try:
            credit_balance(int(user_id), int(billed_amount), "text2img_refund", f"Reembolso por fallo job {job_id}")
        except Exception:
            pass
        update_job(
            job_id,
            {
                "status": "failed",
                "error": str(exc),
                "stage": "Fallo en texto a imagen",
                "eta_seconds": None,
                "updated_at": _utc_now_iso(),
            },
        )
        record_job_outcome("render", "failed", 0)
    finally:
        release_generation_slot("render", int(user_id))


def run_material_render_job(
    *,
    job_id: str,
    user_id: int,
    billed_amount: int,
    input_image_path: str,
    output_image_path: str,
    prompt: str,
    style: str,
    lighting_mode: str,
    quality: str,
    material_mode: str,
    material_plan: str,
    material_names: list[str],
    material_paths: list[str],
    seed: int | None,
) -> None:
    try:
        if is_benchmark_mode_enabled():
            write_placeholder_image(output_image_path, "materials")
            duration = benchmark_duration_seconds()
            remote_asset = _upload_asset_if_enabled(output_image_path, f"jobs/{job_id}{Path(output_image_path).suffix or '.png'}")
            update_job(
                job_id,
                {
                    "status": "completed",
                    "output_image": output_image_path,
                    "progress": 100,
                    "stage": "Benchmark completado",
                    "eta_seconds": 0,
                    "elapsed_seconds": duration,
                    "expected_total_seconds": duration,
                    "model_mode": "benchmark",
                    "warning": "Resultado sintetico de benchmark mode",
                    "output_storage_key": (remote_asset or {}).get("storage_key"),
                    "output_storage_url": (remote_asset or {}).get("url"),
                    "completed_at": _utc_now_iso(),
                    "updated_at": _utc_now_iso(),
                },
            )
            record_job_outcome("render", "completed", duration)
            return

        started_at = _utc_now_iso()
        base_eta = 70 if quality == "ultra" else 55
        update_job(
            job_id,
            {
                "status": "processing",
                "progress": 15,
                "stage": "Preparando materiales",
                "eta_seconds": base_eta,
                "expected_total_seconds": base_eta,
                "started_at": started_at,
                "updated_at": _utc_now_iso(),
            },
        )

        full_prompt = build_arch_prompt(prompt, style, lighting_mode)
        if material_mode == "mix":
            full_prompt = (
                f"{full_prompt}. Usa los materiales de referencia para una mezcla equilibrada y realista en superficies arquitectonicas. "
                "No alteres geometria, perspectiva ni composicion del modelado. "
                "El resultado final debe verse como una fotografia arquitectonica real de un espacio construido, "
                "no como render CGI, viewport, ilustracion ni visualizacion conceptual."
            )
        else:
            plan_text = material_plan.strip() or "Distribuye los materiales en zonas coherentes sin alterar la estructura principal"
            full_prompt = (
                f"{full_prompt}. Aplica materiales por zonas segun esta instruccion: {plan_text}. "
                "Conserva geometria, escala y encuadre original. "
                "El resultado final debe verse como una fotografia arquitectonica real de un espacio construido, "
                "no como render CGI, viewport, ilustracion ni visualizacion conceptual."
            )

        update_job(
            job_id,
            {
                "progress": 55,
                "stage": f"Aplicando {len(material_names)} materiales ({material_mode})",
                "updated_at": _utc_now_iso(),
            },
        )

        render_meta = renderer.generate_material_edit(
            input_image_path=input_image_path,
            material_paths=material_paths,
            output_image_path=output_image_path,
            prompt=full_prompt,
            material_mode=material_mode,
            material_plan=material_plan,
            material_names=material_names,
            quality=quality,
            seed=seed,
        )

        duration = int(render_meta.get("duration_seconds", 1))
        remote_asset = _upload_asset_if_enabled(output_image_path, f"jobs/{job_id}{Path(output_image_path).suffix or '.png'}")
        update_job(
            job_id,
            {
                "status": "completed",
                "output_image": output_image_path,
                "progress": 100,
                "stage": "Completado",
                "eta_seconds": 0,
                "elapsed_seconds": duration,
                "expected_total_seconds": duration,
                "model_mode": str(render_meta.get("mode", "replicate_materials")),
                "warning": None,
                "output_storage_key": (remote_asset or {}).get("storage_key"),
                "output_storage_url": (remote_asset or {}).get("url"),
                "completed_at": _utc_now_iso(),
                "updated_at": _utc_now_iso(),
            },
        )
        record_job_outcome("render", "completed", duration)
    except Exception as exc:
        try:
            credit_balance(int(user_id), int(billed_amount), "materials_refund", f"Reembolso por fallo job {job_id}")
        except Exception:
            pass
        update_job(
            job_id,
            {
                "status": "failed",
                "error": str(exc),
                "stage": "Fallo en materiales",
                "eta_seconds": None,
                "updated_at": _utc_now_iso(),
            },
        )
        record_job_outcome("render", "failed", 0)
    finally:
        release_generation_slot("render", int(user_id))


def run_animation_job(
    *,
    anim_id: str,
    user_id: int,
    billed_amount: int,
    image_path: str,
    output_video_path: str,
    prompt: str,
    model: str,
    duration_seconds: int,
) -> None:
    try:
        if is_benchmark_mode_enabled():
            write_placeholder_binary(output_video_path, b"\x00\x00\x00\x18ftypmp42", "video")
            duration = benchmark_duration_seconds()
            remote_asset = _upload_asset_if_enabled(output_video_path, f"videos/{anim_id}{Path(output_video_path).suffix or '.mp4'}")
            update_anim(
                anim_id,
                {
                    "status": "completed",
                    "video_output": output_video_path,
                    "progress": 100,
                    "stage": "Benchmark completado",
                    "video_storage_key": (remote_asset or {}).get("storage_key"),
                    "video_storage_url": (remote_asset or {}).get("url"),
                    "completed_at": _utc_now_iso(),
                    "updated_at": _utc_now_iso(),
                },
            )
            record_job_outcome("video", "completed", duration)
            return

        update_anim(
            anim_id,
            {
                "status": "processing",
                "stage": "Generando video",
                "progress": 15,
                "started_at": _utc_now_iso(),
                "updated_at": _utc_now_iso(),
            },
        )

        result = animator.animate_replicate(
            image_path=image_path,
            output_video_path=output_video_path,
            prompt=prompt,
            model=model,
            duration_seconds=duration_seconds,
        )

        duration = result.get("duration_seconds", 1)
        remote_asset = _upload_asset_if_enabled(output_video_path, f"videos/{anim_id}{Path(output_video_path).suffix or '.mp4'}")
        update_anim(
            anim_id,
            {
                "status": "completed",
                "video_output": output_video_path,
                "progress": 100,
                "stage": f"Video listo ({duration}s, clip {duration_seconds}s)",
                "video_storage_key": (remote_asset or {}).get("storage_key"),
                "video_storage_url": (remote_asset or {}).get("url"),
                "completed_at": _utc_now_iso(),
                "updated_at": _utc_now_iso(),
            },
        )
        record_job_outcome("video", "completed", duration)
    except Exception as exc:
        try:
            credit_balance(int(user_id), int(billed_amount), "img2vid_refund", f"Reembolso por fallo anim {anim_id}")
        except Exception:
            pass
        update_anim(
            anim_id,
            {
                "status": "failed",
                "error": str(exc),
                "stage": "Fallo en animacion",
                "updated_at": _utc_now_iso(),
            },
        )
        record_job_outcome("video", "failed", 0)
    finally:
        release_generation_slot("video", int(user_id))


def run_music_job(
    *,
    music_id: str,
    user_id: int,
    billed_amount: int,
    output_audio_path: str,
    mode: str,
    genre: str,
    mood: str,
    instruments: str,
    user_taste: str,
    duration_seconds: int,
    bpm: int | None,
    language: str,
    theme: str,
    custom_lyrics: str,
    seed: int | None,
) -> None:
    try:
        if is_benchmark_mode_enabled():
            write_placeholder_binary(output_audio_path, b"ID3", "music")
            elapsed = benchmark_duration_seconds()
            remote_asset = _upload_asset_if_enabled(output_audio_path, f"music/{music_id}{Path(output_audio_path).suffix or '.mp3'}")
            update_music(
                music_id,
                {
                    "status": "completed",
                    "audio_output": output_audio_path,
                    "progress": 100,
                    "stage": f"Benchmark completado ({elapsed}s)",
                    "model": "benchmark",
                    "audio_storage_key": (remote_asset or {}).get("storage_key"),
                    "audio_storage_url": (remote_asset or {}).get("url"),
                    "completed_at": _utc_now_iso(),
                    "updated_at": _utc_now_iso(),
                },
            )
            record_job_outcome("music", "completed", elapsed)
            return

        update_music(
            music_id,
            {
                "status": "processing",
                "stage": "Generando audio",
                "progress": 20,
                "started_at": _utc_now_iso(),
                "updated_at": _utc_now_iso(),
            },
        )

        result = music_generator.generate_replicate(
            output_audio_path=output_audio_path,
            mode=mode,
            genre=genre,
            mood=mood,
            instruments=instruments,
            user_taste=user_taste,
            duration_seconds=duration_seconds,
            bpm=bpm,
            language=language,
            theme=theme,
            custom_lyrics=custom_lyrics,
            seed=seed,
        )

        elapsed = int(result.get("duration_seconds", 1))
        remote_asset = _upload_asset_if_enabled(output_audio_path, f"music/{music_id}{Path(output_audio_path).suffix or '.mp3'}")
        update_music(
            music_id,
            {
                "status": "completed",
                "audio_output": output_audio_path,
                "progress": 100,
                "stage": f"Audio listo ({elapsed}s)",
                "model": str(result.get("model", "")),
                "audio_storage_key": (remote_asset or {}).get("storage_key"),
                "audio_storage_url": (remote_asset or {}).get("url"),
                "completed_at": _utc_now_iso(),
                "updated_at": _utc_now_iso(),
            },
        )
        record_job_outcome("music", "completed", elapsed)
    except Exception as exc:
        try:
            credit_balance(int(user_id), int(billed_amount), "music_refund", f"Reembolso por fallo musica {music_id}")
        except Exception:
            pass
        update_music(
            music_id,
            {
                "status": "failed",
                "error": str(exc),
                "stage": "Fallo en generacion musical",
                "updated_at": _utc_now_iso(),
            },
        )
        record_job_outcome("music", "failed", 0)
    finally:
        release_generation_slot("music", int(user_id))


def run_influencer_job(
    *,
    influencer_id: str,
    user_id: int,
    billed_amount: int,
    source_video_path: str,
    reference_image_path: str,
    output_video_path: str,
    instruction_prompt: str,
    resolution: str,
    target_fps: str,
    turbo: bool,
) -> None:
    try:
        if is_benchmark_mode_enabled():
            write_placeholder_binary(output_video_path, b"\x00\x00\x00\x18ftypmp42", "influencer")
            duration = benchmark_duration_seconds()
            remote_asset = _upload_asset_if_enabled(output_video_path, f"influencer/{influencer_id}{Path(output_video_path).suffix or '.mp4'}")
            update_anim(
                influencer_id,
                {
                    "status": "completed",
                    "stage": "Benchmark completado",
                    "progress": 100,
                    "video_output": output_video_path,
                    "video_storage_key": (remote_asset or {}).get("storage_key"),
                    "video_storage_url": (remote_asset or {}).get("url"),
                    "model": "benchmark",
                    "duration_seconds": duration,
                    "completed_at": _utc_now_iso(),
                    "updated_at": _utc_now_iso(),
                },
            )
            record_job_outcome("influencer", "completed", duration)
            return

        update_anim(
            influencer_id,
            {
                "status": "processing",
                "stage": "Procesando expresion y lip-sync (realismo estricto)",
                "progress": 15,
                "started_at": _utc_now_iso(),
                "updated_at": _utc_now_iso(),
            },
        )

        result = animator.animate_influencer_replicate(
            source_video_path=source_video_path,
            reference_image_path=reference_image_path,
            output_video_path=output_video_path,
            instruction_prompt=instruction_prompt,
            resolution=resolution,
            target_fps=target_fps,
            turbo=bool(turbo),
        )

        remote_asset = _upload_asset_if_enabled(output_video_path, f"influencer/{influencer_id}{Path(output_video_path).suffix or '.mp4'}")

        update_anim(
            influencer_id,
            {
                "status": "completed",
                "stage": "Video influencer listo (realismo estricto)",
                "progress": 100,
                "video_output": output_video_path,
            "video_storage_key": (remote_asset or {}).get("storage_key"),
            "video_storage_url": (remote_asset or {}).get("url"),
                "model": result.get("model", settings.replicate_influencer_model),
                "duration_seconds": result.get("duration_seconds", 1),
                "completed_at": _utc_now_iso(),
                "updated_at": _utc_now_iso(),
            },
        )
        record_job_outcome("influencer", "completed", int(result.get("duration_seconds", 1)))
    except Exception as exc:
        try:
            credit_balance(int(user_id), int(billed_amount), "influencer_refund", f"Reembolso por fallo influencer {influencer_id}")
        except Exception:
            pass
        update_anim(
            influencer_id,
            {
                "status": "failed",
                "stage": "Fallo en influencer",
                "progress": 0,
                "error": str(exc),
                "updated_at": _utc_now_iso(),
            },
        )
        record_job_outcome("influencer", "failed", 0)
    finally:
        release_generation_slot("influencer", int(user_id))
