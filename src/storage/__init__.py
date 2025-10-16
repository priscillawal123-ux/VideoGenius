"""
Storage domain package.
"""

from .constants import StorageProvider
from .dependencies import get_storage_service
from .exceptions import DownloadError, StorageError, UploadError
from .router import router as storage_router
from .schemas import DownloadRequest, StorageConfig, UploadRequest
from .service import CloudStorageService, StorageService

__all__ = [
    "StorageProvider",
    "StorageError",
    "UploadError",
    "DownloadError",
    "storage_router",
    "StorageConfig",
    "UploadRequest",
    "DownloadRequest",
    "StorageService",
    "CloudStorageService",
    "get_storage_service",
]
