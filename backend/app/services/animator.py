import os
import subprocess
import urllib.request
import json
from pathlib import Path
from time import perf_counter
from time import sleep

from PIL import Image, ImageOps

from ..config import settings


class Animator:
    _POLL_INTERVAL_SECONDS = 2.0
    _MAX_WAIT_SECONDS = 900
    _MAX_RELOAD_ERRORS = 5
    _DOWNLOAD_TIMEOUT_SECONDS = 900

    @staticmethod
    def _build_input_payload(model: str, img_file, prompt: str, duration_seconds: int) -> dict:
        model_id = model.lower().strip()
        duration = max(3, min(15, int(duration_seconds)))

        if "kling-v3-video" in model_id:
            return {
                "start_image": img_file,
                "prompt": prompt,
                "duration": duration,
                "mode": "pro",
                "generate_audio": False,
            }

        if "happyhorse-1.0" in model_id:
            return {
                "image": img_file,
                "prompt": prompt,
                "duration": duration,
                "resolution": "1080p",
            }

        return {
            "image": img_file,
            "prompt": prompt,
            "duration": duration,
        }

    @staticmethod
    def _output_to_url(output: object, context: str) -> str:
        if hasattr(output, "url"):
            return str(output.url)

        if isinstance(output, list):
            if not output:
                raise RuntimeError(f"El modelo no devolvio salida para {context}")
            first = output[0]
            if hasattr(first, "url"):
                return str(first.url)
            return str(first)

        return str(output)

    def _write_output_file(self, output: object, target_path: str, context: str) -> None:
        target = Path(target_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        if hasattr(output, "read"):
            target.write_bytes(output.read())
            return

        url = self._output_to_url(output, context)
        if not url.startswith("http"):
            raise RuntimeError(f"Salida inesperada del modelo de {context}: {url!r}")

        with urllib.request.urlopen(url, timeout=self._DOWNLOAD_TIMEOUT_SECONDS) as resp:
            target.write_bytes(resp.read())

    def _run_prediction_with_polling(self, model: str, payload: dict) -> object:
        import replicate

        prediction = replicate.predictions.create(model=model, input=payload)
        deadline = perf_counter() + self._MAX_WAIT_SECONDS
        reload_errors = 0

        while True:
            status = str(getattr(prediction, "status", "")).strip().lower()
            if status == "succeeded":
                return getattr(prediction, "output", None)

            if status in {"failed", "canceled"}:
                detail = getattr(prediction, "error", None) or "Sin detalle"
                raise RuntimeError(f"Prediction failed: {detail}")

            if perf_counter() >= deadline:
                raise RuntimeError(
                    f"La prediccion de Replicate excedio {self._MAX_WAIT_SECONDS}s (estado: {status or 'desconocido'})"
                )

            sleep(self._POLL_INTERVAL_SECONDS)
            try:
                prediction.reload()
                reload_errors = 0
            except Exception as exc:
                reload_errors += 1
                if reload_errors >= self._MAX_RELOAD_ERRORS:
                    raise RuntimeError(f"No se pudo consultar el estado en Replicate: {exc}") from exc
                sleep(min(8.0, self._POLL_INTERVAL_SECONDS * reload_errors))

    @staticmethod
    def _probe_video_size(video_path: str) -> tuple[int, int] | None:
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-select_streams",
                    "v:0",
                    "-show_entries",
                    "stream=width,height",
                    "-of",
                    "json",
                    video_path,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout or "{}")
            streams = payload.get("streams") if isinstance(payload, dict) else None
            if not isinstance(streams, list) or not streams:
                return None
            stream = streams[0] if isinstance(streams[0], dict) else {}
            width = int(stream.get("width") or 0)
            height = int(stream.get("height") or 0)
            if width <= 0 or height <= 0:
                return None
            return width, height
        except Exception:
            return None

    @staticmethod
    def _probe_image_size(image_path: str) -> tuple[int, int] | None:
        try:
            with Image.open(image_path) as raw:
                img = ImageOps.exif_transpose(raw)
                width, height = img.size
                if width <= 0 or height <= 0:
                    return None
                return int(width), int(height)
        except Exception:
            return None

    @staticmethod
    def _round_even(value: int) -> int:
        safe_value = max(2, int(value))
        return safe_value if safe_value % 2 == 0 else safe_value - 1

    def _crop_video_to_match_aspect_ratio(self, source_video_path: str, output_video_path: str) -> None:
        source_size = self._probe_video_size(source_video_path)
        output_size = self._probe_video_size(output_video_path)
        if source_size is None or output_size is None:
            return

        src_w, src_h = source_size
        out_w, out_h = output_size
        source_ratio = src_w / src_h
        output_ratio = out_w / out_h

        if abs(source_ratio - output_ratio) <= 0.01:
            return

        if output_ratio > source_ratio:
            crop_w = self._round_even(int(round(out_h * source_ratio)))
            crop_h = self._round_even(out_h)
        else:
            crop_w = self._round_even(out_w)
            crop_h = self._round_even(int(round(out_w / source_ratio)))

        if crop_w <= 0 or crop_h <= 0 or crop_w > out_w or crop_h > out_h:
            return

        crop_x = max(0, (out_w - crop_w) // 2)
        crop_y = max(0, (out_h - crop_h) // 2)

        if crop_x == 0 and crop_y == 0 and crop_w == out_w and crop_h == out_h:
            return

        target = Path(output_video_path)
        temp_path = target.with_name(f"{target.stem}.cropped{target.suffix}")
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            output_video_path,
            "-vf",
            f"crop={crop_w}:{crop_h}:{crop_x}:{crop_y}",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-c:a",
            "copy",
            str(temp_path),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            temp_path.replace(target)
        finally:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)

    def _crop_video_to_target_aspect_ratio(self, output_video_path: str, target_width: int, target_height: int) -> None:
        output_size = self._probe_video_size(output_video_path)
        if output_size is None:
            return
        if target_width <= 0 or target_height <= 0:
            return

        out_w, out_h = output_size
        target_ratio = target_width / target_height
        output_ratio = out_w / out_h

        if abs(target_ratio - output_ratio) <= 0.01:
            return

        if output_ratio > target_ratio:
            crop_w = self._round_even(int(round(out_h * target_ratio)))
            crop_h = self._round_even(out_h)
        else:
            crop_w = self._round_even(out_w)
            crop_h = self._round_even(int(round(out_w / target_ratio)))

        if crop_w <= 0 or crop_h <= 0 or crop_w > out_w or crop_h > out_h:
            return

        crop_x = max(0, (out_w - crop_w) // 2)
        crop_y = max(0, (out_h - crop_h) // 2)

        if crop_x == 0 and crop_y == 0 and crop_w == out_w and crop_h == out_h:
            return

        target = Path(output_video_path)
        temp_path = target.with_name(f"{target.stem}.cropped{target.suffix}")
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            output_video_path,
            "-vf",
            f"crop={crop_w}:{crop_h}:{crop_x}:{crop_y}",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-c:a",
            "copy",
            str(temp_path),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            temp_path.replace(target)
        finally:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)

    def animate_replicate(
        self,
        image_path: str,
        output_video_path: str,
        prompt: str,
        model: str = "kwaivgi/kling-v3-video",
        duration_seconds: int = 5,
    ) -> dict:
        started = perf_counter()

        if not settings.replicate_api_token:
            raise RuntimeError("Falta REPLICATE_API_TOKEN en backend/.env")

        os.environ["REPLICATE_API_TOKEN"] = settings.replicate_api_token

        with open(image_path, "rb") as img_file:
            payload = self._build_input_payload(model, img_file, prompt, duration_seconds)
            output = self._run_prediction_with_polling(model=model, payload=payload)

        self._write_output_file(output=output, target_path=output_video_path, context="animacion")

        duration = int(perf_counter() - started)
        return {"duration_seconds": max(1, duration)}

    def animate_influencer_replicate(
        self,
        source_video_path: str,
        reference_image_path: str,
        output_video_path: str,
        instruction_prompt: str,
        resolution: str = "720p",
        target_fps: str = "original",
        turbo: bool = False,
    ) -> dict:
        started = perf_counter()

        if not settings.replicate_api_token:
            raise RuntimeError("Falta REPLICATE_API_TOKEN en backend/.env")

        os.environ["REPLICATE_API_TOKEN"] = settings.replicate_api_token

        safe_resolution = resolution if resolution in {"720p", "1080p"} else "720p"
        safe_fps = target_fps if target_fps in {"original", "24", "48"} else "original"

        with open(source_video_path, "rb") as source_video, open(reference_image_path, "rb") as reference_image:
            payload = {
                "video": source_video,
                "image": reference_image,
                "instruction_prompt": instruction_prompt.strip(),
                "resolution": safe_resolution,
                "target_fps": safe_fps,
                "save_audio": True,
                "ignore_audio": False,
                "turbo": bool(turbo),
            }
            output = self._run_prediction_with_polling(model=settings.replicate_influencer_model, payload=payload)

        self._write_output_file(output=output, target_path=output_video_path, context="influencer")

        # Preserve the character image format (vertical/square/horizontal) to avoid black bars.
        reference_size = self._probe_image_size(reference_image_path)
        if reference_size is not None:
            self._crop_video_to_target_aspect_ratio(
                output_video_path=output_video_path,
                target_width=reference_size[0],
                target_height=reference_size[1],
            )
        else:
            self._crop_video_to_match_aspect_ratio(source_video_path=source_video_path, output_video_path=output_video_path)

        duration = int(perf_counter() - started)
        return {"duration_seconds": max(1, duration), "model": settings.replicate_influencer_model}


animator = Animator()
