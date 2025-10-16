"""
Storage domain router.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.dependencies import get_current_active_user
from src.auth.schemas import UserResponse
from src.storage.dependencies import get_storage_service
from src.storage.schemas import (
    DownloadRequest,
    DownloadResponse,
    StorageHealth,
    UploadRequest,
    UploadResponse,
)
from src.storage.service import StorageService

router = APIRouter(prefix="/storage", tags=["storage"])


@router.get("/health", response_model=StorageHealth)
async def get_storage_health(
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
) -> StorageHealth:
    """Get storage health status."""
    try:
        health = await storage_service.health_check()
        return health
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}",
        )


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    upload_request: UploadRequest,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
) -> UploadResponse:
    """Upload a file to storage."""
    try:
        result = await storage_service.upload_file(upload_request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Upload failed: {str(e)}"
        )


@router.post("/download", response_model=DownloadResponse)
async def download_file(
    download_request: DownloadRequest,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
) -> DownloadResponse:
    """Download a file from storage."""
    try:
        result = await storage_service.download_file(download_request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Download failed: {str(e)}"
        )
