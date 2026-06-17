from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


RenderStyle = Literal["editorial", "commercial", "competition", "night", "interior"]
RenderQuality = Literal["fast", "balanced", "ultra"]
JobStatus = Literal["queued", "processing", "completed", "failed"]


class RenderRequest(BaseModel):
    prompt: str = Field(min_length=10, max_length=2000)
    negative_prompt: str = Field(default="low quality, blurry, distorted geometry, cartoon")
    style: RenderStyle = "editorial"
    quality: RenderQuality = "balanced"
    steps: int = Field(default=35, ge=10, le=80)
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0)
    seed: int | None = Field(default=None, ge=0)


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str


class JobDetail(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    job_id: str
    sequence: int | None = None
    status: JobStatus
    prompt: str
    style: str
    input_image: str
    output_image: str | None = None
    error: str | None = None
    warning: str | None = None
    progress: int = 0
    stage: str = "En cola"
    eta_seconds: int | None = None
    elapsed_seconds: int = 0
    expected_total_seconds: int = 0
    model_mode: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    updated_at: str | None = None
