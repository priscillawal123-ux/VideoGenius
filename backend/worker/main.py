"""Cloud Tasks worker for video generation processing."""

import logging
import json
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel

from backend.core.config import get_settings
from backend.core.monitoring import setup_monitoring
from backend.database.bigquery_client import BigQueryClient
from backend.services.script_generator import ScriptGeneratorService
from backend.services.video_generator import VideoGeneratorService
from backend.storage.cloud_storage import CloudStorageService

logger = logging.getLogger(__name__)
app = FastAPI(title="Video Generation Worker", version="1.0.0")

settings = get_settings()

# Setup monitoring
setup_monitoring(app)


class TaskPayload(BaseModel):
    """Payload for video generation task."""

    job_id: str
    request: Dict[str, Any]


def get_script_service() -> ScriptGeneratorService:
    """Dependency to get script generator service."""
    return ScriptGeneratorService(
        project_id=settings.google_project_id, location=settings.vertex_ai_location
    )


def get_video_service() -> VideoGeneratorService:
    """Dependency to get video generator service."""
    cloud_storage = CloudStorageService(settings.cloud_storage_bucket)
    return VideoGeneratorService(cloud_storage)


def get_db_client() -> BigQueryClient:
    """Dependency to get BigQuery client."""
    return BigQueryClient(
        project_id=settings.google_project_id, dataset_id=settings.bigquery_dataset
    )


@app.post("/process-video-generation")
async def process_video_generation_task(
    payload: TaskPayload,
    script_service: ScriptGeneratorService = Depends(get_script_service),
    video_service: VideoGeneratorService = Depends(get_video_service),
    db_client: BigQueryClient = Depends(get_db_client),
) -> Dict[str, str]:
    """Process video generation task from Cloud Tasks.

    Args:
        payload: Task payload with job_id and request data
        script_service: Script generation service
        video_service: Video generation service
        db_client: BigQuery client

    Returns:
        Success message

    Raises:
        HTTPException: If processing fails
    """
    job_id = payload.job_id
    request_data = payload.request

    # Reconstruct request object
    from backend.api.routes.videos import VideoGenerationRequest

    try:
        request = VideoGenerationRequest(**request_data)
    except Exception as e:
        logger.error(f"Invalid request data for job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid request data: {e}"
        )

    try:
        logger.info(f"Starting video generation for job: {job_id}")

        # Update status to generating_script
        await db_client.update_job_status(job_id, "generating_script")

        # Generate script
        script_data = await script_service.generate_script(
            topic=request.topic,
            duration_seconds=request.duration_seconds,
            style=request.style,
            additional_context=request.additional_context,
        )

        # Update with full script
        await db_client.update_job_data(job_id, {"script": script_data})

        # Update status to generating_video
        await db_client.update_job_status(job_id, "generating_video")

        # Generate video from script
        video_url = await video_service.generate_video_from_script(
            script_data=script_data, job_id=job_id
        )

        # Update job with video URL
        await db_client.update_job_data(
            job_id, {"video_url": video_url, "video_status": "completed"}
        )

        # Mark as completed
        await db_client.update_job_status(job_id, "completed")

        logger.info(f"Video generation completed for job: {job_id}")
        return {"status": "success", "message": f"Job {job_id} completed"}

    except Exception as e:
        logger.error(f"Video generation failed for job {job_id}: {e}")
        await db_client.update_job_status(job_id, "failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video generation failed: {e}",
        )


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    import os

    # Use PORT environment variable for Cloud Run compatibility
    port = int(os.getenv("PORT", "8081"))
    uvicorn.run(app, host="0.0.0.0", port=port)
