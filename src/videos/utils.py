"""
Video domain configuration utilities.
"""

from src.core.settings import get_config


def get_video_config():
    """Get video-specific configuration."""
    return get_config().videos


def get_video_limits():
    """Get video generation limits."""
    config = get_video_config()
    return {
        "max_duration": config.max_video_duration,
        "min_duration": config.min_video_duration,
        "max_topic_length": config.max_topic_length,
        "max_additional_context_length": config.max_additional_context_length,
        "max_tags_count": config.max_tags_count,
    }


def get_video_timeouts():
    """Get video processing timeouts."""
    config = get_video_config()
    return {
        "script_generation_timeout": config.script_generation_timeout,
        "video_rendering_timeout": config.video_rendering_timeout,
    }
