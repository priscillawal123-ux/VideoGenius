"""
Unit tests for API endpoints.
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Video Genius API" in data["message"]


def test_health_endpoint(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_buckets_success(client: TestClient):
    """Test successful bucket listing."""
    mock_bucket1 = MagicMock()
    mock_bucket1.name = "test-bucket-1"
    mock_bucket2 = MagicMock()
    mock_bucket2.name = "test-bucket-2"

    with patch("google.cloud.storage.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.list_buckets.return_value = [mock_bucket1, mock_bucket2]
        mock_client_class.return_value = mock_client

        response = client.get("/gcp/buckets")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert "test-bucket-1" in data
        assert "test-bucket-2" in data


def test_list_buckets_failure(client: TestClient):
    """Test bucket listing failure."""
    with patch("google.cloud.storage.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.list_buckets.side_effect = Exception("GCP connection failed")
        mock_client_class.return_value = mock_client

        response = client.get("/gcp/buckets")
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "HTTP_EXCEPTION"
        assert "Failed to access Cloud Storage" in data["message"]
