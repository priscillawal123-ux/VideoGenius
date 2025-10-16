"""
Authentication domain service.
"""

from datetime import datetime, timedelta
from typing import Optional

import jwt
from passlib.context import CryptContext

from src.auth.constants import (
    DEFAULT_REFRESH_TOKEN_EXPIRY,
    DEFAULT_TOKEN_EXPIRY,
    TokenType,
    UserRole,
)
from src.auth.exceptions import (
    AccountDisabledError,
    InsufficientPermissionsError,
    InvalidTokenError,
    TokenExpiredError,
)
from src.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    PasswordResetConfirm,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from src.core.settings import get_config


class AuthService:
    """Authentication service with JWT token management."""

    def __init__(self):
        self.config = get_config().auth
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def _hash_password(self, password: str) -> str:
        """Hash a password."""
        return self.pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def _generate_token(
        self, user_id: str, token_type: TokenType, expiry_seconds: Optional[int] = None
    ) -> str:
        """Generate a JWT token."""
        if expiry_seconds is None:
            expiry_seconds = (
                DEFAULT_TOKEN_EXPIRY
                if token_type == TokenType.ACCESS
                else DEFAULT_REFRESH_TOKEN_EXPIRY
            )

        expire = datetime.utcnow() + timedelta(seconds=expiry_seconds)
        payload = {
            "sub": user_id,
            "type": token_type.value,
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        return jwt.encode(
            payload, self.config.jwt_secret_key, algorithm=self.config.jwt_algorithm
        )

    def _decode_token(self, token: str) -> dict:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.config.jwt_secret_key,
                algorithms=[self.config.jwt_algorithm],
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.InvalidTokenError:
            raise InvalidTokenError()

    async def authenticate_user(self, login_data: LoginRequest) -> UserResponse:
        """Authenticate a user with email and password."""
        # This would typically query the database
        # For now, we'll raise an exception as database integration is pending
        raise NotImplementedError("Database integration required")

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        # This would typically save to database
        # For now, we'll raise an exception as database integration is pending
        raise NotImplementedError("Database integration required")

    async def get_user_by_id(self, user_id: str) -> UserResponse:
        """Get user by ID."""
        # This would typically query the database
        # For now, we'll raise an exception as database integration is pending
        raise NotImplementedError("Database integration required")

    async def update_user(self, user_id: str, update_data: UserUpdate) -> UserResponse:
        """Update user information."""
        # This would typically update the database
        # For now, we'll raise an exception as database integration is pending
        raise NotImplementedError("Database integration required")

    async def delete_user(self, user_id: str) -> None:
        """Delete a user."""
        # This would typically delete from database
        # For now, we'll raise an exception as database integration is pending
        raise NotImplementedError("Database integration required")

    async def change_password(
        self, user_id: str, password_data: ChangePasswordRequest
    ) -> None:
        """Change user password."""
        # This would typically update the database
        # For now, we'll raise an exception as database integration is pending
        raise NotImplementedError("Database integration required")

    async def generate_tokens(self, user: UserResponse) -> TokenResponse:
        """Generate access and refresh tokens for a user."""
        access_token = self._generate_token(user.id, TokenType.ACCESS)
        refresh_token = self._generate_token(user.id, TokenType.REFRESH)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=DEFAULT_TOKEN_EXPIRY,
            user=user,
        )

    async def refresh_access_token(
        self, refresh_data: RefreshTokenRequest
    ) -> TokenResponse:
        """Refresh access token using refresh token."""
        payload = self._decode_token(refresh_data.refresh_token)

        if payload.get("type") != TokenType.REFRESH.value:
            raise InvalidTokenError()

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError()

        # Get user from database
        user = await self.get_user_by_id(user_id)

        # Generate new tokens
        return await self.generate_tokens(user)

    async def validate_token(
        self, token: str, token_type: TokenType = TokenType.ACCESS
    ) -> str:
        """Validate a token and return the user ID."""
        payload = self._decode_token(token)

        if payload.get("type") != token_type.value:
            raise InvalidTokenError()

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError()

        return user_id

    async def get_current_user(self, token: str) -> UserResponse:
        """Get current user from access token."""
        user_id = await self.validate_token(token, TokenType.ACCESS)
        return await self.get_user_by_id(user_id)

    async def initiate_password_reset(self, email: str) -> None:
        """Initiate password reset process."""
        # This would typically send an email
        # For now, we'll raise an exception as email integration is pending
        raise NotImplementedError("Email integration required")

    async def reset_password(self, reset_data: PasswordResetConfirm) -> None:
        """Reset user password using reset token."""
        # This would typically validate token and update password
        # For now, we'll raise an exception as database integration is pending
        raise NotImplementedError("Database integration required")

    async def validate_user_permissions(
        self, user: UserResponse, required_role: UserRole
    ) -> None:
        """Validate that user has required permissions."""
        if not user.is_active:
            raise AccountDisabledError()

        role_hierarchy = {
            UserRole.USER: 1,
            UserRole.PREMIUM_USER: 2,
            UserRole.ADMIN: 3,
        }

        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        if user_level < required_level:
            raise InsufficientPermissionsError(required_role.value)
