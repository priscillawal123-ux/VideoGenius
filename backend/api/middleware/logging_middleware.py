"""
Middleware for structured logging in Video Genius FastAPI application.

Provides request/response logging, performance metrics, and error tracking.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.logging_config import logger as structured_logger


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request/response logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with structured logging.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Start timer
        start_time = time.perf_counter()

        # Get request info
        method = request.method
        path = request.url.path
        query_string = request.url.query
        client_host = request.client.host if request.client else "unknown"

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log request
            structured_logger.log_request(
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                user_id=request.state.__dict__.get("user_id"),
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log error
            structured_logger.log_error_with_context(
                exc,
                {
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "duration_ms": duration_ms,
                    "client_host": client_host,
                },
            )

            raise


class ErrorTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for error tracking and reporting."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Track errors in request processing.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        try:
            response = await call_next(request)

            # Log errors
            if response.status_code >= 400:
                path = request.url.path
                method = request.method

                if response.status_code >= 500:
                    # Server error
                    structured_logger.error(
                        f"Server error: {method} {path}",
                        extra={
                            "status_code": response.status_code,
                            "path": path,
                            "method": method,
                        },
                    )
                elif response.status_code >= 400:
                    # Client error
                    structured_logger.warning(
                        f"Client error: {method} {path}",
                        extra={
                            "status_code": response.status_code,
                            "path": path,
                            "method": method,
                        },
                    )

            return response

        except Exception as exc:
            structured_logger.error(
                f"Unhandled exception: {str(exc)}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                },
                exc_info=True,
            )
            raise


async def add_request_context(request: Request, call_next: Callable) -> Response:
    """Add request context to state.

    Args:
        request: Incoming HTTP request
        call_next: Next middleware/handler

    Returns:
        HTTP response
    """
    # Extract user ID if available
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        request.state.user_id = auth_header[7:].split(".")[0]  # Extract from JWT
    else:
        request.state.user_id = None

    response = await call_next(request)
    return response
