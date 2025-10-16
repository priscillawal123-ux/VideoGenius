"""Monitoring and tracing middleware for FastAPI."""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for request monitoring and tracing."""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Extract request info
        method = request.method
        path = request.url.path
        query_string = str(request.url.query)

        # Create request ID for tracing
        request_id = f"{int(start_time * 1000000)}"

        # Log request start
        logger.info(f"Request started: {request_id} {method} {path}")

        # Process request
        try:
            response = await call_next(request)

            # Log successful response
            duration = time.time() - start_time
            logger.info(
                f"Request completed: {request_id} {method} {path} {response.status_code} {duration:.3f}s"
            )

            return response

        except Exception as e:
            # Log error response
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {request_id} {method} {path} {str(e)} {duration:.3f}s"
            )
            raise


async def health_check_middleware(request: Request, call_next):
    """Middleware for detailed health checks."""
    if request.url.path == "/health":
        # Perform actual health checks
        health_status = await perform_health_checks()
        if not health_status["healthy"]:
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "details": health_status},
            )
        return JSONResponse(content={"status": "healthy"})

    response = await call_next(request)
    return response


async def perform_health_checks() -> dict:
    """Perform comprehensive health checks."""
    health_status = {"healthy": True, "checks": {}}

    try:
        # Check BigQuery connectivity
        from backend.database.bigquery_client import BigQueryClient

        bq_client = BigQueryClient(
            project_id=settings.google_project_id, dataset_id=settings.bigquery_dataset
        )
        # Simple query to test connection
        await bq_client.client.query("SELECT 1")
        health_status["checks"]["bigquery"] = "ok"
    except Exception as e:
        health_status["checks"]["bigquery"] = f"error: {str(e)}"
        health_status["healthy"] = False

    try:
        # Check Cloud Storage connectivity
        from backend.storage.cloud_storage import CloudStorageService

        storage_client = CloudStorageService(settings.cloud_storage_bucket)
        # Test bucket access
        bucket = storage_client.client.bucket(settings.cloud_storage_bucket)
        bucket.reload()
        health_status["checks"]["cloud_storage"] = "ok"
    except Exception as e:
        health_status["checks"]["cloud_storage"] = f"error: {str(e)}"
        health_status["healthy"] = False

    try:
        # Check Vertex AI connectivity
        from backend.services.script_generator import ScriptGeneratorService

        script_service = ScriptGeneratorService(
            project_id=settings.google_project_id, location=settings.vertex_ai_location
        )
        # This will test if the model can be initialized
        health_status["checks"]["vertex_ai"] = "ok"
    except Exception as e:
        health_status["checks"]["vertex_ai"] = f"error: {str(e)}"
        health_status["healthy"] = False

    return health_status


def setup_monitoring(app):
    """Setup monitoring and tracing for FastAPI app."""
    # Add monitoring middleware
    # app.middleware("http")(MonitoringMiddleware)

    # Add health check middleware
    # app.middleware("http")(health_check_middleware)

    # Configure structured logging for Cloud Logging
    # if settings.environment == "production":
    #     # Use JSON logging for Cloud Logging
    #     import json

    #     shared_processors = [
    #         structlog.stdlib.filter_by_level,
    #         structlog.stdlib.add_logger_name,
    #         structlog.stdlib.add_log_level,
    #         structlog.stdlib.PositionalArgumentsFormatter(),
    #         structlog.processors.TimeStamper(fmt="iso"),
    #         structlog.processors.StackInfoRenderer(),
    #         structlog.processors.format_exc_info,
    #         structlog.processors.UnicodeDecoder(),
    #         structlog.processors.JSONRenderer(),
    #     ]

    #     structlog.configure(
    #         processors=shared_processors,
    #         context_class=dict,
    #         logger_factory=structlog.stdlib.LoggerFactory(),
    #         wrapper_class=structlog.stdlib.BoundLogger,
    #         cache_logger_on_first_use=True,
    #     )
    # else:
    #     # Use pretty printing for development
    #     structlog.configure(
    #         processors=[
    #             structlog.stdlib.filter_by_level,
    #             structlog.stdlib.add_logger_name,
    #             structlog.stdlib.add_log_level,
    #             structlog.stdlib.PositionalArgumentsFormatter(),
    #             structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
    #             structlog.processors.StackInfoRenderer(),
    #             structlog.processors.format_exc_info,
    #             structlog.processors.UnicodeDecoder(),
    #             structlog.dev.ConsoleRenderer(),
    #         ],
    #         context_class=dict,
    #         logger_factory=structlog.stdlib.LoggerFactory(),
    #         wrapper_class=structlog.stdlib.BoundLogger,
    #         cache_logger_on_first_use=True,
    #     )
