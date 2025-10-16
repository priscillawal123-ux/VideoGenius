"""
Storage domain exceptions.
"""

from typing import Optional

from src.core.exceptions import DomainException
from src.storage.constants import StorageErrorCode


class StorageError(DomainException):
    """Base exception for storage errors."""

    def __init__(
        self, message: str, error_code: StorageErrorCode, details: Optional[dict] = None
    ):
        super().__init__(message, error_code.value, details)


class UploadError(StorageError):
    """Raised when file upload fails."""

    def __init__(self, file_path: str, details: Optional[dict] = None):
        message = f"Failed to upload file: {file_path}"
        super().__init__(message, StorageErrorCode.UPLOAD_FAILED, details)


class DownloadError(StorageError):
    """Raised when file download fails."""

    def __init__(self, file_path: str, details: Optional[dict] = None):
        message = f"Failed to download file: {file_path}"
        super().__init__(message, StorageErrorCode.DOWNLOAD_FAILED, details)


class DeleteError(StorageError):
    """Raised when file deletion fails."""

    def __init__(self, file_path: str, details: Optional[dict] = None):
        message = f"Failed to delete file: {file_path}"
        super().__init__(message, StorageErrorCode.DELETE_FAILED, details)


class NotFoundError(StorageError):
    """Raised when file is not found."""

    def __init__(self, file_path: str, details: Optional[dict] = None):
        message = f"File not found: {file_path}"
        super().__init__(message, StorageErrorCode.NOT_FOUND, details)


class PermissionDeniedError(StorageError):
    """Raised when storage permissions are insufficient."""

    def __init__(self, operation: str, file_path: str, details: Optional[dict] = None):
        message = f"Permission denied for {operation} on {file_path}"
        super().__init__(message, StorageErrorCode.PERMISSION_DENIED, details)


class InvalidPathError(StorageError):
    """Raised when file path is invalid."""

    def __init__(self, file_path: str, details: Optional[dict] = None):
        message = f"Invalid file path: {file_path}"
        super().__init__(message, StorageErrorCode.INVALID_PATH, details)
