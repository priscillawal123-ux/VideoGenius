"""
Custom exceptions for video generation domain.
"""

from src.videos.constants import ErrorCode


class VideoGenerationError(Exception):
    """Base exception for video generation errors."""

    def __init__(self, message: str, error_code: ErrorCode):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class InvalidTopicError(VideoGenerationError):
    """Raised when topic is invalid."""

    def __init__(self, message: str = "Invalid topic provided"):
        super().__init__(message, ErrorCode.INVALID_TOPIC)


class InvalidDurationError(VideoGenerationError):
    """Raised when duration is invalid."""

    def __init__(self, message: str = "Invalid duration provided"):
        super().__init__(message, ErrorCode.INVALID_DURATION)


class InvalidStyleError(VideoGenerationError):
    """Raised when style is invalid."""

    def __init__(self, message: str = "Invalid video style provided"):
        super().__init__(message, ErrorCode.INVALID_STYLE)


class ScriptGenerationError(VideoGenerationError):
    """Raised when script generation fails."""

    def __init__(self, message: str = "Failed to generate video script"):
        super().__init__(message, ErrorCode.SCRIPT_GENERATION_FAILED)


class VideoGenerationFailedError(VideoGenerationError):
    """Raised when video generation fails."""

    def __init__(self, message: str = "Failed to generate video"):
        super().__init__(message, ErrorCode.VIDEO_GENERATION_FAILED)


class StorageUploadError(VideoGenerationError):
    """Raised when storage upload fails."""

    def __init__(self, message: str = "Failed to upload video to storage"):
        super().__init__(message, ErrorCode.STORAGE_UPLOAD_FAILED)


class JobNotFoundError(VideoGenerationError):
    """Raised when job is not found."""

    def __init__(self, job_id: str):
        message = f"Video generation job {job_id} not found"
        super().__init__(message, ErrorCode.JOB_NOT_FOUND)


class ConcurrentJobsLimitExceededError(VideoGenerationError):
    """Raised when concurrent jobs limit is exceeded."""

    def __init__(self, message: str = "Maximum concurrent jobs limit exceeded"):
        super().__init__(message, ErrorCode.CONCURRENT_JOBS_LIMIT_EXCEEDED)
