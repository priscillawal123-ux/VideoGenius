"""
Global configuration for Video Genius.
"""

import logging
from typing import Any, List

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from src.core.models import CustomModel

logger = logging.getLogger(__name__)


class GlobalConfig(CustomModel):
    """Global application configuration."""

    # Environment
    environment: str = Field(default="development")
    debug: bool = Field(default=False)

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8080)
    allowed_hosts: List[str] = Field(default_factory=lambda: ["*"])
    base_url: str = Field(default="https://videogenius.com.br")

    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:8080",
            "https://video-genius.com",
            "https://videogenius.com.br",
            "https://www.videogenius.com.br",
        ]
    )
    cors_headers: List[str] = Field(default_factory=lambda: ["*"])

    # Security
    jwt_secret_key: str = Field(default="change-me-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_hours: int = Field(default=24)

    # Application
    app_name: str = Field(default="Video Genius")
    app_version: str = Field(default="1.0.0")
    api_prefix: str = Field(default="/api/v1")

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize configuration."""
        super().__init__(**kwargs)
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        level = getattr(logging, self.log_level.upper(), logging.INFO)

        if self.log_format == "json":
            # JSON logging for production
            import json_log_formatter

            formatter = json_log_formatter.JSONFormatter()
        else:
            # Human-readable logging for development
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        root_logger.addHandler(handler)

        logger.info(f"Logging configured with level: {self.log_level}")


# Global config instance
global_config = GlobalConfig()
