"""
Logging configuration for Video Genius.
"""

import json
import logging
import sys
from typing import Any, Optional

from backend.core.config import get_settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)

        return json.dumps(log_entry, default=str)


def setup_logging(level: Optional[str] = None) -> None:
    """Setup logging configuration."""
    settings = get_settings()

    # Determine log level
    if level is None:
        level = settings.log_level

    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter based on log format setting
    if settings.log_format.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set logging levels for external libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # Create video_genius logger
    logger = logging.getLogger("video_genius")
    logger.setLevel(numeric_level)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(f"video_genius.{name}")


def log_with_context(
    logger: logging.Logger, level: int, message: str, **context: Any
) -> None:
    """Log message with additional context."""
    extra = {"extra_fields": context} if context else {}
    logger.log(level, message, extra=extra)


def log_error_with_context(
    logger: logging.Logger, message: str, error: Exception, **context: Any
) -> None:
    """Log error with exception details and context."""
    context.update(
        {
            "error_type": type(error).__name__,
            "error_message": str(error),
        }
    )
    log_with_context(logger, logging.ERROR, message, **context)
