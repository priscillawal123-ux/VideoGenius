"""
Database configuration.
"""

from pydantic import Field, PostgresDsn

from src.core.models import CustomModel


class DatabaseConfig(CustomModel):
    """Configuration for database connections."""

    # BigQuery
    google_project_id: str = Field(default="video-genius-dev")
    bigquery_dataset: str = Field(default="video_genius")
    bigquery_location: str = Field(default="us-central1")

    # PostgreSQL (if needed for metadata)
    postgres_url: PostgresDsn | None = Field(default=None)

    # Connection settings
    connection_pool_size: int = Field(default=10)
    connection_max_overflow: int = Field(default=20)
    connection_pool_timeout: int = Field(default=30)
    connection_pool_recycle: int = Field(default=3600)

    # Query settings
    query_timeout: int = Field(default=300)  # 5 minutes
    max_results_limit: int = Field(default=1000)

    # Migration settings
    alembic_config_path: str = Field(default="alembic.ini")
    migrations_path: str = Field(default="alembic/versions")
