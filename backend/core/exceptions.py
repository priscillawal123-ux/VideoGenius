"""
Core exceptions for Video Genius.
"""

from typing import Any, Dict, Optional


class VideoGeniusException(Exception):
    """Base exception for Video Genius application."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
        }


class ValidationError(VideoGeniusException):
    """Validation error."""

    def __init__(self, message: str, field: Optional[str] = None, **details: Any):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details={"field": field, **details} if field else details,
        )


class NotFoundError(VideoGeniusException):
    """Resource not found error."""

    def __init__(
        self, resource: str, resource_id: Optional[str] = None, **details: Any
    ):
        message = f"{resource} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource": resource, "resource_id": resource_id, **details},
        )


class ConflictError(VideoGeniusException):
    """Resource conflict error."""

    def __init__(self, message: str, resource: Optional[str] = None, **details: Any):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details={"resource": resource, **details} if resource else details,
        )


class AuthenticationError(VideoGeniusException):
    """Authentication error."""

    def __init__(self, message: str = "Authentication failed", **details: Any):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(VideoGeniusException):
    """Authorization error."""

    def __init__(self, message: str = "Insufficient permissions", **details: Any):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


class ExternalServiceError(VideoGeniusException):
    """External service error."""

    def __init__(
        self, service: str, message: str, status_code: int = 502, **details: Any
    ):
        super().__init__(
            message=f"{service}: {message}",
            status_code=status_code,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, **details},
        )


class ConfigurationError(VideoGeniusException):
    """Configuration error."""

    def __init__(self, message: str, config_key: Optional[str] = None, **details: Any):
        super().__init__(
            message=message,
            status_code=500,
            error_code="CONFIGURATION_ERROR",
            details={"config_key": config_key, **details} if config_key else details,
        )


class RateLimitError(VideoGeniusException):
    """Rate limit exceeded error."""

    def __init__(self, message: str = "Rate limit exceeded", **details: Any):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
        )


class QuotaExceededError(VideoGeniusException):
    """Quota exceeded error."""

    def __init__(self, resource: str, message: str = "Quota exceeded", **details: Any):
        super().__init__(
            message=message,
            status_code=429,
            error_code="QUOTA_EXCEEDED",
            details={"resource": resource, **details},
        )
