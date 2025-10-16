"""
Authentication domain router.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.dependencies import (
    get_auth_service,
    get_current_active_user,
    get_current_admin_user,
)
from src.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from src.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    """Register a new user."""
    try:
        user = await auth_service.create_user(user_data)
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """Authenticate user and return tokens."""
    try:
        login_data = LoginRequest(email=form_data.username, password=form_data.password)
        user = await auth_service.authenticate_user(login_data)
        tokens = await auth_service.generate_tokens(user)
        return tokens
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """Refresh access token using refresh token."""
    try:
        tokens = await auth_service.refresh_access_token(refresh_data)
        return tokens
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
) -> UserResponse:
    """Get current user information."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    """Update current user information."""
    try:
        updated_user = await auth_service.update_user(current_user.id, update_data)
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Change current user password."""
    try:
        await auth_service.change_password(current_user.id, password_data)
        return {"message": "Password changed successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/reset-password-request")
async def request_password_reset(
    reset_data: PasswordResetRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Request password reset."""
    try:
        await auth_service.initiate_password_reset(reset_data.email)
        return {"message": "Password reset email sent"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    current_user: Annotated[UserResponse, Depends(get_current_admin_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> list[UserResponse]:
    """List all users (admin only)."""
    # This would need a method to list users in the service
    # For now, return empty list
    return []


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_admin_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    """Get user by ID (admin only)."""
    try:
        user = await auth_service.get_user_by_id(user_id)
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_admin_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    """Update user by ID (admin only)."""
    try:
        updated_user = await auth_service.update_user(user_id, update_data)
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_admin_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Delete user by ID (admin only)."""
    try:
        await auth_service.delete_user(user_id)
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
