"""End-to-end integration tests for video generation pipeline."""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from backend.api.main import app
from backend.worker.main import app as worker_app


@pytest.fixture
def api_client():
    """FastAPI test client for API."""
    return TestClient(app)


@pytest.fixture
def worker_client():
    """FastAPI test client for worker."""
    return TestClient(worker_app)


@pytest.fixture
async def async_api_client():
    """Async HTTP client for API."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_full_video_generation_pipeline(api_client, async_api_client):
    """Test complete video generation pipeline from API to worker.

    This test mocks external services but verifies the full flow:
    1. API receives request
    2. Creates job in BigQuery
    3. Queues task in Cloud Tasks
    4. Worker processes task
    5. Updates job status
    """
    # Mock all external dependencies
    with (
        patch("backend.database.bigquery_client.BigQueryClient") as mock_bq,
        patch("backend.services.cloud_tasks_client.CloudTasksClient") as mock_tasks,
        patch(
            "backend.services.script_generator.ScriptGeneratorService"
        ) as mock_script,
        patch("backend.services.video_generator.VideoGeneratorService") as mock_video,
    ):

        # Setup mocks
        mock_bq_instance = MagicMock()
        mock_bq_instance.create_job_record = AsyncMock(return_value="test-job-123")
        mock_bq_instance.update_job_status = AsyncMock()
        mock_bq_instance.update_job_data = AsyncMock()
        mock_bq.return_value = mock_bq_instance

        mock_tasks_instance = MagicMock()
        mock_tasks_instance.create_task = AsyncMock(return_value="task-123")
        mock_tasks.return_value = mock_tasks_instance

        mock_script_instance = MagicMock()
        mock_script_instance.generate_script = AsyncMock(
            return_value={
                "title": "Test Video",
                "script": "This is a test script.",
                "duration": 60,
            }
        )
        mock_script.return_value = mock_script_instance

        mock_video_instance = MagicMock()
        mock_video_instance.generate_video_from_script = AsyncMock(
            return_value="https://storage.googleapis.com/test/video.mp4"
        )
        mock_video.return_value = mock_video_instance

        # Test API endpoint
        payload = {
            "topic": "Test video generation",
            "duration_seconds": 60,
            "style": "educational",
            "additional_context": "Test context",
        }

        response = api_client.post("/api/v1/videos/generate", json=payload)

        # Verify API response
        assert response.status_code == 202
        data = response.json()
        assert data["job_id"] == "test-job-123"
        assert data["status"] == "queued"
        assert "estimated_completion_time" in data

        # Verify BigQuery was called to create job
        mock_bq_instance.create_job_record.assert_called_once()
        call_args = mock_bq_instance.create_job_record.call_args
        assert call_args[1]["job_type"] == "video_generation"
        assert call_args[1]["parameters"] == payload

        # Verify Cloud Tasks was called to queue task
        mock_tasks_instance.create_task.assert_called_once()
        task_payload = mock_tasks_instance.create_task.call_args[1]["payload"]
        assert task_payload["job_id"] == "test-job-123"
        assert task_payload["request"] == payload

        # Simulate worker processing the task
        worker_payload = {"job_id": "test-job-123", "request": payload}

        worker_response = api_client.post(
            "/process-video-generation", json=worker_payload
        )

        # Verify worker response
        assert worker_response.status_code == 200
        worker_data = worker_response.json()
        assert worker_data["status"] == "success"

        # Verify job status updates
        assert (
            mock_bq_instance.update_job_status.call_count >= 2
        )  # generating_script + completed
        mock_bq_instance.update_job_data.assert_called()


@pytest.mark.asyncio
async def test_video_generation_failure_handling(api_client):
    """Test failure handling in video generation pipeline."""
    with (
        patch("backend.database.bigquery_client.BigQueryClient") as mock_bq,
        patch("backend.services.cloud_tasks_client.CloudTasksClient") as mock_tasks,
    ):

        mock_bq_instance = MagicMock()
        mock_bq_instance.create_job_record = AsyncMock(
            side_effect=Exception("BigQuery error")
        )
        mock_bq.return_value = mock_bq_instance

        mock_tasks_instance = MagicMock()
        mock_tasks.return_value = mock_tasks_instance

        payload = {
            "topic": "Test video",
            "duration_seconds": 60,
            "style": "educational",
        }

        response = api_client.post("/api/v1/videos/generate", json=payload)

        # Should return 500 on failure
        assert response.status_code == 500
        assert "Failed to initiate video generation" in response.json()["detail"]


@pytest.mark.asyncio
async def test_worker_health_check(worker_client):
    """Test worker health check endpoint."""
    response = worker_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_invalid_worker_payload(worker_client):
    """Test worker with invalid payload."""
    invalid_payload = {"invalid": "data"}

    response = worker_client.post("/process-video-generation", json=invalid_payload)

    # Should return 422 for validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_video_status_endpoint(api_client):
    """Test video status checking endpoint."""
    with patch("backend.database.bigquery_client.BigQueryClient") as mock_bq:
        mock_bq_instance = MagicMock()
        mock_bq_instance.query_single_row = AsyncMock(
            return_value={
                "job_id": "test-job-123",
                "status": "completed",
                "video_url": "https://storage.googleapis.com/test/video.mp4",
                "created_at": "2024-01-01T00:00:00Z",
            }
        )
        mock_bq.return_value = mock_bq_instance

        response = api_client.get("/api/v1/videos/test-job-123/status")

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "test-job-123"
        assert data["status"] == "completed"
        assert "video_url" in data


@pytest.mark.asyncio
async def test_video_status_not_found(api_client):
    """Test video status for non-existent job."""
    with patch("backend.database.bigquery_client.BigQueryClient") as mock_bq:
        mock_bq_instance = MagicMock()
        mock_bq_instance.query_single_row = AsyncMock(return_value=None)
        mock_bq.return_value = mock_bq_instance

        response = api_client.get("/api/v1/videos/non-existent/status")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
