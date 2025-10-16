"""
Authentication domain exceptions.
"""

from typing import Optional

from src.auth.constants import ErrorCode
from src.core.exceptions import DomainException


class AuthenticationError(DomainException):
    """Base exception for authentication errors."""

    def __init__(
        self, message: str, error_code: ErrorCode, details: Optional[dict] = None
    ):
        super().__init__(message, error_code.value, details)


class InvalidCredentialsError(AuthenticationError):
    """Raised when user provides invalid credentials."""

    def __init__(self, details: Optional[dict] = None):
        super().__init__(
            "Invalid username or password", ErrorCode.INVALID_CREDENTIALS, details
        )


class UserNotFoundError(AuthenticationError):
    """Raised when user is not found."""

    def __init__(self, user_id: Optional[str] = None, details: Optional[dict] = None):
        message = f"User not found: {user_id}" if user_id else "User not found"
        super().__init__(message, ErrorCode.USER_NOT_FOUND, details)


class UserAlreadyExistsError(AuthenticationError):
    """Raised when attempting to create a user that already exists."""

    def __init__(self, email: str, details: Optional[dict] = None):
        super().__init__(
            f"User with email {email} already exists",
            ErrorCode.USER_ALREADY_EXISTS,
            details,
        )


class InvalidTokenError(AuthenticationError):
    """Raised when JWT token is invalid."""

    def __init__(self, details: Optional[dict] = None):
        super().__init__("Invalid or malformed token", ErrorCode.INVALID_TOKEN, details)


class TokenExpiredError(AuthenticationError):
    """Raised when JWT token has expired."""

    def __init__(self, details: Optional[dict] = None):
        super().__init__("Token has expired", ErrorCode.TOKEN_EXPIRED, details)


class InsufficientPermissionsError(AuthenticationError):
    """Raised when user lacks required permissions."""

    def __init__(
        self, required_role: Optional[str] = None, details: Optional[dict] = None
    ):
        message = "Insufficient permissions"
        if required_role:
            message += f" - requires {required_role}"
        super().__init__(message, ErrorCode.INSUFFICIENT_PERMISSIONS, details)


class AccountDisabledError(AuthenticationError):
    """Raised when user account is disabled."""

    def __init__(self, details: Optional[dict] = None):
        super().__init__("Account is disabled", ErrorCode.ACCOUNT_DISABLED, details)
