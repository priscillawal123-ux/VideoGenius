"""
Unit tests for video API routes.
"""

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient


class TestVideoAPI:
    """Test cases for video API endpoints."""

    def test_generate_video_success(self, client: TestClient):
        """Test successful video generation request."""
        request_data = {
            "topic": "Introduction to Machine Learning",
            "duration_seconds": 120,
            "style": "educational",
            "additional_context": "Focus on practical applications",
            "tags": ["AI", "ML"],
        }

        with (
            patch("backend.api.routes.videos.get_db_client") as mock_get_db,
            patch("backend.api.routes.videos.get_script_service") as mock_get_script,
            patch("backend.api.routes.videos.get_video_service") as mock_get_video,
            patch("backend.api.routes.videos.BackgroundTasks") as mock_bg_tasks_class,
        ):

            # Mock the dependency functions
            mock_db = AsyncMock()
            mock_db.create_job_record.return_value = "test-job-123"
            mock_get_db.return_value = mock_db

            mock_script = MagicMock()
            mock_get_script.return_value = mock_script

            mock_video = MagicMock()
            mock_get_video.return_value = mock_video

            mock_bg_tasks = MagicMock()
            mock_bg_tasks_class.return_value = mock_bg_tasks

            response = client.post("/api/v1/videos/generate", json=request_data)
            assert response.status_code == 202
            data = response.json()
            assert data["job_id"] == "test-job-123"
            assert data["status"] == "queued"
            assert "estimated_completion_time" in data
            assert "Video generation started" in data["message"]

    def test_generate_video_validation_error_topic_too_short(self, client: TestClient):
        """Test video generation with topic too short."""
        request_data = {"topic": "Short", "duration_seconds": 120}

        response = client.post("/api/v1/videos/generate", json=request_data)
        assert response.status_code == 422

    def test_generate_video_validation_error_duration_too_short(
        self, client: TestClient
    ):
        """Test video generation with duration too short."""
        request_data = {
            "topic": "Introduction to Machine Learning",
            "duration_seconds": 10,
        }

        response = client.post("/api/v1/videos/generate", json=request_data)
        assert response.status_code == 422

    def test_generate_video_validation_error_duration_too_long(
        self, client: TestClient
    ):
        """Test video generation with duration too long."""
        request_data = {
            "topic": "Introduction to Machine Learning",
            "duration_seconds": 700,
        }

        response = client.post("/api/v1/videos/generate", json=request_data)
        assert response.status_code == 422

    def test_generate_video_validation_error_too_many_tags(self, client: TestClient):
        """Test video generation with too many tags."""
        request_data = {
            "topic": "Introduction to Machine Learning",
            "duration_seconds": 120,
            "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"],
        }

        response = client.post("/api/v1/videos/generate", json=request_data)
        assert response.status_code == 422

    def test_generate_video_invalid_style(self, client: TestClient):
        """Test video generation with invalid style."""
        request_data = {
            "topic": "Introduction to Machine Learning",
            "duration_seconds": 120,
            "style": "invalid_style",
        }

        response = client.post("/api/v1/videos/generate", json=request_data)
        assert response.status_code == 422

    def test_generate_video_additional_context_too_long(self, client: TestClient):
        """Test video generation with additional context too long."""
        request_data = {
            "topic": "Introduction to Machine Learning",
            "duration_seconds": 120,
            "additional_context": "x" * 600,
        }

        response = client.post("/api/v1/videos/generate", json=request_data)
        assert response.status_code == 422

    def test_generate_video_db_error(self, client: TestClient):
        """Test video generation with database error."""
        request_data = {
            "topic": "Introduction to Machine Learning",
            "duration_seconds": 120,
        }

        with (
            patch("backend.api.routes.videos.get_db_client") as mock_get_db,
            patch("backend.api.routes.videos.BackgroundTasks") as mock_bg_tasks_class,
        ):

            mock_db = AsyncMock()
            mock_db.create_job_record.side_effect = Exception(
                "Database connection failed"
            )
            mock_get_db.return_value = mock_db

            mock_bg_tasks = MagicMock()
            mock_bg_tasks_class.return_value = mock_bg_tasks

            response = client.post("/api/v1/videos/generate", json=request_data)
            assert response.status_code == 500
            data = response.json()
            assert "Failed to initiate video generation" in data["detail"]

    def test_get_generation_status_success(self, client: TestClient):
        """Test successful status retrieval."""
        job_data = {
            "job_id": "test-job-123",
            "status": "completed",
            "video_url": "https://storage.googleapis.com/bucket/video.mp4",
        }

        with patch("backend.api.routes.videos.get_db_client") as mock_get_db:
            mock_db = AsyncMock()
            mock_db.query_single_row.return_value = job_data
            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/videos/test-job-123/status")
            assert response.status_code == 200
            data = response.json()
            assert data["job_id"] == "test-job-123"
            assert data["status"] == "completed"

    def test_get_generation_status_not_found(self, client: TestClient):
        """Test status retrieval for non-existent job."""
        with patch("backend.api.routes.videos.get_db_client") as mock_db_client:
            mock_db = AsyncMock()
            mock_db.query_single_row.return_value = None
            mock_db_client.return_value = mock_db

            response = client.get("/api/v1/videos/non-existent-job/status")
            assert response.status_code == 404
            data = response.json()
            assert "not found" in data["detail"]

    def test_get_generation_status_db_error(self, client: TestClient):
        """Test status retrieval with database error."""
        with patch("backend.api.routes.videos.get_db_client") as mock_get_db:
            mock_db = AsyncMock()
            mock_db.query_single_row.side_effect = Exception(
                "Database connection failed"
            )
            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/videos/test-job-123/status")
            assert response.status_code == 500
            data = response.json()
            assert "Failed to retrieve status" in data["detail"]

    def test_estimate_generation_time(self):
        """Test generation time estimation."""
        from backend.api.routes.videos import estimate_generation_time

        # Test with 60 seconds duration
        estimated = estimate_generation_time(60)
        # Should be (60 * 5) + 120 = 420
        assert estimated == 420

        # Test with 120 seconds duration
        estimated = estimate_generation_time(120)
        # Should be (120 * 5) + 120 = 720
        assert estimated == 720
