import logging
from typing import List

from fastapi import APIRouter, HTTPException
from google.cloud import storage

logger = logging.getLogger(__name__)

router = APIRouter(tags=["gcp"])


@router.get(
    "/buckets",
    response_model=List[str],
    summary="List Cloud Storage buckets",
    description="List all Cloud Storage buckets in the current project",
)
async def list_buckets() -> List[str]:
    """List Cloud Storage buckets.

    Returns:
        List of bucket names

    Raises:
        HTTPException: If GCP access fails
    """
    try:
        client = storage.Client()
        buckets = client.list_buckets()
        bucket_names = [bucket.name for bucket in buckets]
        logger.info(f"Listed {len(bucket_names)} buckets")
        return bucket_names
    except Exception as e:
        logger.error(f"Failed to list buckets: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to access Cloud Storage: {str(e)}"
        )
