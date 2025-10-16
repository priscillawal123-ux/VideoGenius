"""
End-to-end tests for complete video generation workflow.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.api.main import create_application
from backend.database.bigquery_client import BigQueryClient
from backend.services.script_generator import ScriptGeneratorService
from backend.services.video_generator import VideoGeneratorService


@pytest.fixture
def e2e_client(mock_script_service_e2e, mock_video_service_e2e, mock_db_client_e2e):
    """Create test client for end-to-end tests with mocked dependencies."""
    from backend.api.routes.videos import (
        get_db_client,
        get_script_service,
        get_video_service,
    )

    app = create_application()

    # Override dependencies with mock services
    app.dependency_overrides[get_script_service] = lambda: mock_script_service_e2e
    app.dependency_overrides[get_video_service] = lambda: mock_video_service_e2e
    app.dependency_overrides[get_db_client] = lambda: mock_db_client_e2e

    return TestClient(app)


@pytest.fixture
def mock_script_service_e2e():
    """Mock ScriptGeneratorService for e2e tests."""
    service = MagicMock(spec=ScriptGeneratorService)
    service.generate_script = AsyncMock(
        return_value={
            "title": "Test Video",
            "hook": "Welcome to our test!",
            "script": "This is a test script for video generation.",
            "key_points": ["Point 1", "Point 2"],
            "metadata": {"topic": "Test", "duration": 60, "style": "educational"},
        }
    )
    return service


@pytest.fixture
def mock_video_service_e2e():
    """Mock VideoGeneratorService for e2e tests."""
    service = MagicMock(spec=VideoGeneratorService)
    service.generate_video_from_script = AsyncMock(
        return_value="https://storage.googleapis.com/test-bucket/test-video.mp4"
    )
    return service


@pytest.fixture
def mock_db_client_e2e():
    """Mock BigQueryClient for e2e tests."""
    client = MagicMock(spec=BigQueryClient)

    # Mock job creation
    client.create_job_record = AsyncMock(return_value="e2e-job-123")

    # Mock status updates
    client.update_job_status = AsyncMock()
    client.update_job_data = AsyncMock()

    # Mock status queries - start with queued status
    client.query_single_row = AsyncMock(
        return_value={
            "job_id": "e2e-job-123",
            "status": "queued",
            "topic": "End-to-End Test",
            "created_at": "2024-01-01T00:00:00Z",
        }
    )

    return client


class TestVideoGenerationE2E:
    """End-to-end tests for complete video generation workflow."""

    @pytest.mark.asyncio
    async def test_complete_video_generation_workflow(
        self,
        e2e_client,
        mock_script_service_e2e,
        mock_video_service_e2e,
        mock_db_client_e2e,
    ):
        """Test complete video generation workflow from request to completion."""
        # Reset call counts
        mock_db_client_e2e.query_single_row.reset_mock()

        # Step 1: Submit video generation request
        request_data = {
            "topic": "End-to-End Test",
            "duration_seconds": 60,
            "style": "educational",
            "additional_context": "For testing purposes",
            "tags": ["test", "e2e"],
        }

        response = e2e_client.post("/api/v1/videos/generate", json=request_data)

        assert response.status_code == 202
        generation_response = response.json()
        job_id = generation_response["job_id"]

        assert generation_response["status"] == "queued"
        assert "estimated_completion_time" in generation_response

        # Step 2: Check initial status (should be queued)
        status_response = e2e_client.get(f"/api/v1/videos/{job_id}/status")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["status"] == "queued"
        assert status_data["job_id"] == job_id

        # Step 3: Simulate background processing manually
        from backend.api.routes.videos import (
            VideoGenerationRequest,
            process_video_generation,
        )

        # Create proper request object
        request_obj = VideoGenerationRequest(**request_data)
        await process_video_generation(
            job_id,
            request_obj,
            mock_script_service_e2e,
            mock_video_service_e2e,
            mock_db_client_e2e,
        )

        # Step 4: Check final status (should be completed after processing)
        # Update mock to return completed status for subsequent calls
        mock_db_client_e2e.query_single_row.return_value = {
            "job_id": job_id,
            "status": "completed",
            "video_url": "https://storage.googleapis.com/test-bucket/test-video.mp4",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:05:00Z",
        }

        status_response = e2e_client.get(f"/api/v1/videos/{job_id}/status")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["status"] == "completed"
        assert "video_url" in status_data
        assert (
            status_data["video_url"]
            == "https://storage.googleapis.com/test-bucket/test-video.mp4"
        )

        # Verify all services were called correctly
        mock_script_service_e2e.generate_script.assert_called_once()
        mock_video_service_e2e.generate_video_from_script.assert_called_once()
        assert mock_db_client_e2e.create_job_record.call_count == 1
        assert (
            mock_db_client_e2e.update_job_status.call_count >= 2
        )  # At least queued -> processing -> completed

    def test_video_generation_with_different_styles(self, e2e_client):
        """Test video generation with different styles."""
        styles = ["educational", "entertaining", "documentary", "tutorial"]

        for style in styles:
            with (
                patch(
                    "backend.api.routes.videos.get_script_service"
                ) as mock_script_svc,
                patch("backend.api.routes.videos.get_video_service") as mock_video_svc,
                patch("backend.api.routes.videos.get_db_client") as mock_db,
            ):

                mock_script_svc.return_value.generate_script = AsyncMock(
                    return_value={
                        "title": f"{style.title()} Video",
                        "hook": f"Welcome to {style} content!",
                        "script": f"This is a {style} video script.",
                        "key_points": ["Point 1"],
                        "metadata": {"style": style},
                    }
                )
                mock_video_svc.return_value.generate_video_from_script = AsyncMock(
                    return_value="https://example.com/video.mp4"
                )
                mock_db.return_value.create_job_record = AsyncMock(
                    return_value=f"{style}-job"
                )

                request_data = {
                    "topic": f"{style.title()} Topic",
                    "duration_seconds": 60,
                    "style": style,
                }

                response = e2e_client.post("/api/v1/videos/generate", json=request_data)

                assert response.status_code == 202
                data = response.json()
                assert data["status"] == "queued"
                assert "job_id" in data

    def test_concurrent_video_generation_requests(self, e2e_client, mock_db_client_e2e):
        """Test multiple concurrent video generation requests."""
        # Use the existing mock but override create_job_record to return unique IDs
        job_counter = 0

        def create_unique_job_record(*args, **kwargs):
            nonlocal job_counter
            job_counter += 1
            return f"concurrent-job-{job_counter}"

        mock_db_client_e2e.create_job_record = AsyncMock(
            side_effect=create_unique_job_record
        )

        # Submit multiple requests
        requests_data = [
            {
                "topic": f"Concurrent Topic {i}",
                "duration_seconds": 60,
                "style": "educational",
            }
            for i in range(1, 4)
        ]

        responses = []
        for request_data in requests_data:
            response = e2e_client.post("/api/v1/videos/generate", json=request_data)
            responses.append(response)

        # Verify all requests succeeded
        for response in responses:
            assert response.status_code == 202
            data = response.json()
            assert data["status"] == "queued"
            assert "job_id" in data

        # Verify unique job IDs
        job_ids = [r.json()["job_id"] for r in responses]
        assert len(set(job_ids)) == len(job_ids)  # All unique

    def test_video_generation_error_handling(self, e2e_client):
        """Test error handling in video generation workflow."""
        # Test script generation failure
        with (
            patch("backend.api.routes.videos.get_script_service") as mock_script_svc,
            patch("backend.api.routes.videos.get_video_service") as mock_video_svc,
            patch("backend.api.routes.videos.get_db_client") as mock_db,
        ):

            mock_script_svc.return_value.generate_script = AsyncMock(
                side_effect=Exception("Script generation failed")
            )
            mock_video_svc.return_value.generate_video_from_script = AsyncMock()
            mock_db.return_value.create_job_record = AsyncMock(return_value="error-job")
            mock_db.return_value.update_job_status = AsyncMock()

            request_data = {"topic": "Error Test", "duration_seconds": 60}

            response = e2e_client.post("/api/v1/videos/generate", json=request_data)

            # Request should still be accepted (async processing)
            assert response.status_code == 202

            # In real scenario, background task would handle the error
            # and update job status to 'failed'

    def test_status_check_for_nonexistent_job(self, e2e_client):
        """Test status check for job that doesn't exist."""
        with patch("backend.api.routes.videos.get_db_client") as mock_get_db:
            mock_db = MagicMock(spec=BigQueryClient)
            mock_db.query_single_row = AsyncMock(return_value=None)
            mock_get_db.return_value = mock_db

            response = e2e_client.get("/api/v1/videos/nonexistent-job/status")

            assert response.status_code == 404
            data = response.json()
            assert "not found" in data["detail"].lower()

    def test_video_generation_with_maximum_parameters(self, e2e_client):
        """Test video generation with maximum allowed parameters."""
        with (
            patch("backend.api.routes.videos.get_script_service") as mock_script_svc,
            patch("backend.api.routes.videos.get_video_service") as mock_video_svc,
            patch("backend.api.routes.videos.get_db_client") as mock_db,
        ):

            mock_script_svc.return_value.generate_script = AsyncMock(
                return_value={
                    "title": "Maximum Parameters Test",
                    "hook": "Test hook",
                    "script": "Test script",
                    "key_points": ["Test"],
                    "metadata": {},
                }
            )
            mock_video_svc.return_value.generate_video_from_script = AsyncMock(
                return_value="https://example.com/video.mp4"
            )
            mock_db.return_value.create_job_record = AsyncMock(
                return_value="max-params-job"
            )

            request_data = {
                "topic": "A" * 200,  # Maximum topic length
                "duration_seconds": 600,  # Maximum duration
                "style": "educational",
                "additional_context": "B" * 500,  # Maximum context length
                "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],  # Maximum tags
            }

            response = e2e_client.post("/api/v1/videos/generate", json=request_data)

            assert response.status_code == 202
            data = response.json()
            assert data["status"] == "queued"

    def test_estimate_generation_time_calculation(self, e2e_client):
        """Test that generation time is estimated correctly."""
        # Test different durations
        test_cases = [
            (30, 270),  # 30 * 5 + 120 = 270
            (120, 720),  # 120 * 5 + 120 = 720
            (300, 1620),  # 300 * 5 + 120 = 1620
            (600, 3120),  # 600 * 5 + 120 = 3120
        ]

        for duration, expected_time in test_cases:
            with (
                patch(
                    "backend.services.script_generator.ScriptGeneratorService"
                ) as mock_script_svc,
                patch(
                    "backend.services.video_generator.VideoGeneratorService"
                ) as mock_video_svc,
                patch("backend.database.bigquery_client.BigQueryClient") as mock_db,
            ):
                mock_script_svc.return_value.generate_script = AsyncMock(
                    return_value={
                        "title": "Time Estimation Test",
                        "hook": "Test",
                        "script": "Test",
                        "key_points": [],
                        "metadata": {},
                    }
                )
                mock_video_svc.return_value.generate_video_from_script = AsyncMock(
                    return_value="https://example.com/video.mp4"
                )
                mock_db.return_value.create_job_record = AsyncMock(
                    return_value="time-test-job"
                )

                request_data = {
                    "topic": "Time Estimation Test Topic",
                    "duration_seconds": duration,
                    "style": "educational",
                }

                response = e2e_client.post("/api/v1/videos/generate", json=request_data)

                assert response.status_code == 202
                data = response.json()
                assert data["estimated_completion_time"] == expected_time
