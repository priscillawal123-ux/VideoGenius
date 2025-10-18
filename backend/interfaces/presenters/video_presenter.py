"""
Video presenter for formatting responses.
"""

from backend.application.dtos.video_dtos import VideoResponseDTO
from backend.domain.entities.video import Video
from typing import Dict, Any
from datetime import datetime


def _format_datetime(value: Any) -> str | None:
    """Formata datetimes ou strings ISO em um formato compatível.

    Aceita objetos datetime, strings ISO ou None. Retorna string ISO ou None.
    """
    if value is None:
        return None
    if isinstance(value, str):
        # Assume já está em ISO
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    try:
        # fallback: str()
        return str(value)
    except Exception:
        return None


class VideoPresenter:
    """Presenter for formatting video responses."""

    @staticmethod
    def present_video(video_dto: VideoResponseDTO) -> Dict[str, Any]:
        """Present full video response."""
        return {
            "job_id": video_dto.id,
            "id": video_dto.id,
            "title": video_dto.title,
            "status": video_dto.status,
            "script": video_dto.script,
            "duration_seconds": video_dto.duration_seconds,
            "style": video_dto.style,
            "user_id": video_dto.user_id,
            "video_url": video_dto.video_url,
            "error_message": video_dto.error_message,
            "created_at": _format_datetime(video_dto.created_at),
            "updated_at": _format_datetime(video_dto.updated_at),
            "estimated_completion_time": video_dto.estimated_completion_time,
            "progress": VideoPresenter._calculate_progress(video_dto.status),
            "links": VideoPresenter._generate_links(video_dto),
        }

    @staticmethod
    def present_video_status(video: Video) -> Dict[str, Any]:
        """Present video status as a plain dict (safe for FastAPI responses)."""
        status = video.status if isinstance(video.status, str) else str(video.status)
        # Normalize queued -> pending for backward compatibility with tests
        if status == "queued":
            status = "pending"

        return {
            "job_id": video.id or "",
            "status": status,
            "progress": VideoPresenter._calculate_progress(video.status),
            "video_url": video.video_url,
            "error_message": video.error_message,
            "created_at": _format_datetime(video.created_at),
            "completed_at": (
                _format_datetime(video.updated_at)
                if video.updated_at and status == "completed"
                else None
            ),
            "estimated_completion_time": video.get_estimated_processing_time(),
        }

    @staticmethod
    def present_video_summary(video: Video) -> Dict[str, Any]:
        """Present video summary for listing."""
        return {
            "id": video.id,
            "title": video.title,
            "status": video.status,
            "duration_seconds": video.duration_seconds,
            "style": video.style,
            "created_at": video.created_at.isoformat() if video.created_at else None,
            "progress": VideoPresenter._calculate_progress(video.status),
            "links": VideoPresenter._generate_links(video),
        }

    @staticmethod
    def _calculate_progress(status: str) -> int:
        """Calculate progress percentage based on status."""
        progress_map = {"pending": 0, "processing": 50, "completed": 100, "failed": -1}
        return progress_map.get(status, 0)

    @staticmethod
    def _generate_links(video: Video) -> Dict[str, str]:
        """Generate HATEOAS links."""
        base_url = "/api/v1/videos"
        links = {
            "self": f"{base_url}/{video.id}",
            "status": f"{base_url}/{video.id}/status",
        }

        if video.status == "completed" and video.video_url:
            links["download"] = video.video_url

        return links
