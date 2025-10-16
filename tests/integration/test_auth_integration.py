import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.main import app
from backend.models.user import UserCreate
from backend.services.auth_service import create_user
from backend.database.session import get_db


@pytest.mark.asyncio
class TestAuthenticationIntegration:
    """Integration tests for authentication endpoints."""

    @pytest.fixture
    async def client(self) -> AsyncClient:
        """Create test client."""
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            yield client

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession) -> dict:
        """Create a test user."""
        user_data = UserCreate(
            email="integration_test@example.com",
            full_name="Integration Test User",
            password="testpass123",
        )

        # Create user in database
        db_user = create_user(
            email=user_data.email,
            full_name=user_data.full_name,
            password=user_data.password,
        )

        return {
            "id": db_user.id,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "password": user_data.password,
        }

    async def test_health_check(self, client: AsyncClient) -> None:
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data

    async def test_user_registration_success(self, client: AsyncClient) -> None:
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "securepass123",
        }

        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 200

        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["is_active"] is True
        # Password should not be returned
        assert "password" not in data
        assert "hashed_password" not in data

    async def test_user_registration_duplicate_email(
        self, client: AsyncClient, test_user: dict
    ) -> None:
        """Test registration with duplicate email."""
        user_data = {
            "email": test_user["email"],  # Same email as test_user
            "full_name": "Another User",
            "password": "anotherpass123",
        }

        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "email" in data["detail"].lower() or "exists" in data["detail"].lower()

    async def test_user_registration_invalid_data(self, client: AsyncClient) -> None:
        """Test registration with invalid data."""
        # Test missing required fields
        response = await client.post("/auth/register", json={})
        assert response.status_code == 422  # Validation error

        # Test invalid email
        user_data = {
            "email": "invalid-email",
            "full_name": "Test User",
            "password": "testpass123",
        }
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 422

    async def test_user_login_success(
        self, client: AsyncClient, test_user: dict
    ) -> None:
        """Test successful user login."""
        login_data = {"username": test_user["email"], "password": test_user["password"]}

        response = await client.post("/auth/login", data=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    async def test_user_login_wrong_password(
        self, client: AsyncClient, test_user: dict
    ) -> None:
        """Test login with wrong password."""
        login_data = {"username": test_user["email"], "password": "wrongpassword"}

        response = await client.post("/auth/login", data=login_data)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "incorrect" in data["detail"].lower()

    async def test_user_login_nonexistent_user(self, client: AsyncClient) -> None:
        """Test login with nonexistent user."""
        login_data = {"username": "nonexistent@example.com", "password": "somepassword"}

        response = await client.post("/auth/login", data=login_data)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_get_current_user_authenticated(
        self, client: AsyncClient, test_user: dict
    ) -> None:
        """Test getting current user when authenticated."""
        # First login to get token
        login_data = {"username": test_user["email"], "password": test_user["password"]}
        login_response = await client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]

        # Now test getting current user
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["full_name"] == test_user["full_name"]
        assert "id" in data
        assert data["is_active"] is True

    async def test_get_current_user_no_token(self, client: AsyncClient) -> None:
        """Test getting current user without token."""
        response = await client.get("/auth/me")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_get_current_user_invalid_token(self, client: AsyncClient) -> None:
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_token_refresh_success(
        self, client: AsyncClient, test_user: dict
    ) -> None:
        """Test successful token refresh."""
        # First login to get token
        login_data = {"username": test_user["email"], "password": test_user["password"]}
        login_response = await client.post("/auth/login", data=login_data)
        original_token = login_response.json()["access_token"]

        # Now refresh token
        headers = {"Authorization": f"Bearer {original_token}"}
        response = await client.post("/auth/refresh", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

        # New token should be different from original
        new_token = data["access_token"]
        assert new_token != original_token
        assert isinstance(new_token, str)
        assert len(new_token) > 0

    async def test_token_refresh_no_token(self, client: AsyncClient) -> None:
        """Test token refresh without token."""
        response = await client.post("/auth/refresh")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_token_refresh_invalid_token(self, client: AsyncClient) -> None:
        """Test token refresh with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.post("/auth/refresh", headers=headers)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_protected_route_access(
        self, client: AsyncClient, test_user: dict
    ) -> None:
        """Test accessing protected routes with valid token."""
        # Login first
        login_data = {"username": test_user["email"], "password": test_user["password"]}
        login_response = await client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]

        # Test accessing a protected route (in this case, /auth/me is protected)
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code == 200

    async def test_protected_route_access_denied(self, client: AsyncClient) -> None:
        """Test accessing protected routes without authentication."""
        # Try to access protected route without token
        response = await client.get("/auth/me")
        assert response.status_code == 401

        # Try with invalid token
        headers = {"Authorization": "Bearer invalid"}
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code == 401

    async def test_complete_authentication_flow(self, client: AsyncClient) -> None:
        """Test complete authentication flow: register -> login -> access -> refresh."""
        # 1. Register new user
        user_data = {
            "email": "complete_flow@example.com",
            "full_name": "Complete Flow User",
            "password": "flowpass123",
        }
        register_response = await client.post("/auth/register", json=user_data)
        assert register_response.status_code == 200

        # 2. Login with new user
        login_data = {"username": user_data["email"], "password": user_data["password"]}
        login_response = await client.post("/auth/login", data=login_data)
        assert login_response.status_code == 200
        original_token = login_response.json()["access_token"]

        # 3. Access protected resource
        headers = {"Authorization": f"Bearer {original_token}"}
        me_response = await client.get("/auth/me", headers=headers)
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["email"] == user_data["email"]

        # 4. Refresh token
        refresh_response = await client.post("/auth/refresh", headers=headers)
        assert refresh_response.status_code == 200
        new_token = refresh_response.json()["access_token"]
        assert new_token != original_token

        # 5. Verify new token works
        new_headers = {"Authorization": f"Bearer {new_token}"}
        me_response_2 = await client.get("/auth/me", headers=new_headers)
        assert me_response_2.status_code == 200
        assert me_response_2.json()["email"] == user_data["email"]
