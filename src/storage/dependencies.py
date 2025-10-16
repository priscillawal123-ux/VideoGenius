"""
Storage domain dependencies.
"""

from typing import Annotated

from fastapi import Depends

from src.core.settings import get_config
from src.storage.schemas import StorageConfig
from src.storage.service import StorageService, StorageServiceFactory


def get_storage_config() -> StorageConfig:
    """Get storage configuration from settings."""
    storage_config = get_config().storage
    return StorageConfig(
        provider=storage_config.provider, **storage_config.model_dump() # type: ignore
    )


def get_storage_service(
    config: Annotated[StorageConfig, Depends(get_storage_config)],
) -> StorageService:
    """Get storage service instance."""
    return StorageServiceFactory.create_service(config)
