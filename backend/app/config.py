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
    admin_username: str = ""
    admin_password: str = ""
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

    jobs_queue_enabled: bool = False
    redis_url: str = ""
    queue_require_redis: bool = False
    rq_default_queue: str = "default"
    rq_queues: str = "default,render,video,music,influencer"
    rq_job_timeout_seconds: int = 1800

    postgres_mirror_enabled: bool = False
    postgres_dsn: str = ""
    postgres_primary_auth_enabled: bool = False
    postgres_primary_wallet_enabled: bool = False
    postgres_primary_jobs_enabled: bool = False
    postgres_primary_auth_percent: int = 0
    postgres_primary_wallet_percent: int = 0
    postgres_primary_jobs_percent: int = 0
    postgres_cutover_seed: str = "iaimp-cutover"
    sqlite_fallback_enabled: bool = True

    render_queue_backlog_limit: int = 250
    video_queue_backlog_limit: int = 80
    music_queue_backlog_limit: int = 120
    influencer_queue_backlog_limit: int = 40
    render_user_active_limit: int = 3
    video_user_active_limit: int = 1
    music_user_active_limit: int = 2
    influencer_user_active_limit: int = 1

    object_storage_enabled: bool = False
    object_storage_bucket: str = ""
    object_storage_region: str = ""
    object_storage_endpoint_url: str = ""
    object_storage_access_key_id: str = ""
    object_storage_secret_access_key: str = ""
    object_storage_public_base_url: str = ""
    object_storage_presign_expiry_seconds: int = 3600

    benchmark_mode_enabled: bool = False
    benchmark_job_duration_seconds: int = 1

    render_latency_warn_ms: int = 1200
    render_rejection_warn_count: int = 10
    render_error_warn_count: int = 5
    video_latency_warn_ms: int = 1500
    video_rejection_warn_count: int = 5
    video_error_warn_count: int = 3
    music_latency_warn_ms: int = 1000
    music_rejection_warn_count: int = 8
    music_error_warn_count: int = 4
    influencer_latency_warn_ms: int = 1800
    influencer_rejection_warn_count: int = 3
    influencer_error_warn_count: int = 2
    consistency_min_coverage_pct: float = 99.0

    use_gpu: bool = True
    max_image_size: int = 2048
    default_steps: int = 35
    default_guidance: float = 7.5

    model_config = SettingsConfigDict(env_file="backend/.env", env_file_encoding="utf-8", extra="ignore")

    @property
    def is_production(self) -> bool:
        return (self.app_env or "").strip().lower() in {"prod", "production"}

    @property
    def secure_cookies(self) -> bool:
        return self.is_production


settings = Settings()


def ensure_directories() -> None:
    for path in [settings.data_dir, settings.output_dir, settings.input_dir]:
        Path(path).mkdir(parents=True, exist_ok=True)
