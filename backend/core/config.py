"""
Configuration management using Pydantic Settings and
Google Cloud Secret Manager with performance optimizations.
"""

import logging
from typing import Any, List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.services.secret_manager import SecretManagerService

logger = logging.getLogger(__name__)


class CircuitBreakerConfig(BaseSettings):
    """Circuit breaker configuration."""

    failure_threshold: int = Field(default=5)
    recovery_timeout: int = Field(default=60)


class CacheConfig(BaseSettings):
    """Cache configuration."""

    ttl_seconds: int = Field(default=3600)
    max_size: int = Field(default=100)


class RetryConfig(BaseSettings):
    """Retry configuration."""

    initial_delay: float = Field(default=1.0)
    maximum_delay: float = Field(default=16.0)
    multiplier: float = Field(default=2.0)
    deadline: float = Field(default=120.0)


class Settings(BaseSettings):
    """Application settings loaded from environment variables
    and Secret Manager with Google Cloud best practices."""

    # Environment
    environment: str = Field(default="development")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8080)
    allowed_hosts: List[str] = Field(default_factory=lambda: ["*"])

    # Performance optimizations
    use_uvloop: bool = Field(default=True)
    enable_circuit_breaker: bool = Field(default=True)
    enable_caching: bool = Field(default=True)

    # Circuit breaker settings
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig)

    # Cache settings
    vertex_ai_cache: CacheConfig = Field(
        default_factory=lambda: CacheConfig(ttl_seconds=3600, max_size=100)
    )
    storage_cache: CacheConfig = Field(
        default_factory=lambda: CacheConfig(ttl_seconds=300, max_size=500)
    )
    secret_cache: CacheConfig = Field(
        default_factory=lambda: CacheConfig(ttl_seconds=600, max_size=50)
    )

    # Retry settings
    vertex_ai_retry: RetryConfig = Field(
        default_factory=lambda: RetryConfig(deadline=120.0)
    )
    bigquery_retry: RetryConfig = Field(
        default_factory=lambda: RetryConfig(deadline=60.0)
    )
    storage_retry: RetryConfig = Field(
        default_factory=lambda: RetryConfig(deadline=60.0)
    )
    secret_retry: RetryConfig = Field(
        default_factory=lambda: RetryConfig(deadline=30.0)
    )

    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
            "https://video-genius.com",
            "https://videogenius.com.br",
            "https://www.videogenius.com.br",
        ]
    )

    # Google Cloud
    google_project_id: str = Field(default="test-project", alias="GCP_PROJECT_ID")
    vertex_ai_location: str = Field(default="us-central1")
    bigquery_dataset: str = Field(default="test-dataset")
    cloud_storage_bucket: str = Field(default="test-bucket")
    worker_url: str = Field(
        default="http://localhost:8081/process-video-generation", alias="WORKER_URL"
    )

    # Secret Manager
    use_secret_manager: bool = Field(default=False)
    secret_manager_project_id: Optional[str] = Field(default=None)

    # Security
    jwt_secret_key: str = Field(default="test-secret-key")

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="text")

    # YouTube API
    youtube_api_key: Optional[str] = Field(default=None)
    youtube_client_secrets_file: Optional[str] = Field(default=None)
    youtube_oauth_credentials: Optional[str] = Field(default=None)

    # Video Generation
    default_video_duration: int = Field(default=60)
    max_video_duration: int = Field(default=600)
    video_output_format: str = Field(default="mp4")

    # FFmpeg
    ffmpeg_path: str = Field(default="/usr/bin/ffmpeg")

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize settings with optional Secret Manager loading."""
        super().__init__(**kwargs)

        # Load secrets from Secret Manager if enabled
        if self.use_secret_manager and self.secret_manager_project_id:
            self._load_from_secret_manager()

    def _load_from_secret_manager(self) -> None:
        """Load sensitive settings from Google Cloud Secret Manager."""
        try:
            assert self.secret_manager_project_id is not None
            secret_manager = SecretManagerService(self.secret_manager_project_id)

            # Load JWT secret key
            try:
                self.jwt_secret_key = secret_manager.get_secret("jwt-secret-key")
                logger.info("Loaded JWT secret key from Secret Manager")
            except ValueError:
                logger.warning("JWT secret key not found in Secret Manager")

            # Load YouTube API key
            try:
                self.youtube_api_key = secret_manager.get_secret("youtube-api-key")
                logger.info("Loaded YouTube API key from Secret Manager")
            except ValueError:
                logger.warning("YouTube API key not found in Secret Manager")

            # Load YouTube client secrets (JSON)
            try:
                youtube_secrets = secret_manager.get_secret_json(
                    "youtube-client-secrets"
                )
                self.youtube_client_secrets_file = youtube_secrets.get(
                    "client_secrets_path"
                )
                logger.info("Loaded YouTube client secrets from Secret Manager")
            except ValueError:
                logger.warning("YouTube client secrets not found in Secret Manager")

        except Exception as e:
            logger.error(f"Failed to load secrets from Secret Manager: {e}")
            logger.warning("Falling back to environment variables")


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
