"""
Pydantic schemas for video generation domain.
"""

from typing import List, Optional

from pydantic import Field, field_validator

from src.core.models import CustomModel
from src.videos.constants import VideoStyle


class VideoGenerationRequest(CustomModel):
    """Request model for video generation."""

    topic: str = Field(
        ..., min_length=10, max_length=200, description="Video topic or subject"
    )
    duration_seconds: int = Field(
        ..., ge=30, le=600, description="Target video duration (30-600 seconds)"
    )
    style: VideoStyle = Field(default=VideoStyle.EDUCATIONAL, description="Video style")
    additional_context: Optional[str] = Field(
        None, max_length=500, description="Additional context or requirements"
    )
    tags: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="Video tags",
    )

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tags format."""
        return [tag.lower().strip() for tag in v if tag.strip()]


class VideoGenerationResponse(CustomModel):
    """Response model for video generation."""

    job_id: str = Field(..., description="Generation job ID")
    status: str = Field(..., description="Job status")
    estimated_completion_time: int = Field(..., description="Estimated time in seconds")
    message: str = Field(..., description="Status message")


class VideoJobStatus(CustomModel):
    """Video job status response."""

    job_id: str = Field(..., description="Generation job ID")
    status: str = Field(..., description="Current job status")
    topic: str = Field(..., description="Video topic")
    style: str = Field(..., description="Video style")
    duration_seconds: int = Field(..., description="Target duration")
    video_url: Optional[str] = Field(None, description="Generated video URL")
    script: Optional[dict] = Field(None, description="Generated script data")
    created_at: str = Field(..., description="Job creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    estimated_completion_time: Optional[int] = Field(
        None, description="Estimated completion time"
    )


class VideoGenerationError(CustomModel):
    """Error response for video generation."""

    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
