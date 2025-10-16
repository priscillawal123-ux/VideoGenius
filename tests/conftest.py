"""
Pytest fixtures and configuration.
"""

import os
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Set test environment variables before importing app
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("GOOGLE_PROJECT_ID", "test-project")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("CLOUD_STORAGE_BUCKET", "test-bucket")
os.environ.setdefault("VERTEX_AI_LOCATION", "us-central1")
os.environ.setdefault("BIGQUERY_DATASET", "test-dataset")

from backend.api.main import app


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def setup_test_environment() -> None:
    """Setup test environment variables."""
    # Additional test setup if needed
    pass


# GCP Service Mocks
@pytest.fixture
def mock_vertex_ai() -> Generator[MagicMock, None, None]:
    """Mock Vertex AI TextGenerationModel."""
    with patch("backend.services.script_generator.aiplatform") as mock_aiplatform:
        with patch(
            "backend.services.script_generator.TextGenerationModel"
        ) as mock_model:
            mock_instance = MagicMock()
            mock_instance.predict.return_value = MagicMock()
            mock_instance.predict.return_value.text = "Generated script content"
            mock_model.from_pretrained.return_value = mock_instance
            yield mock_instance


@pytest.fixture
def mock_bigquery() -> Generator[MagicMock, None, None]:
    """Mock BigQuery client."""
    with patch("backend.database.bigquery_client.bigquery.Client") as mock_client:
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = [
            MagicMock(
                items=lambda: [
                    ("job_id", "test-job"),
                    ("status", "completed"),
                ].__iter__()
            )
        ]
        mock_client.return_value.query.return_value = mock_query_job
        mock_client.return_value.insert_rows_json.return_value = []
        yield mock_client.return_value


@pytest.fixture
def mock_cloud_storage() -> Generator[MagicMock, None, None]:
    """Mock Google Cloud Storage."""
    with patch("backend.storage.cloud_storage.storage.Client") as mock_client:
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.public_url = (
            "https://storage.googleapis.com/test-bucket/test-file.mp4"
        )
        mock_bucket.blob.return_value = mock_blob
        mock_client.return_value.bucket.return_value = mock_bucket
        yield mock_client.return_value


@pytest.fixture
def mock_gtts() -> Generator[MagicMock, None, None]:
    """Mock gTTS for text-to-speech."""
    with patch("backend.services.video_generator.gTTS") as mock_gtts:
        mock_instance = MagicMock()
        mock_gtts.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_moviepy() -> Generator[dict, None, None]:
    """Mock MoviePy components."""
    with (
        patch("backend.services.video_generator.ImageClip") as mock_image_clip,
        patch("backend.services.video_generator.concatenate_videoclips") as mock_concat,
        patch("backend.services.video_generator.AudioFileClip") as mock_audio_clip,
    ):

        mock_clip = MagicMock()
        mock_image_clip.return_value = mock_clip
        mock_concat.return_value = mock_clip
        mock_audio_clip.return_value = mock_clip

        yield {
            "image_clip": mock_image_clip,
            "concat": mock_concat,
            "audio_clip": mock_audio_clip,
            "clip": mock_clip,
        }


# Service Fixtures
@pytest.fixture
def mock_script_service(mock_vertex_ai) -> Any:
    """Mock ScriptGeneratorService."""
    from backend.services.script_generator import ScriptGeneratorService

    service = ScriptGeneratorService(
        project_id="test-project", location="us-central1", model_name="text-bison"
    )
    return service


@pytest.fixture
def mock_video_service(mock_cloud_storage, mock_gtts, mock_moviepy) -> Any:
    """Mock VideoGeneratorService."""
    from backend.services.video_generator import VideoGeneratorService
    from backend.storage.cloud_storage import CloudStorageService

    storage_service = CloudStorageService("test-bucket")
    service = VideoGeneratorService(storage_service)
    return service


@pytest.fixture
def mock_db_service(mock_bigquery) -> Any:
    """Mock BigQueryClient."""
    from backend.database.bigquery_client import BigQueryClient

    client = BigQueryClient(project_id="test-project", dataset_id="test-dataset")
    return client


@pytest.fixture
def mock_storage_service(mock_cloud_storage) -> Any:
    """Mock CloudStorageService."""
    from backend.storage.cloud_storage import CloudStorageService

    service = CloudStorageService("test-bucket")
    return service


# Test Data Fixtures
@pytest.fixture
def sample_video_request() -> dict:
    """Sample video generation request data."""
    return {
        "topic": "Machine Learning Basics",
        "duration_seconds": 120,
        "style": "educational",
        "additional_context": "Focus on beginners",
        "tags": ["AI", "ML", "tutorial"],
    }


@pytest.fixture
def sample_script_data() -> dict:
    """Sample script generation response."""
    return {
        "title": "Understanding Machine Learning",
        "hook": "Did you know ML is everywhere?",
        "script": "Machine learning is a subset of AI...",
        "key_points": ["What is ML", "Types of ML", "Real-world applications"],
        "metadata": {
            "topic": "Machine Learning Basics",
            "duration": 120,
            "style": "educational",
            "model": "test-model",
        },
    }


@pytest.fixture
def sample_job_record() -> dict:
    """Sample job record from BigQuery."""
    return {
        "job_id": "test-job-123",
        "user_id": "user123",
        "status": "completed",
        "topic": "Machine Learning Basics",
        "duration_seconds": 120,
        "style": "educational",
        "video_url": "https://storage.googleapis.com/test-bucket/video_test-job-123.mp4",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:05:00Z",
    }
