"""
Database domain schemas.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from src.core.models import CustomModel
from src.database.constants import DatabaseProvider, QueryType


class DatabaseConfig(CustomModel):
    """Configuration for database connections."""

    provider: DatabaseProvider
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    connection_string: Optional[str] = None
    connection_timeout: int = Field(default=30, ge=1, le=300)
    query_timeout: int = Field(default=300, ge=1, le=3600)
    max_connections: int = Field(default=10, ge=1, le=100)
    enable_ssl: bool = True
    ssl_cert_path: Optional[str] = None


class QueryRequest(CustomModel):
    """Schema for database query requests."""

    query: str
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    query_type: QueryType = QueryType.SELECT
    timeout: Optional[int] = None


class QueryResult(CustomModel):
    """Schema for database query results."""

    success: bool
    rows_affected: Optional[int] = None
    data: Optional[List[Dict[str, Any]]] = None
    execution_time: float
    query_id: str


class BigQueryJob(CustomModel):
    """Schema for BigQuery job information."""

    job_id: str
    project_id: str
    dataset_id: Optional[str] = None
    table_id: Optional[str] = None
    query: Optional[str] = None
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    bytes_processed: Optional[int] = None
    total_rows: Optional[int] = None


class DatabaseHealth(CustomModel):
    """Schema for database health status."""

    provider: DatabaseProvider
    is_connected: bool
    connection_time: Optional[float] = None
    last_check: datetime
    error_message: Optional[str] = None


class TableInfo(CustomModel):
    """Schema for table information."""

    name: str
    table_schema: str = Field(..., alias="schema")
    row_count: Optional[int] = None
    size_bytes: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
