"""
Video generation service with async operations.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

from backend.services.script_generator import ScriptGeneratorService
from backend.services.video_generator import VideoGeneratorService
from backend.storage.cloud_storage import CloudStorageService
from src.core.settings import get_config
from src.videos.constants import VideoStatus
from src.videos.exceptions import ScriptGenerationError, VideoGenerationFailedError

logger = logging.getLogger(__name__)
config = get_config()


class VideoGenerationService:
    """Service for handling video generation operations."""

    def __init__(
        self,
        script_service: Optional[ScriptGeneratorService] = None,
        video_service: Optional[VideoGeneratorService] = None,
        storage_service: Optional[CloudStorageService] = None,
    ):
        """Initialize video generation service."""
        self.script_service = script_service or ScriptGeneratorService(
            project_id=config.google_project_id,
            location=config.database.bigquery_location,
        )
        self.video_service = video_service or VideoGeneratorService(
            CloudStorageService(config.storage.cloud_storage_bucket)
        )
        self.storage_service = storage_service or CloudStorageService(
            config.storage.cloud_storage_bucket
        )

    async def generate_video(
        self,
        job_id: str,
        topic: str,
        duration_seconds: int,
        style: str,
        additional_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a complete video from topic.

        Args:
            job_id: Unique job identifier
            topic: Video topic
            duration_seconds: Target video duration
            style: Video style
            additional_context: Additional context for generation

        Returns:
            Dict containing video URL and metadata

        Raises:
            ScriptGenerationError: If script generation fails
            VideoGenerationFailedError: If video generation fails
        """
        try:
            logger.info(f"Starting video generation for job {job_id}")

            # Generate script
            script_data = await self._generate_script(
                topic=topic,
                duration_seconds=duration_seconds,
                style=style,
                additional_context=additional_context,
            )

            # Generate video from script
            video_url = await self._generate_video_from_script(
                script_data=script_data,
                job_id=job_id,
            )

            logger.info(f"Video generation completed for job {job_id}")

            return {
                "video_url": video_url,
                "script_data": script_data,
                "status": VideoStatus.COMPLETED,
            }

        except Exception as e:
            logger.error(f"Video generation failed for job {job_id}: {e}")
            raise VideoGenerationFailedError(f"Video generation failed: {str(e)}")

    async def _generate_script(
        self,
        topic: str,
        duration_seconds: int,
        style: str,
        additional_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate video script using AI.

        Args:
            topic: Video topic
            duration_seconds: Target duration
            style: Video style
            additional_context: Additional context

        Returns:
            Generated script data

        Raises:
            ScriptGenerationError: If script generation fails
        """
        try:
            logger.info(f"Generating script for topic: {topic}")

            script_data = await self.script_service.generate_script(
                topic=topic,
                duration_seconds=duration_seconds,
                style=style,
                additional_context=additional_context,
            )

            if not script_data:
                raise ScriptGenerationError("Script generation returned empty result")

            logger.info("Script generation completed successfully")
            return script_data

        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            raise ScriptGenerationError(f"Failed to generate script: {str(e)}")

    async def _generate_video_from_script(
        self,
        script_data: Dict[str, Any],
        job_id: str,
    ) -> str:
        """
        Generate video from script data.

        Args:
            script_data: Generated script data
            job_id: Job identifier for file naming

        Returns:
            Video URL in cloud storage

        Raises:
            VideoGenerationFailedError: If video generation fails
        """
        try:
            logger.info(f"Generating video from script for job {job_id}")

            video_url = await self.video_service.generate_video_from_script(
                script_data=script_data,
                job_id=job_id,
            )

            if not video_url:
                raise VideoGenerationFailedError("Video generation returned empty URL")

            logger.info(f"Video generation completed, URL: {video_url}")
            return video_url

        except Exception as e:
            logger.error(f"Video generation from script failed: {e}")
            raise VideoGenerationFailedError(f"Failed to generate video: {str(e)}")

    async def estimate_generation_time(self, duration_seconds: int) -> int:
        """
        Estimate total generation time based on video duration.

        Args:
            duration_seconds: Target video duration

        Returns:
            Estimated time in seconds
        """
        # Base time + time per duration second
        base_time = config.videos.base_processing_time
        time_per_second = config.videos.time_per_duration_second

        return int(base_time + (duration_seconds * time_per_second))
