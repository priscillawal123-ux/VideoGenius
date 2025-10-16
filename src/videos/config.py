"""
Video generation configuration.
"""

from typing import List

from pydantic import Field

from src.core.models import CustomModel


class VideoConfig(CustomModel):
    """Configuration for video generation features."""

    # Video Generation
    default_video_duration: int = Field(default=60, ge=30, le=600)
    max_video_duration: int = Field(default=600)
    min_video_duration: int = Field(default=30)

    # Styles
    supported_styles: List[str] = Field(
        default_factory=lambda: [
            "educational",
            "entertaining",
            "documentary",
            "tutorial",
        ]
    )

    # Content limits
    max_topic_length: int = Field(default=200)
    max_additional_context_length: int = Field(default=500)
    max_tags_count: int = Field(default=5)

    # Processing
    script_generation_timeout: int = Field(default=300)  # 5 minutes
    video_rendering_timeout: int = Field(default=1800)  # 30 minutes
    max_concurrent_jobs: int = Field(default=5)

    # Output
    video_output_format: str = Field(default="mp4")
    default_video_quality: str = Field(default="720p")

    # Estimation
    base_processing_time: int = Field(default=120)  # Base time in seconds
    time_per_duration_second: float = Field(default=5.0)  # Multiplier for duration
