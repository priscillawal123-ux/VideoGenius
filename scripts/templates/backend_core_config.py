# Video Genius - Python Configuration Template
# Versão: 1.0.0

"""
Configuration management using Pydantic Settings.
"""
from typing import List, Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8080, env="PORT")
    allowed_hosts: List[str] = Field(default_factory=lambda: ["*"])

    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:8080",
            "https://video-genius.com",
        ]
    )

    # Google Cloud
    google_project_id: str = Field(..., env="GOOGLE_PROJECT_ID")
    vertex_ai_location: str = Field(
        default="us-central1", env="VERTEX_AI_LOCATION"
    )
    bigquery_dataset: str = Field(
        default="video_data", env="BIGQUERY_DATASET"
    )
    cloud_storage_bucket: str = Field(..., env="CLOUD_STORAGE_BUCKET")

    # Security
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")

    # YouTube API
    youtube_api_key: Optional[str] = Field(
        default=None, env="YOUTUBE_API_KEY"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = None


def get_settings() -> Settings:
    """Get application settings."""
    global settings
    if settings is None:
        settings = Settings()
    return settings