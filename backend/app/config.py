from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "IA IMP"
    app_env: str = "development"

    data_dir: str = "backend/data"
    output_dir: str = "backend/data/outputs"
    input_dir: str = "backend/data/inputs"

    hf_model_id: str = "stabilityai/stable-diffusion-xl-base-1.0"
    controlnet_model_id: str = "diffusers/controlnet-canny-sdxl-1.0"
    render_provider: str = "local"
    replicate_api_token: str = ""
    replicate_model: str = "black-forest-labs/flux-kontext-pro"
    replicate_text_model: str = "google/nano-banana"
    replicate_chat_model: str = "openai/gpt-4o"
    replicate_music_model: str = "minimax/music-2.6"
    replicate_song_model: str = "minimax/music-2.6"
    replicate_material_model: str = "google/nano-banana"
    replicate_influencer_model: str = "prunaai/p-video-animate"
    wompi_public_key: str = ""
    wompi_private_key: str = ""
    wompi_events_key: str = ""
    wompi_integrity_key: str = ""
    wompi_checkout_base_url: str = "https://checkout.wompi.co/p/"
    wompi_api_base_url: str = "https://api.wompi.co/v1"
    wompi_currency: str = "COP"
    wompi_min_recharge_cop: int = 5000
    admin_username: str = "admin"
    admin_password: str = "Admin1234!"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_use_tls: bool = True
    replicate_input_image_field: str = "input_image"
    replicate_max_concurrent_predictions: int = 2
    replicate_retry_max_attempts: int = 4
    replicate_retry_initial_delay_seconds: float = 1.2
    fallback_to_local_on_cloud_error: bool = False

    use_gpu: bool = True
    max_image_size: int = 2048
    default_steps: int = 35
    default_guidance: float = 7.5

    model_config = SettingsConfigDict(env_file="backend/.env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()


def ensure_directories() -> None:
    for path in [settings.data_dir, settings.output_dir, settings.input_dir]:
        Path(path).mkdir(parents=True, exist_ok=True)
