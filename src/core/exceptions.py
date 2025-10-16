"""
Core domain exceptions.
"""

from typing import Any, Dict, Optional


class DomainException(Exception):
    """Base exception for domain-specific errors."""

    def __init__(
        self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class ValidationError(DomainException):
    """Raised when data validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class NotFoundError(DomainException):
    """Raised when a resource is not found."""

    def __init__(
        self, resource: str, resource_id: str, details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource} with id {resource_id} not found"
        super().__init__(message, "NOT_FOUND", details)


class ConflictError(DomainException):
    """Raised when there's a conflict with existing data."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFLICT", details)


class ExternalServiceError(DomainException):
    """Raised when an external service fails."""

    def __init__(self, service: str, details: Optional[Dict[str, Any]] = None):
        message = f"External service {service} failed"
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)


class ConfigurationError(DomainException):
    """Raised when there's a configuration issue."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIGURATION_ERROR", details)
