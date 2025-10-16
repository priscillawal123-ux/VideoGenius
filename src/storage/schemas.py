"""
Storage domain schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import Field

from src.core.models import CustomModel
from src.storage.constants import StorageProvider


class StorageConfig(CustomModel):
    """Configuration for storage services."""

    provider: StorageProvider
    bucket_name: Optional[str] = None
    base_path: str = ""
    credentials_path: Optional[str] = None
    upload_timeout: int = Field(default=300, ge=1, le=3600)
    download_timeout: int = Field(default=300, ge=1, le=3600)
    max_file_size: int = Field(default=100 * 1024 * 1024, ge=1024)  # 100MB default
    chunk_size: int = Field(default=8 * 1024 * 1024, ge=1024)  # 8MB default


class FileInfo(CustomModel):
    """Schema for file information."""

    path: str
    size: int
    content_type: Optional[str] = None
    etag: Optional[str] = None
    last_modified: Optional[datetime] = None
    created_at: Optional[datetime] = None


class UploadRequest(CustomModel):
    """Schema for file upload requests."""

    file_path: str
    content: bytes
    content_type: Optional[str] = None
    metadata: Optional[dict] = Field(default_factory=dict)


class UploadResponse(CustomModel):
    """Schema for upload responses."""

    success: bool
    file_path: str
    size: int
    etag: Optional[str] = None
    upload_time: float


class DownloadRequest(CustomModel):
    """Schema for file download requests."""

    file_path: str
    range_start: Optional[int] = None
    range_end: Optional[int] = None


class DownloadResponse(CustomModel):
    """Schema for download responses."""

    content: bytes
    content_type: Optional[str] = None
    size: int
    etag: Optional[str] = None
    last_modified: Optional[datetime] = None


class StorageHealth(CustomModel):
    """Schema for storage health status."""

    provider: StorageProvider
    is_connected: bool
    bucket_exists: bool
    last_check: datetime
    error_message: Optional[str] = None
