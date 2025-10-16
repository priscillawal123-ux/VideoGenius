"""
Global exception handler middleware.
"""

from typing import Any

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse

from backend.core.exceptions import VideoGeniusException
from backend.core.logging import get_logger

logger = get_logger(__name__)


async def exception_handler(request: Request, exc: Exception) -> Response:
    """Global exception handler for Video Genius API."""

    # Handle VideoGenius custom exceptions
    if isinstance(exc, VideoGeniusException):
        logger.error(
            f"VideoGenius exception: {exc.error_code}",
            extra={
                "error_code": exc.error_code,
                "status_code": exc.status_code,
                "path": str(request.url),
                "method": request.method,
                "details": exc.details,
            },
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
        )

    # Handle FastAPI HTTPException
    if isinstance(exc, HTTPException):
        logger.warning(
            f"HTTP exception: {exc.status_code}",
            extra={
                "status_code": exc.status_code,
                "detail": exc.detail,
                "path": str(request.url),
                "method": request.method,
            },
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP_EXCEPTION",
                "message": exc.detail,
                "status_code": exc.status_code,
            },
        )

    # Handle unexpected exceptions
    logger.error(
        f"Unexpected exception: {type(exc).__name__}",
        exc_info=exc,
        extra={
            "exception_type": type(exc).__name__,
            "path": str(request.url),
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "status_code": 500,
        },
    )


def add_exception_handlers(app: Any) -> None:
    """Add global exception handlers to FastAPI app."""
    app.add_exception_handler(VideoGeniusException, exception_handler)
    app.add_exception_handler(HTTPException, exception_handler)
    app.add_exception_handler(Exception, exception_handler)
