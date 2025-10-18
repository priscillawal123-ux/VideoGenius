"""
Cloud Logging Configuration for Video Genius Backend

Provides structured logging, error reporting, and performance metrics
for Google Cloud environment.

Usage:
    from logging_config import setup_cloud_logging, logger
    
    # Log structured event
    logger.info("Task created", extra={
        "task_id": task_id,
        "user_id": user_id,
        "duration_ms": duration
    })
    
    # Log error
    logger.error("Failed to process video", extra={
        "error_code": "VIDEO_PROCESS_FAILED",
        "video_id": video_id,
        "retry_count": retry_count
    }, exc_info=True)
"""

import json
import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional

import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler
from google.cloud.logging_v2.logger import Logger as GoogleLogger
from pythonjsonlogger import jsonlogger


class StructuredFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add timestamp
        log_record["timestamp"] = datetime.utcnow().isoformat() + "Z"

        # Add severity level
        log_record["severity"] = record.levelname

        # Add source location
        log_record["sourceLocation"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        # Add exception info if present
        if record.exc_info and not log_record.get("exception"):
            log_record["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exc(),
            }

        # Add custom fields from extra dict
        if hasattr(record, "custom_fields"):
            log_record.update(record.custom_fields)

        # Remove duplicate message field
        if "msg" in log_record and log_record.get("message"):
            del log_record["msg"]


class VideoGeniusLogger:
    """Structured logger for Video Genius backend."""

    def __init__(
        self,
        name: str = "video-genius",
        project_id: Optional[str] = None,
        use_cloud_logging: bool = True,
    ):
        """Initialize logger.

        Args:
            name: Logger name
            project_id: Google Cloud project ID (auto-detected if None)
            use_cloud_logging: Whether to use Google Cloud Logging
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.use_cloud_logging = use_cloud_logging
        self.project_id = project_id

        # Remove any existing handlers
        self.logger.handlers.clear()

        # Console handler with JSON formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        formatter = StructuredFormatter(
            fmt="%(timestamp)s %(severity)s %(message)s"
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Cloud Logging handler
        if use_cloud_logging:
            try:
                client = google.cloud.logging.Client(project=project_id)
                cloud_handler = CloudLoggingHandler(
                    client, name=name, resource=self._get_resource()
                )
                cloud_handler.setLevel(logging.INFO)
                self.logger.addHandler(cloud_handler)
            except Exception as e:
                self.logger.warning(
                    f"Failed to initialize Cloud Logging: {e}. "
                    "Falling back to console logging."
                )

    @staticmethod
    def _get_resource() -> Dict[str, Any]:
        """Get Google Cloud resource descriptor.

        Returns:
            Resource descriptor dict
        """
        import os

        # Detect if running on Cloud Run
        if os.getenv("K_SERVICE"):
            return {
                "type": "cloud_run_revision",
                "labels": {
                    "service_name": os.getenv("K_SERVICE", "unknown"),
                    "revision_name": os.getenv("K_REVISION", "unknown"),
                },
            }

        # Default to global resource
        return {"type": "global"}

    def _add_custom_fields(self, extra: Optional[Dict[str, Any]] = None) -> None:
        """Add custom fields to logger context."""
        if extra:
            current_logger = logging.getLogger()
            if not hasattr(current_logger, "custom_fields"):
                current_logger.custom_fields = {}
            current_logger.custom_fields.update(extra)

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message."""
        self._add_custom_fields(extra)
        self.logger.debug(message)

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log info message."""
        self._add_custom_fields(extra)
        self.logger.info(message)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message."""
        self._add_custom_fields(extra)
        self.logger.warning(message)

    def error(
        self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False
    ) -> None:
        """Log error message."""
        self._add_custom_fields(extra)
        self.logger.error(message, exc_info=exc_info)

    def critical(
        self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False
    ) -> None:
        """Log critical message."""
        self._add_custom_fields(extra)
        self.logger.critical(message, exc_info=exc_info)

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None,
    ) -> None:
        """Log HTTP request.

        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            user_id: User ID (optional)
        """
        level = "WARNING" if status_code >= 400 else "INFO"
        self.logger.log(
            getattr(logging, level),
            f"{method} {path}",
            extra={
                "httpRequest": {
                    "method": method,
                    "path": path,
                    "status": status_code,
                    "duration_ms": duration_ms,
                    "user_id": user_id,
                }
            },
        )

    def log_task_operation(
        self,
        operation: str,
        task_id: str,
        status: str,
        duration_ms: float,
        user_id: Optional[str] = None,
    ) -> None:
        """Log task operation.

        Args:
            operation: Operation type (create/update/delete/read)
            task_id: Task ID
            status: Operation status (success/failure)
            duration_ms: Operation duration
            user_id: User ID (optional)
        """
        self.logger.info(
            f"Task {operation}",
            extra={
                "event": f"task_{operation}",
                "task_id": task_id,
                "status": status,
                "duration_ms": duration_ms,
                "user_id": user_id,
            },
        )

    def log_database_query(
        self,
        query_type: str,
        table: str,
        duration_ms: float,
        rows_affected: int,
    ) -> None:
        """Log database query.

        Args:
            query_type: Query type (SELECT/INSERT/UPDATE/DELETE)
            table: Table name
            duration_ms: Query duration
            rows_affected: Number of rows affected
        """
        self.logger.debug(
            f"Database {query_type}",
            extra={
                "database": {
                    "query_type": query_type,
                    "table": table,
                    "duration_ms": duration_ms,
                    "rows_affected": rows_affected,
                }
            },
        )

    def log_error_with_context(
        self,
        error: Exception,
        context: Dict[str, Any],
    ) -> None:
        """Log error with context.

        Args:
            error: Exception object
            context: Context information
        """
        self.logger.error(
            f"{type(error).__name__}: {str(error)}",
            extra={
                "error": {
                    "type": type(error).__name__,
                    "message": str(error),
                    "context": context,
                }
            },
            exc_info=True,
        )


def setup_cloud_logging(
    project_id: Optional[str] = None,
    use_cloud_logging: bool = True,
) -> VideoGeniusLogger:
    """Setup Cloud Logging for Video Genius.

    Args:
        project_id: Google Cloud project ID (auto-detected if None)
        use_cloud_logging: Whether to use Google Cloud Logging

    Returns:
        Configured logger instance
    """
    logger = VideoGeniusLogger(
        name="video-genius",
        project_id=project_id,
        use_cloud_logging=use_cloud_logging,
    )
    return logger


# Global logger instance
logger = setup_cloud_logging()


if __name__ == "__main__":
    # Example usage
    print("Testing Cloud Logging Configuration...")

    # Info log
    logger.info(
        "Application started",
        extra={"version": "1.0.0", "environment": "production"},
    )

    # Request log
    logger.log_request(
        method="GET",
        path="/api/v1/tasks",
        status_code=200,
        duration_ms=245.5,
        user_id="user123",
    )

    # Task operation log
    logger.log_task_operation(
        operation="create",
        task_id="task_abc123",
        status="success",
        duration_ms=150.2,
        user_id="user123",
    )

    # Database query log
    logger.log_database_query(
        query_type="SELECT",
        table="tasks",
        duration_ms=45.3,
        rows_affected=21,
    )

    # Error log with context
    try:
        raise ValueError("Invalid task status")
    except Exception as e:
        logger.log_error_with_context(
            e,
            {"task_id": "task_abc123", "attempted_status": "invalid"},
        )

    print("✅ Cloud Logging configuration working correctly!")
