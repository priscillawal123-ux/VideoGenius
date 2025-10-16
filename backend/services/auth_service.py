"""
Authentication service for Video Genius API.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.models.user import TokenData, UserInDB

# Password hashing context
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        exp: datetime = datetime.fromtimestamp(payload.get("exp", 0))
        if email is None:
            return None
        return TokenData(email=email, exp=exp)
    except JWTError:
        return None


# Mock user database - In production, this would be a real database
_mock_users_db = {
    "user@example.com": UserInDB(
        id=1,
        email="user@example.com",
        full_name="Example User",
        hashed_password=get_password_hash("pass123"),
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
}


def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Get user by email from database."""
    return _mock_users_db.get(email)


def create_user(email: str, full_name: str, password: str) -> UserInDB:
    """Create a new user."""
    if email in _mock_users_db:
        raise ValueError("User already exists")

    user_id = len(_mock_users_db) + 1
    hashed_password = get_password_hash(password)
    user = UserInDB(
        id=user_id,
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    _mock_users_db[email] = user
    return user


def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    """Authenticate user with email and password."""
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
