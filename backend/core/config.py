"""
Configuration management using Pydantic Settings.

Centralized configuration for the Video Genius application.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings using Pydantic."""

    # Environment
    env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    api_workers: int = 4

    # CORS
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8080"
    ]

    # Google Cloud
    google_project_id: Optional[str] = None
    vertex_ai_location: str = "us-central1"
    bigquery_dataset: str = "video_data"
    cloud_storage_bucket: str = "video-genius-assets"

    # Security
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # YouTube API (optional)
    youtube_api_key: Optional[str] = None

    # Feature Flags
    enable_caching: bool = True
    enable_monitoring: bool = True

    class Config:
        env_file = ".env.local"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()