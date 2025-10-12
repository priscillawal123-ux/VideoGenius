"""
Unit tests for the main API application.

Tests basic functionality of the FastAPI application.
"""

from fastapi.testclient import TestClient


class TestMainAPI:
    """Test cases for the main FastAPI application."""

    def test_root_endpoint(self, client: TestClient):
        """Test the root endpoint returns correct response."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data

    def test_health_endpoint(self, client: TestClient):
        """Test the health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data

    def test_openapi_docs_available(self, client: TestClient):
        """Test that OpenAPI documentation is available."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert "info" in data
        assert "paths" in data
        assert data["info"]["title"] == "Video Genius API"

    def test_cors_headers(self, client: TestClient):
        """Test CORS headers are properly set."""
        response = client.options("/")

        # Check if CORS headers are present
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers"
        ]

        response_headers = {k.lower(): v for k, v in response.headers.items()}

        # At least one CORS header should be present
        has_cors = any(header in response_headers for header in cors_headers)
        assert has_cors, "CORS headers should be present"