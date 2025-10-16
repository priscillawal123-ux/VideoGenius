"""
FastAPI dependencies for video generation domain.
"""

from typing import Any, Dict

from fastapi import Depends, HTTPException, status

from src.database.bigquery_client import BigQueryClient
from src.videos.exceptions import JobNotFoundError
from src.videos.service import VideoGenerationService


async def get_video_service() -> VideoGenerationService:
    """Dependency to get video generation service."""
    return VideoGenerationService()


async def get_db_client() -> BigQueryClient:
    """Dependency to get BigQuery client."""
    from src.core.settings import get_config

    config = get_config()

    return BigQueryClient(
        project_id=config.google_project_id,
        dataset_id=config.bigquery_dataset,
    )


async def validate_job_exists(
    job_id: str,
    db_client: BigQueryClient = Depends(get_db_client),
) -> Dict[str, Any]:
    """
    Validate that a video generation job exists.

    Args:
        job_id: Job identifier
        db_client: Database client

    Returns:
        Job data if found

    Raises:
        HTTPException: If job not found
    """
    try:
        query = f"""
        SELECT * FROM `{db_client.project_id}.{db_client.dataset_id}.video_jobs`
        WHERE job_id = @job_id
        """

        job = await db_client.query_single_row(query, {"job_id": job_id})

        if not job:
            raise JobNotFoundError(job_id)

        return job

    except JobNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating job: {str(e)}",
        )
