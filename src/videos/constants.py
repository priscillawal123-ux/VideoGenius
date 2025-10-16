"""
Constants for video generation domain.
"""

from enum import Enum


class VideoStatus(str, Enum):
    """Video generation job status."""

    QUEUED = "queued"
    GENERATING_SCRIPT = "generating_script"
    GENERATING_VIDEO = "generating_video"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoStyle(str, Enum):
    """Available video styles."""

    EDUCATIONAL = "educational"
    ENTERTAINING = "entertaining"
    DOCUMENTARY = "documentary"
    TUTORIAL = "tutorial"


class ErrorCode(str, Enum):
    """Error codes for video operations."""

    INVALID_TOPIC = "INVALID_TOPIC"
    INVALID_DURATION = "INVALID_DURATION"
    INVALID_STYLE = "INVALID_STYLE"
    SCRIPT_GENERATION_FAILED = "SCRIPT_GENERATION_FAILED"
    VIDEO_GENERATION_FAILED = "VIDEO_GENERATION_FAILED"
    STORAGE_UPLOAD_FAILED = "STORAGE_UPLOAD_FAILED"
    JOB_NOT_FOUND = "JOB_NOT_FOUND"
    CONCURRENT_JOBS_LIMIT_EXCEEDED = "CONCURRENT_JOBS_LIMIT_EXCEEDED"


# Default values
DEFAULT_VIDEO_DURATION = 60
MAX_VIDEO_DURATION = 600
MIN_VIDEO_DURATION = 30

# Content limits
MAX_TOPIC_LENGTH = 200
MAX_ADDITIONAL_CONTEXT_LENGTH = 500
MAX_TAGS_COUNT = 5

# Processing timeouts (seconds)
SCRIPT_GENERATION_TIMEOUT = 300  # 5 minutes
VIDEO_RENDERING_TIMEOUT = 1800  # 30 minutes

# Estimation constants
BASE_PROCESSING_TIME = 120  # Base time in seconds
TIME_PER_DURATION_SECOND = 5.0  # Multiplier for duration
