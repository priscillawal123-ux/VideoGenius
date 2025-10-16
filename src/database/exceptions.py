"""
Database domain exceptions.
"""

from typing import Optional

from src.core.exceptions import DomainException
from src.database.constants import DatabaseErrorCode


class DatabaseError(DomainException):
    """Base exception for database errors."""

    def __init__(
        self,
        message: str,
        error_code: DatabaseErrorCode,
        details: Optional[dict] = None,
    ):
        super().__init__(message, error_code.value, details)


class ConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(self, provider: str, details: Optional[dict] = None):
        message = f"Failed to connect to {provider} database"
        super().__init__(message, DatabaseErrorCode.CONNECTION_FAILED, details)


class QueryError(DatabaseError):
    """Raised when a database query fails."""

    def __init__(self, query: str, details: Optional[dict] = None):
        message = f"Database query failed: {query[:100]}..."
        super().__init__(message, DatabaseErrorCode.QUERY_FAILED, details)


class TransactionError(DatabaseError):
    """Raised when a database transaction fails."""

    def __init__(self, operation: str, details: Optional[dict] = None):
        message = f"Database transaction failed during {operation}"
        super().__init__(message, DatabaseErrorCode.TRANSACTION_FAILED, details)


class TimeoutError(DatabaseError):
    """Raised when a database operation times out."""

    def __init__(
        self, operation: str, timeout_seconds: int, details: Optional[dict] = None
    ):
        message = f"Database operation '{operation}' timed out after {timeout_seconds} seconds"
        super().__init__(message, DatabaseErrorCode.TIMEOUT, details)


class InvalidQueryError(DatabaseError):
    """Raised when a query is invalid."""

    def __init__(self, query: str, reason: str, details: Optional[dict] = None):
        message = f"Invalid query: {reason}"
        super().__init__(message, DatabaseErrorCode.INVALID_QUERY, details)


class PermissionDeniedError(DatabaseError):
    """Raised when database permissions are insufficient."""

    def __init__(self, operation: str, details: Optional[dict] = None):
        message = f"Permission denied for database operation: {operation}"
        super().__init__(message, DatabaseErrorCode.PERMISSION_DENIED, details)
