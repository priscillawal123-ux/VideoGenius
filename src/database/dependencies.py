"""
Database domain dependencies.
"""

from typing import Annotated

from fastapi import Depends

from src.core.settings import get_config
from src.database.schemas import DatabaseConfig
from src.database.service import DatabaseService, DatabaseServiceFactory


def get_database_config() -> DatabaseConfig:
    """Get database configuration from settings."""
    db_config = get_config().database
    return DatabaseConfig(**db_config.model_dump())


def get_database_service(
    config: Annotated[DatabaseConfig, Depends(get_database_config)],
) -> DatabaseService:
    """Get database service instance."""
    return DatabaseServiceFactory.create_service(config)
