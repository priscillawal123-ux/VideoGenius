"""
Integration tests for video generation API endpoints.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.api.main import create_application
from backend.database.bigquery_client import BigQueryClient
from backend.services.script_generator import ScriptGeneratorService
from backend.services.video_generator import VideoGeneratorService


@pytest.fixture
def client(mock_script_service, mock_video_service, mock_db_client):
    """Create test client with mocked dependencies."""
    from backend.api.routes.videos import (
        get_db_client,
        get_script_service,
        get_video_service,
    )

    app = create_application()

    # Override dependencies with mock services
    app.dependency_overrides[get_script_service] = lambda: mock_script_service
    app.dependency_overrides[get_video_service] = lambda: mock_video_service
    app.dependency_overrides[get_db_client] = lambda: mock_db_client

    return TestClient(app)


@pytest.fixture
def mock_script_service():
    """Mock ScriptGeneratorService."""
    service = MagicMock(spec=ScriptGeneratorService)
    service.generate_script = AsyncMock(
        return_value={
            "title": "Test Script",
            "hook": "Test hook",
            "script": "Test script content",
            "key_points": ["Point 1", "Point 2"],
            "metadata": {"topic": "Test", "duration": 60},
        }
    )
    return service


@pytest.fixture
def mock_video_service():
    """Mock VideoGeneratorService."""
    service = MagicMock(spec=VideoGeneratorService)
    service.generate_video_from_script = AsyncMock(
        return_value="https://storage.googleapis.com/test-bucket/test-video.mp4"
    )
    return service


@pytest.fixture
def mock_db_client():
    """Mock BigQueryClient."""
    client = MagicMock(spec=BigQueryClient)
    client.create_job_record = AsyncMock(return_value="test-job-123")
    client.update_job_status = AsyncMock()
    client.update_job_data = AsyncMock()
    client.query_single_row = AsyncMock(
        return_value={
            "job_id": "test-job-123",
            "status": "completed",
            "topic": "Test Topic",
            "video_url": "https://storage.googleapis.com/bucket/video.mp4",
        }
    )
    return client


class TestVideoGenerationAPI:
    """Integration tests for video generation API."""

    def test_generate_video_success(
        self, client, mock_script_service, mock_video_service, mock_db_client
    ):
        """Test successful video generation request."""
        # Given
        request_data = {
            "topic": "Machine Learning Basics",
            "duration_seconds": 120,
            "style": "educational",
            "additional_context": "Focus on beginners",
            "tags": ["AI", "ML"],
        }

        expected_job_id = "test-job-123"

        mock_db_client.create_job_record.return_value = expected_job_id

        # When
        response = client.post("/api/v1/videos/generate", json=request_data)

        # Then
        assert response.status_code == 202  # Accepted
        data = response.json()
        # Check that response has the expected structure
        assert data["status"] == "queued"
        assert data["estimated_completion_time"] == 720
        assert "job_id" in data
        assert "message" in data
        assert "Video generation started" in data["message"]

        # Verify job record creation was called
        mock_db_client.create_job_record.assert_called_once_with(
            job_type="video_generation",
            parameters={
                "topic": "Machine Learning Basics",
                "duration_seconds": 120,
                "style": "educational",  # Enum value
                "additional_context": "Focus on beginners",
                "tags": ["ai", "ml"],  # Lowercased
            },
            user_id="anonymous",
        )

    def test_generate_video_minimal_request(
        self, client, mock_script_service, mock_video_service, mock_db_client
    ):
        """Test video generation with minimal required fields."""
        request_data = {"topic": "Python Programming", "duration_seconds": 60}

        expected_job_id = "minimal-job-456"

        mock_db_client.create_job_record.return_value = expected_job_id

        response = client.post("/api/v1/videos/generate", json=request_data)

        assert response.status_code == 202
        data = response.json()
        # Check structure instead of exact values
        assert data["status"] == "queued"
        assert data["estimated_completion_time"] == 420  # 60 * 5 + 120
        assert "job_id" in data
        assert "message" in data

    def test_generate_video_validation_error_topic_too_short(self, client):
        """Test video generation with topic too short."""
        request_data = {"topic": "Hi", "duration_seconds": 60}  # Too short

        response = client.post("/api/v1/videos/generate", json=request_data)

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "topic" in str(data)

    def test_generate_video_validation_error_duration_too_short(self, client):
        """Test video generation with duration too short."""
        request_data = {"topic": "Valid Topic", "duration_seconds": 10}  # Too short

        response = client.post("/api/v1/videos/generate", json=request_data)

        assert response.status_code == 422
        data = response.json()
        assert "duration_seconds" in str(data)

    def test_generate_video_validation_error_duration_too_long(self, client):
        """Test video generation with duration too long."""
        request_data = {"topic": "Valid Topic", "duration_seconds": 700}  # Too long

        response = client.post("/api/v1/videos/generate", json=request_data)

        assert response.status_code == 422
        data = response.json()
        assert "duration_seconds" in str(data)

    def test_generate_video_validation_error_too_many_tags(self, client):
        """Test video generation with too many tags."""
        request_data = {
            "topic": "Valid Topic",
            "duration_seconds": 60,
            "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"],  # Too many
        }

        response = client.post("/api/v1/videos/generate", json=request_data)

        assert response.status_code == 422
        data = response.json()
        assert "tags" in str(data)

    def test_generate_video_invalid_style(self, client):
        """Test video generation with invalid style."""
        request_data = {
            "topic": "Valid Topic",
            "duration_seconds": 60,
            "style": "invalid_style",
        }

        response = client.post("/api/v1/videos/generate", json=request_data)

        assert response.status_code == 422
        data = response.json()
        assert "style" in str(data)

    def test_generate_video_additional_context_too_long(self, client):
        """Test video generation with additional context too long."""
        request_data = {
            "topic": "Valid Topic",
            "duration_seconds": 60,
            "additional_context": "x" * 501,  # Too long
        }

        response = client.post("/api/v1/videos/generate", json=request_data)

        assert response.status_code == 422
        data = response.json()
        assert "additional_context" in str(data)

    def test_get_generation_status_success(self, client, mock_db_client):
        """Test successful status retrieval."""
        job_id = "test-job-123"
        expected_status = {
            "job_id": job_id,
            "status": "completed",
            "topic": "Test Topic",
            "video_url": "https://storage.googleapis.com/bucket/video.mp4",
        }

        mock_db_client.query_single_row.return_value = expected_status

        response = client.get(f"/api/v1/videos/{job_id}/status")

        assert response.status_code == 200
        data = response.json()
        assert data == expected_status

    def test_get_generation_status_job_not_found(self, client, mock_db_client):
        """Test status retrieval for non-existent job."""
        job_id = "nonexistent-job"

        mock_db_client.query_single_row.return_value = None

        response = client.get(f"/api/v1/videos/{job_id}/status")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_get_generation_status_query_failure(self, client, mock_db_client):
        """Test status retrieval with query failure."""
        job_id = "test-job-123"

        mock_db_client.query_single_row.side_effect = Exception("Query failed")

        response = client.get(f"/api/v1/videos/{job_id}/status")

        # Query failures return 500
        assert response.status_code == 500
        data = response.json()
        assert "retrieve status" in data["detail"].lower()

    def test_generate_video_internal_error(self, client, mock_db_client):
        """Test video generation with internal error during job creation."""
        request_data = {"topic": "Valid Topic", "duration_seconds": 60}

        mock_db_client.create_job_record.side_effect = Exception("Database error")

        response = client.post("/api/v1/videos/generate", json=request_data)

        # Database errors during job creation return 500
        assert response.status_code == 500
        data = response.json()
        assert "initiate video generation" in data["detail"].lower()

    def test_generate_video_validation_error_internal(self, client, mock_db_client):
        """Test video generation with internal validation error during job creation."""
        request_data = {"topic": "Valid Topic", "duration_seconds": 60}

        mock_db_client.create_job_record.side_effect = ValueError("Invalid parameters")

        response = client.post("/api/v1/videos/generate", json=request_data)

        # Validation errors during job creation return 400
        assert response.status_code == 400
        data = response.json()
        assert "Invalid parameters" in data["detail"]
