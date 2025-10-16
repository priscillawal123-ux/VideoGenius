"""
Video generation API routes.
"""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from backend.core.config import get_settings
from backend.database.bigquery_client import BigQueryClient
from backend.services.script_generator import ScriptGeneratorService
from backend.services.video_generator import VideoGeneratorService
from backend.services.cloud_tasks_client import CloudTasksClient
from backend.services.pubsub_client import PubSubClient
from backend.storage.cloud_storage import CloudStorageService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/videos", tags=["videos"])

settings = get_settings()


class VideoStyle(str, Enum):
    """Available video styles."""

    EDUCATIONAL = "educational"
    ENTERTAINING = "entertaining"
    DOCUMENTARY = "documentary"
    TUTORIAL = "tutorial"


class VideoGenerationRequest(BaseModel):
    """Request model for video generation."""

    topic: str = Field(
        ..., min_length=10, max_length=200, description="Video topic or subject"
    )
    duration_seconds: int = Field(
        ..., ge=30, le=600, description="Target video duration (30-600 seconds)"
    )
    style: VideoStyle = Field(default=VideoStyle.EDUCATIONAL, description="Video style")
    additional_context: Optional[str] = Field(
        None, max_length=500, description="Additional context or requirements"
    )
    tags: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="Video tags",
    )

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tags format."""
        return [tag.lower().strip() for tag in v if tag.strip()]


class VideoGenerationResponse(BaseModel):
    """Response model for video generation."""

    job_id: str = Field(..., description="Generation job ID")
    status: str = Field(..., description="Job status")
    estimated_completion_time: int = Field(..., description="Estimated time in seconds")
    message: str = Field(..., description="Status message")


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


def get_cloud_tasks_client() -> CloudTasksClient:
    """Dependency to get Cloud Tasks client."""
    return CloudTasksClient(
        project_id=settings.google_project_id,
        location=settings.vertex_ai_location,
        queue_name="video-generation-queue",
    )


def get_pubsub_client() -> Optional[PubSubClient]:
    """Dependency to get Pub/Sub client."""
    try:
        return PubSubClient(project_id=settings.google_project_id)
    except Exception as e:
        logger.warning(f"Failed to initialize Pub/Sub client: {e}")
        # Return a mock client that does nothing for local development
        return None


@router.post(
    "/generate",
    response_model=VideoGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate new video",
    description="""
    Initiate asynchronous video generation process using AI.

    This endpoint starts the video creation pipeline:
    1. **Blueprint Generation**: AI creates detailed video blueprint/script using Pub/Sub
    2. **Script Generation**: AI creates engaging script using Vertex AI
    3. **Content Analysis**: Script is analyzed for optimal video structure
    4. **Asset Creation**: Visual assets and audio are generated
    5. **Video Rendering**: Final video is assembled and rendered
    6. **Storage Upload**: Completed video is uploaded to Google Drive

    **Process Duration**: Typically 5-10x the requested video duration
    **Supported Formats**: MP4, AVI, MOV, MKV
    **Max Duration**: 10 minutes per video

    **Rate Limits**: 10 videos per hour for free users
    """,
    responses={
        202: {
            "description": "Video generation started successfully",
            "content": {
                "application/json": {
                    "example": {
                        "job_id": "vg_1234567890_abc123",
                        "status": "queued",
                        "estimated_completion_time": 720,
                        "message": "Video generation started. Job ID: vg_1234567890_abc123",
                    }
                }
            },
        },
        400: {
            "description": "Invalid request parameters",
            "content": {
                "application/json": {
                    "example": {"detail": "Topic must be between 10 and 200 characters"}
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to initiate video generation"}
                }
            },
        },
    },
)
async def generate_video(
    request: VideoGenerationRequest,
    script_service: ScriptGeneratorService = Depends(get_script_service),
    video_service: VideoGeneratorService = Depends(get_video_service),
    db_client: BigQueryClient = Depends(get_db_client),
    cloud_tasks_client: CloudTasksClient = Depends(get_cloud_tasks_client),
) -> VideoGenerationResponse:
    """Generate a new video based on provided parameters.

    This endpoint initiates an asynchronous video generation process:
    1. Generates script using Vertex AI
    2. Creates visual assets
    3. Renders final video
    4. Uploads to Cloud Storage

    Args:
        request: Video generation parameters
        script_service: Script generation service
        video_service: Video generation service
        db_client: BigQuery client
        cloud_tasks_client: Cloud Tasks client

    Returns:
        Generation job details

    Raises:
        HTTPException: If generation cannot be initiated
    """
    try:
        # Create job record
        job_id = await db_client.create_job_record(
            job_type="video_generation",
            parameters=request.dict(),
            user_id="anonymous",  # TODO: Add user authentication
        )

        # Estimate completion time based on duration
        estimated_time = estimate_generation_time(request.duration_seconds)

        # TODO: Add Pub/Sub blueprint generation here
        logger.info(f"Blueprint generation would be triggered for job {job_id}")

        # Then queue video generation task in Cloud Tasks
        task_payload = {
            "job_id": job_id,
            "request": request.dict(),
        }
        await cloud_tasks_client.create_task(payload=task_payload)

        logger.info(f"Video generation queued: {job_id} for topic: {request.topic}")

        return VideoGenerationResponse(
            job_id=job_id,
            status="queued",
            estimated_completion_time=estimated_time,
            message=f"Video generation started. Job ID: {job_id}",
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Generation initiation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate video generation",
        )


@router.get(
    "/{job_id}/status",
    response_model=Dict[str, Any],
    summary="Get generation status",
    description="""
    Check the current status of a video generation job.

    Returns detailed information about the generation process including:
    - Current status (queued, generating_script, generating_video, completed, failed)
    - Progress percentage
    - Estimated completion time
    - Video URL (when completed)
    - Error details (if failed)

    **Status Values**:
    - `queued`: Job is waiting to be processed
    - `generating_script`: AI is creating the video script
    - `generating_video`: Video assets are being created and assembled
    - `completed`: Video generation finished successfully
    - `failed`: Generation failed (check error field for details)
    """,
    responses={
        200: {
            "description": "Job status retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "job_id": "vg_1234567890_abc123",
                        "status": "completed",
                        "progress": 100,
                        "video_url": "https://drive.google.com/file/d/abc123...",
                        "created_at": "2024-01-15T10:30:00Z",
                        "completed_at": "2024-01-15T10:45:00Z",
                    }
                }
            },
        },
        404: {
            "description": "Job not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Job vg_invalid_id not found"}
                }
            },
        },
    },
)
async def get_generation_status(
    job_id: str, db_client: BigQueryClient = Depends(get_db_client)
) -> Dict[str, Any]:
    """Get status of video generation job.

    Args:
        job_id: Generation job ID
        db_client: BigQuery client

    Returns:
        Job status details

    Raises:
        HTTPException: If job not found
    """
    try:
        # Query BigQuery for job status
        query = f"""
        SELECT * FROM `{settings.google_project_id}.{settings.bigquery_dataset}.video_jobs`
        WHERE job_id = @job_id
        """

        job = await db_client.query_single_row(query, {"job_id": job_id})

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} not found"
            )

        return job

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve status",
        )


def estimate_generation_time(duration: int) -> int:
    """Estimate generation time based on video duration.

    Args:
        duration: Video duration in seconds

    Returns:
        Estimated time in seconds
    """
    # Rough estimate: 5x the video duration + base overhead
    return (duration * 5) + 120
