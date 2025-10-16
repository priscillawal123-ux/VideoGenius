"""
Unit tests for BigQueryClient video operations.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.api_core import exceptions

from backend.database.bigquery_client import BigQueryClient


class TestBigQueryClientVideoOperations:
    """Test cases for BigQueryClient video-related operations."""

    @pytest.fixture
    def client(self):
        """Create BigQueryClient instance with mocked dependencies."""
        with patch(
            "backend.database.bigquery_client.bigquery.Client"
        ) as mock_bq_client:
            client = BigQueryClient(
                project_id="test-project", dataset_id="test-dataset"
            )
            return client

    @pytest.mark.asyncio
    async def test_create_job_record_success(self, client):
        """Test successful job record creation."""
        job_type = "video_generation"
        parameters = {
            "topic": "Machine Learning",
            "duration_seconds": 120,
            "style": "educational",
        }
        user_id = "user123"

        # Mock insert_row
        with patch.object(client, "insert_row", new_callable=AsyncMock) as mock_insert:
            mock_insert.return_value = "job-123"

            # When
            job_id = await client.create_job_record(job_type, parameters, user_id)

            # Then
            assert isinstance(job_id, str)
            mock_insert.assert_called_once_with(
                "video_jobs",
                {
                    "job_id": job_id,
                    "user_id": user_id,
                    "status": "queued",
                    "topic": "Machine Learning",
                    "duration_seconds": 120,
                    "style": "educational",
                    "created_at": "AUTO",
                    "updated_at": "AUTO",
                },
            )

    @pytest.mark.asyncio
    async def test_create_job_record_anonymous_user(self, client):
        """Test job record creation with anonymous user."""
        parameters = {"topic": "Test Topic", "duration_seconds": 60}

        with patch.object(client, "insert_row", new_callable=AsyncMock) as mock_insert:
            # When
            job_id = await client.create_job_record("video_generation", parameters)

            # Then
            call_args = mock_insert.call_args[0]
            assert call_args[0] == "video_jobs"
            job_record = call_args[1]
            assert job_record["user_id"] == "anonymous"

    @pytest.mark.asyncio
    async def test_create_job_record_minimal_parameters(self, client):
        """Test job record creation with minimal parameters."""
        parameters = {"topic": "Test"}

        with patch.object(client, "insert_row", new_callable=AsyncMock) as mock_insert:
            # When
            job_id = await client.create_job_record("video_generation", parameters)

            # Then
            call_args = mock_insert.call_args[0]
            job_record = call_args[1]
            assert job_record["topic"] == "Test"
            assert job_record["duration_seconds"] is None
            assert job_record["style"] is None

    @pytest.mark.asyncio
    async def test_create_job_record_insert_failure(self, client):
        """Test job record creation failure."""
        parameters = {"topic": "Test"}

        with patch.object(client, "insert_row", new_callable=AsyncMock) as mock_insert:
            mock_insert.side_effect = ValueError("Insert failed")

            # When/Then
            with pytest.raises(ValueError, match="Insert failed"):
                await client.create_job_record("video_generation", parameters)

    def test_update_job_status_success(self, client):
        """Test successful job status update."""
        job_id = "job-123"
        status = "completed"

        # When
        client.update_job_status(job_id, status)

        # Then - This is a no-op in current implementation, just logs

    def test_update_job_status_with_error(self, client):
        """Test job status update with error."""
        job_id = "job-123"
        status = "failed"
        error = "Processing failed"

        # When
        client.update_job_status(job_id, status, error)

        # Then - This is a no-op in current implementation, just logs

    def test_update_job_data_success(self, client):
        """Test successful job data update."""
        job_id = "job-123"
        data = {"video_url": "https://example.com/video.mp4", "script": "test script"}

        # When
        client.update_job_data(job_id, data)

        # Then - This is a no-op in current implementation, just logs

    @pytest.mark.asyncio
    async def test_query_single_row_success(self, client):
        """Test successful single row query."""
        query = "SELECT * FROM test_table WHERE id = @id"
        parameters = {"id": "123"}

        expected_row = {"id": "123", "name": "test"}

        with patch.object(client, "query_data", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = [expected_row]

            # When
            result = await client.query_single_row(query, parameters)

            # Then
            assert result == expected_row
            mock_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_single_row_no_results(self, client):
        """Test single row query with no results."""
        query = "SELECT * FROM test_table WHERE id = @id"
        parameters = {"id": "nonexistent"}

        with patch.object(client, "query_data", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = []

            # When
            result = await client.query_single_row(query, parameters)

            # Then
            assert result is None

    @pytest.mark.asyncio
    async def test_query_single_row_no_parameters(self, client):
        """Test single row query without parameters."""
        query = "SELECT * FROM test_table LIMIT 1"

        expected_row = {"id": "1", "name": "test"}

        with patch.object(client, "query_data", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = [expected_row]

            # When
            result = await client.query_single_row(query)

            # Then
            assert result == expected_row
            # Should be called with None parameters
            call_args = mock_query.call_args
            assert call_args[0][1] is None

    @pytest.mark.asyncio
    async def test_query_single_row_query_failure(self, client):
        """Test single row query failure."""
        query = "SELECT * FROM invalid_table"

        with patch.object(client, "query_data", new_callable=AsyncMock) as mock_query:
            mock_query.side_effect = Exception("Query failed")

            # When
            result = await client.query_single_row(query)

            # Then
            assert result is None

    @pytest.mark.asyncio
    async def test_get_job_success(self, client):
        """Test successful job retrieval."""
        job_id = "job-123"
        expected_job = {"job_id": job_id, "status": "completed", "topic": "Test Topic"}

        with patch.object(client, "query_data", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = [expected_job]

            # When
            result = await client.get_job(job_id)

            # Then
            assert result == expected_job
            mock_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_job_not_found(self, client):
        """Test job retrieval when job doesn't exist."""
        job_id = "nonexistent-job"

        with patch.object(client, "query_data", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = []

            # When
            result = await client.get_job(job_id)

            # Then
            assert result is None

    @pytest.mark.asyncio
    async def test_get_job_query_failure(self, client):
        """Test job retrieval failure."""
        job_id = "job-123"

        # Mock the query_data method to raise exception
        with patch.object(client, "query_data", new_callable=AsyncMock) as mock_query:
            mock_query.side_effect = Exception("Query failed")

            # When
            result = await client.get_job(job_id)

            # Then - should return None on query failure
            assert result is None
            mock_query.assert_called_once()

    def test_initialization(self):
        """Test BigQueryClient initialization."""
        with patch(
            "backend.database.bigquery_client.bigquery.Client"
        ) as mock_bq_client:
            client = BigQueryClient(
                project_id="test-project", dataset_id="test-dataset"
            )

            mock_bq_client.assert_called_once_with(project="test-project")
            assert client.project_id == "test-project"
            assert client.dataset_id == "test-dataset"
