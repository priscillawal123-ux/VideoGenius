"""
Database domain constants.
"""

from enum import Enum


class DatabaseProvider(str, Enum):
    """Supported database providers."""

    BIGQUERY = "bigquery"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


class QueryType(str, Enum):
    """Types of database queries."""

    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"


class DatabaseErrorCode(str, Enum):
    """Database error codes."""

    CONNECTION_FAILED = "CONNECTION_FAILED"
    QUERY_FAILED = "QUERY_FAILED"
    TRANSACTION_FAILED = "TRANSACTION_FAILED"
    TIMEOUT = "TIMEOUT"
    INVALID_QUERY = "INVALID_QUERY"
    PERMISSION_DENIED = "PERMISSION_DENIED"


# Connection settings
DEFAULT_CONNECTION_TIMEOUT = 30  # seconds
DEFAULT_QUERY_TIMEOUT = 300  # seconds
DEFAULT_MAX_CONNECTIONS = 10
DEFAULT_CONNECTION_POOL_SIZE = 5
