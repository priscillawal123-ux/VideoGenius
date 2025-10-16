"""
Storage domain constants.
"""

from enum import Enum


class StorageProvider(str, Enum):
    """Supported storage providers."""

    GCS = "gcs"  # Google Cloud Storage
    GDRIVE = "gdrive"  # Google Drive
    S3 = "s3"  # Amazon S3
    AZURE = "azure"  # Azure Blob Storage
    LOCAL = "local"  # Local filesystem


class StorageErrorCode(str, Enum):
    """Storage error codes."""

    UPLOAD_FAILED = "UPLOAD_FAILED"
    DOWNLOAD_FAILED = "DOWNLOAD_FAILED"
    DELETE_FAILED = "DELETE_FAILED"
    NOT_FOUND = "NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    INVALID_PATH = "INVALID_PATH"


# Storage settings
DEFAULT_UPLOAD_TIMEOUT = 300  # seconds
DEFAULT_DOWNLOAD_TIMEOUT = 300  # seconds
DEFAULT_MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
DEFAULT_CHUNK_SIZE = 8 * 1024 * 1024  # 8MB
