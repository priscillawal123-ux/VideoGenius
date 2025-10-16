"""
Tests for authentication functionality.
"""

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


def test_register_user(client):
    """Test user registration."""
    user_data = {
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "password123",
    }

    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "created_at" in data


def test_login_user(client):
    """Test user login."""
    # First register a user
    user_data = {
        "email": "loginuser@example.com",
        "full_name": "Login User",
        "password": "password123",
    }
    client.post("/auth/register", json=user_data)

    # Then try to login
    login_data = {"email": user_data["email"], "password": user_data["password"]}

    response = client.post(
        "/auth/login",
        data={"username": login_data["email"], "password": login_data["password"]},
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """Test login with wrong password."""
    login_data = {
        "email": "user@example.com",  # This user exists in mock data
        "password": "wrongpassword",
    }

    response = client.post(
        "/auth/login",
        data={"username": login_data["email"], "password": login_data["password"]},
    )
    assert response.status_code == 401


def test_get_current_user(client):
    """Test getting current user info."""
    # First login to get token
    login_data = {
        "email": "user@example.com",  # Mock user
        "password": "pass123",  # Mock password
    }

    login_response = client.post(
        "/auth/login",
        data={"username": login_data["email"], "password": login_data["password"]},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Use token to get user info
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == "user@example.com"
    assert data["full_name"] == "Example User"


def test_get_current_user_no_token(client):
    """Test getting current user without token."""
    response = client.get("/auth/me")
    assert response.status_code == 401
