"""
Constants for authentication domain.
"""

from enum import Enum


class UserRole(str, Enum):
    """User roles in the system."""

    ADMIN = "admin"
    USER = "user"
    PREMIUM_USER = "premium_user"


class AuthProvider(str, Enum):
    """Authentication providers."""

    LOCAL = "local"
    GOOGLE = "google"


class TokenType(str, Enum):
    """JWT token types."""

    ACCESS = "access"
    REFRESH = "refresh"


class ErrorCode(str, Enum):
    """Error codes for authentication operations."""

    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    ACCOUNT_DISABLED = "ACCOUNT_DISABLED"


# Password validation patterns
PASSWORD_PATTERN = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]"
PASSWORD_MIN_LENGTH = 8

# Rate limiting
LOGIN_RATE_LIMIT = "5/minute"
API_RATE_LIMIT = "100/minute"

# Session settings
SESSION_COOKIE_NAME = "video_genius_session"
SESSION_MAX_AGE = 86400  # 24 hours

# Default values
DEFAULT_TOKEN_EXPIRY = 3600  # 1 hour
DEFAULT_REFRESH_TOKEN_EXPIRY = 604800  # 7 days
DEFAULT_SESSION_TIMEOUT = 1800  # 30 minutes
