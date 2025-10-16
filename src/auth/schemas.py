"""
Authentication domain schemas.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import EmailStr, Field

from src.auth.constants import UserRole
from src.core.models import CustomModel


class UserBase(CustomModel):
    """Base user schema."""

    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.USER
    is_active: bool = True
    email_verified: bool = False


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(CustomModel):
    """Schema for updating user information."""

    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    email_verified: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response data."""

    id: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None


class LoginRequest(CustomModel):
    """Schema for login requests."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(CustomModel):
    """Schema for token responses."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(CustomModel):
    """Schema for refresh token requests."""

    refresh_token: str


class PasswordResetRequest(CustomModel):
    """Schema for password reset requests."""

    email: EmailStr


class PasswordResetConfirm(CustomModel):
    """Schema for password reset confirmation."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class ChangePasswordRequest(CustomModel):
    """Schema for password change requests."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class AuthProviderInfo(CustomModel):
    """Schema for authentication provider information."""

    provider: str
    provider_id: str
    provider_data: dict = Field(default_factory=dict)


class UserWithProviders(UserResponse):
    """Schema for user with authentication providers."""

    providers: List[AuthProviderInfo] = Field(default_factory=list)
