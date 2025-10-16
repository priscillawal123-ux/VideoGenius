"""
Authentication configuration.
"""

from datetime import timedelta

from pydantic import Field

from src.core.models import CustomModel


class AuthConfig(CustomModel):
    """Configuration for authentication features."""

    # JWT settings
    jwt_secret_key: str = Field(default="change-me-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    jwt_refresh_token_expire_days: int = Field(default=30)

    # Password settings
    password_min_length: int = Field(default=8)
    password_require_uppercase: bool = Field(default=True)
    password_require_lowercase: bool = Field(default=True)
    password_require_digits: bool = Field(default=True)
    password_require_special_chars: bool = Field(default=True)

    # OAuth settings (future use)
    google_oauth_client_id: str | None = Field(default=None)
    google_oauth_client_secret: str | None = Field(default=None)

    # Session settings
    session_cookie_name: str = Field(default="video_genius_session")
    session_max_age: int = Field(default=86400)  # 24 hours
    session_secure: bool = Field(default=True)
    session_httponly: bool = Field(default=True)

    # Rate limiting
    login_rate_limit: str = Field(default="5/minute")
    api_rate_limit: str = Field(default="100/minute")

    @property
    def jwt_access_token_expire_timedelta(self) -> timedelta:
        """Get access token expiration as timedelta."""
        return timedelta(minutes=self.jwt_access_token_expire_minutes)

    @property
    def jwt_refresh_token_expire_timedelta(self) -> timedelta:
        """Get refresh token expiration as timedelta."""
        return timedelta(days=self.jwt_refresh_token_expire_days)
