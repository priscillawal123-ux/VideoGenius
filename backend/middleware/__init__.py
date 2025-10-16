"""
Middleware package for Video Genius API.
"""

from .auth_middleware import get_current_user

__all__ = ["get_current_user"]
