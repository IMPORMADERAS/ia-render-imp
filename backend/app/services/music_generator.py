import os
import urllib.request
from pathlib import Path
from time import perf_counter

from ..config import settings


class MusicGenerator:
    @staticmethod
    def _compose_prompt(
        mode: str,
        genre: str,
        mood: str,
        instruments: str,
        user_taste: str,
        bpm: int | None,
        language: str,
        theme: str,
        custom_lyrics: str,
    ) -> str:
        genre_text = genre.strip() or "cinematic electronic"
        mood_text = mood.strip() or "emotional and modern"
        instr_text = instruments.strip() or "synth bass, pads, drums"
        taste_text = user_taste.strip() or "clean production, contemporary mix"
        bpm_text = f"~{bpm} BPM" if bpm else "moderate tempo"

        if mode == "instrumental":
            return (
                f"Create an instrumental track. Genre: {genre_text}. Mood: {mood_text}. "
                f"Instruments: {instr_text}. Tempo: {bpm_text}. "
                f"User taste references: {taste_text}. "
                "No vocals, no lyrics, no spoken voice. "
                "Polished mix, clear stereo image, dynamic arrangement."
            )

        song_theme = theme.strip() or "personal growth and resilience"
        lyric_block = custom_lyrics.strip()
        lyrics_instruction = (
            f"Use these custom lyrics as the main source: {lyric_block}."
            if lyric_block
            else "Write original lyrics with a strong hook, verse/chorus structure, and memorable refrain."
        )

        return (
            f"Create a full song in {language.upper()} inspired by modern AI songwriting apps like Suno style. "
            f"Genre: {genre_text}. Mood: {mood_text}. Instruments: {instr_text}. Tempo: {bpm_text}. "
            f"Theme: {song_theme}. User taste references: {taste_text}. "
            f"{lyrics_instruction} "
            "Add intro, verse, chorus, bridge, and final chorus energy. Keep it radio-friendly and emotionally engaging."
        )

    @staticmethod
    def _compose_song_lyrics(language: str, theme: str, custom_lyrics: str) -> str:
        custom = custom_lyrics.strip()
        if custom:
            return custom

        if (language or "es").strip().lower().startswith("en"):
            topic = theme.strip() or "personal growth"
            return (
                "[Verse]\n"
                f"I was down but now I rise, chasing brighter skies about {topic}\n"
                "Every scar became a map, every fear a door\n\n"
                "[Chorus]\n"
                "I keep moving, I keep shining through the storm\n"
                "Turning all my broken pieces into form\n"
                "This is my time, this is my fire\n"
                "I keep moving higher\n"
            )

        topic = theme.strip() or "superacion personal"
        return (
            "[Verso]\n"
            f"Caigo y me levanto, voy buscando luz, hablando de {topic}\n"
            "Cada herida fue camino, cada noche me enseno\n\n"
            "[Coro]\n"
            "Sigo adelante, no me apaga el temporal\n"
            "Con mis cicatrices vuelvo a despegar\n"
            "Hoy es mi momento, hoy vuelve a brillar\n"
            "Mi fuerza interior\n"
        )

    @staticmethod
    def _collect_model_candidates(primary_model: str) -> list[str]:
        candidates = [
            primary_model.strip(),
            "minimax/music-2.6",
            "meta/musicgen",
        ]
        result: list[str] = []
        for model in candidates:
            if model and model not in result:
                result.append(model)
        return result

    def _run_replicate_and_download(self, model_id: str, input_payload: dict, output_audio_path: str) -> None:
        import replicate

        output = replicate.run(model_id, input=input_payload)

        target = Path(output_audio_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        if hasattr(output, "read"):
            target.write_bytes(output.read())
            return

        if hasattr(output, "url"):
            with urllib.request.urlopen(str(output.url), timeout=300) as resp:
                target.write_bytes(resp.read())
            return

        if isinstance(output, list):
            if not output:
                raise RuntimeError("El modelo no devolvio audio")
            first = output[0]
            if hasattr(first, "url"):
                with urllib.request.urlopen(str(first.url), timeout=300) as resp:
                    target.write_bytes(resp.read())
                return
            url = str(first)
            if not url.startswith("http"):
                raise RuntimeError(f"Salida inesperada del modelo musical: {url!r}")
            with urllib.request.urlopen(url, timeout=300) as resp:
                target.write_bytes(resp.read())
            return

        url = str(output)
        if not url.startswith("http"):
            raise RuntimeError(f"Salida inesperada del modelo musical: {url!r}")
        with urllib.request.urlopen(url, timeout=300) as resp:
            target.write_bytes(resp.read())

    def _payload_for_model(
        self,
        model_id: str,
        mode: str,
        prompt: str,
        safe_duration: int,
        language: str,
        theme: str,
        custom_lyrics: str,
        seed: int | None,
    ) -> dict:
        model_key = model_id.lower().strip()

        if "minimax/music-2.6" in model_key:
            payload = {
                "prompt": f"{prompt}. Target duration around {safe_duration} seconds.",
                "audio_format": "mp3",
                "sample_rate": 44100,
                "bitrate": 256000,
            }
            if mode == "instrumental":
                payload["is_instrumental"] = True
            else:
                payload["is_instrumental"] = False
                lyrics = self._compose_song_lyrics(language=language, theme=theme, custom_lyrics=custom_lyrics)
                payload["lyrics"] = lyrics
                if not custom_lyrics.strip():
                    payload["lyrics_optimizer"] = True
            if seed is not None:
                payload["seed"] = int(seed)
            return payload

        # meta/musicgen fallback
        payload = {
            "prompt": prompt,
            "duration": safe_duration,
            "model_version": "stereo-melody-large",
        }
        if seed is not None:
            payload["seed"] = int(seed)
        return payload

    def generate_replicate(
        self,
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
    ) -> dict[str, int | str]:
        started = perf_counter()

        if not settings.replicate_api_token:
            raise RuntimeError("Falta REPLICATE_API_TOKEN en backend/.env")

        os.environ["REPLICATE_API_TOKEN"] = settings.replicate_api_token

        import replicate

        safe_mode = (mode or "instrumental").strip().lower()
        if safe_mode not in {"instrumental", "song"}:
            safe_mode = "instrumental"

        prompt = self._compose_prompt(
            mode=safe_mode,
            genre=genre,
            mood=mood,
            instruments=instruments,
            user_taste=user_taste,
            bpm=bpm,
            language=language,
            theme=theme,
            custom_lyrics=custom_lyrics,
        )

        safe_duration = max(8, min(30, int(duration_seconds)))
        primary_model = (
            settings.replicate_song_model.strip()
            if safe_mode == "song"
            else settings.replicate_music_model.strip()
        )
        model_candidates = self._collect_model_candidates(primary_model)

        last_error: Exception | None = None
        used_model = model_candidates[0]
        for model_id in model_candidates:
            input_payload = self._payload_for_model(
                model_id=model_id,
                mode=safe_mode,
                prompt=prompt,
                safe_duration=safe_duration,
                language=language,
                theme=theme,
                custom_lyrics=custom_lyrics,
                seed=seed,
            )
            try:
                self._run_replicate_and_download(
                    model_id=model_id,
                    input_payload=input_payload,
                    output_audio_path=output_audio_path,
                )
                used_model = model_id
                last_error = None
                break
            except Exception as exc:
                last_error = exc

        if last_error is not None:
            raise RuntimeError(
                f"No se pudo generar audio con los modelos configurados. Ultimo error: {last_error}"
            ) from last_error

        duration = int(perf_counter() - started)
        return {
            "duration_seconds": max(1, duration),
            "mode": safe_mode,
            "model": used_model,
            "prompt_used": prompt,
            "clip_seconds": safe_duration,
        }


music_generator = MusicGenerator()
