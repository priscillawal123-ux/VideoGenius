"""
FastAPI router for video generation endpoints.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from src.database.bigquery_client import BigQueryClient
from src.videos.dependencies import (
    get_db_client,
    get_video_service,
    validate_job_exists,
)
from src.videos.schemas import (
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoJobStatus,
)
from src.videos.service import VideoGenerationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/videos", tags=["videos"])


@router.post(
    "/generate",
    response_model=VideoGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate new video",
    description="Initiate video generation process using AI",
)
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks,
    video_service: VideoGenerationService = Depends(get_video_service),
    db_client: BigQueryClient = Depends(get_db_client),
) -> VideoGenerationResponse:
    """Generate a new video based on provided parameters.

    This endpoint initiates an asynchronous video generation process:
    1. Generates script using Vertex AI
    2. Creates visual assets
    3. Renders final video
    4. Uploads to Cloud Storage

    Args:
        request: Video generation parameters
        background_tasks: FastAPI background tasks
        video_service: Video generation service
        db_client: BigQuery client

    Returns:
        Generation job details

    Raises:
        HTTPException: If generation cannot be initiated
    """
    try:
        # Create job record
        job_id = await db_client.create_job_record(
            job_type="video_generation",
            parameters=request.model_dump(),
            user_id="anonymous",  # TODO: Add user authentication
        )

        # Estimate completion time
        estimated_time = await video_service.estimate_generation_time(
            request.duration_seconds
        )

        # Queue background task
        background_tasks.add_task(
            process_video_generation,
            job_id=job_id,
            request=request,
            video_service=video_service,
            db_client=db_client,
        )

        logger.info(f"Video generation initiated: {job_id} for topic: {request.topic}")

        return VideoGenerationResponse(
            job_id=job_id,
            status="queued",
            estimated_completion_time=estimated_time,
            message=f"Video generation started. Job ID: {job_id}",
        )

    except Exception as e:
        logger.error(f"Generation initiation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate video generation",
        )


@router.get(
    "/{job_id}/status",
    response_model=VideoJobStatus,
    summary="Get generation status",
    description="Check status of video generation job",
)
async def get_generation_status(
    job: Dict[str, Any] = Depends(validate_job_exists),
) -> VideoJobStatus:
    """Get status of video generation job.

    Args:
        job: Validated job data

    Returns:
        Job status details
    """
    return VideoJobStatus(**job)


async def process_video_generation(
    job_id: str,
    request: VideoGenerationRequest,
    video_service: VideoGenerationService,
    db_client: BigQueryClient,
) -> None:
    """Background task to process video generation."""
    try:
        logger.info(f"Processing video generation for job {job_id}")

        # Update status to generating script
        await db_client.update_job_status(job_id, "generating_script")

        # Generate video
        result = await video_service.generate_video(
            job_id=job_id,
            topic=request.topic,
            duration_seconds=request.duration_seconds,
            style=request.style.value,
            additional_context=request.additional_context,
        )

        # Update job with results
        await db_client.update_job_data(
            job_id,
            {
                "video_url": result["video_url"],
                "script": result["script_data"],
            },
        )

        # Mark as completed
        await db_client.update_job_status(job_id, "completed")

        logger.info(f"Video generation completed: {job_id}")

    except Exception as e:
        logger.error(f"Video generation failed for {job_id}: {e}")
        await db_client.update_job_status(job_id, "failed", error=str(e))
