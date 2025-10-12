"""
Logging configuration for the Video Genius application.

Provides structured logging with proper formatting and levels.
"""

import logging
import sys
from typing import Optional

from backend.core.config import settings


def setup_logging(
    level: Optional[str] = None,
    format_string: Optional[str] = None
) -> None:
    """Setup logging configuration for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
    """
    # Use provided level or get from settings
    log_level = level or settings.log_level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Default format string
    if format_string is None:
        if settings.debug:
            format_string = (
                "%(asctime)s - %(name)s - %(levelname)s - "
                "%(filename)s:%(lineno)d - %(message)s"
            )
        else:
            format_string = (
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

    # Create formatter
    formatter = logging.Formatter(
        format_string,
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set specific loggers to reduce noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # Log the setup
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)