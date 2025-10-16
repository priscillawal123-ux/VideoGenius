"""
Storage configuration.
"""

from pydantic import Field

from src.core.models import CustomModel


class StorageConfig(CustomModel):
    """Configuration for cloud storage."""

    # Storage provider
    provider: str = Field(default="gdrive")  # Options: gcs, gdrive

    # Google Cloud Storage
    cloud_storage_bucket: str = Field(default="video-genius-dev-videos")
    cloud_storage_location: str = Field(default="us-central1")

    # Upload settings
    max_file_size: int = Field(default=500 * 1024 * 1024)  # 500MB
    allowed_video_formats: list[str] = Field(
        default_factory=lambda: ["mp4", "avi", "mov", "mkv"]
    )

    # Storage paths
    videos_path: str = Field(default="videos/")
    scripts_path: str = Field(default="scripts/")
    thumbnails_path: str = Field(default="thumbnails/")

    # CDN settings
    cdn_base_url: str | None = Field(default=None)
    signed_url_expiration: int = Field(default=3600)  # 1 hour

    # Cleanup settings
    temp_file_cleanup_interval: int = Field(default=3600)  # 1 hour
    max_temp_file_age: int = Field(default=86400)  # 24 hours
