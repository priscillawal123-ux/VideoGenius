"""
Unit tests for CloudStorageService.
"""

import io
from unittest.mock import MagicMock, patch

import pytest
from google.api_core import exceptions

from backend.storage.cloud_storage import CloudStorageService


class TestCloudStorageService:
    """Test cases for CloudStorageService."""

    @pytest.fixture
    def service(self):
        """Create service instance with mocked dependencies."""
        with patch("backend.storage.cloud_storage.storage.Client") as mock_client:
            mock_bucket = MagicMock()
            mock_client.return_value.bucket.return_value = mock_bucket

            service = CloudStorageService("test-bucket")
            return service

    @pytest.mark.asyncio
    async def test_upload_file_success(self, service):
        """Test successful file upload."""
        # Given
        file_obj = io.BytesIO(b"test content")
        filename = "test.mp4"
        content_type = "video/mp4"
        metadata = {"job_id": "123", "title": "Test Video"}

        mock_blob = MagicMock()
        mock_blob.public_url = "https://storage.googleapis.com/test-bucket/test.mp4"
        service.bucket.blob.return_value = mock_blob

        # When
        result = await service.upload_file(file_obj, filename, content_type, metadata)

        # Then
        assert result == "https://storage.googleapis.com/test-bucket/test.mp4"
        service.bucket.blob.assert_called_once_with(filename)
        mock_blob.upload_from_file.assert_called_once_with(file_obj)
        assert mock_blob.content_type == content_type
        assert mock_blob.metadata == metadata

    @pytest.mark.asyncio
    async def test_upload_file_no_content_type(self, service):
        """Test file upload without content type."""
        file_obj = io.BytesIO(b"test content")
        filename = "test.txt"

        mock_blob = MagicMock()
        mock_blob.public_url = "https://storage.googleapis.com/test-bucket/test.txt"
        service.bucket.blob.return_value = mock_blob

        # When
        result = await service.upload_file(file_obj, filename)

        # Then
        assert result == "https://storage.googleapis.com/test-bucket/test.txt"
        # Verify upload was called
        mock_blob.upload_from_file.assert_called_once_with(file_obj)

    @pytest.mark.asyncio
    async def test_upload_file_no_metadata(self, service):
        """Test file upload without metadata."""
        file_obj = io.BytesIO(b"test content")
        filename = "test.txt"

        mock_blob = MagicMock()
        mock_blob.public_url = "https://storage.googleapis.com/test-bucket/test.txt"
        service.bucket.blob.return_value = mock_blob

        # When
        result = await service.upload_file(file_obj, filename)

        # Then
        assert result == "https://storage.googleapis.com/test-bucket/test.txt"
        # Verify upload was called
        mock_blob.upload_from_file.assert_called_once_with(file_obj)

    @pytest.mark.asyncio
    async def test_upload_file_failure(self, service):
        """Test file upload failure."""
        file_obj = io.BytesIO(b"test content")
        filename = "test.mp4"

        mock_blob = MagicMock()
        mock_blob.upload_from_file.side_effect = exceptions.GoogleAPIError(
            "Upload failed"
        )
        service.bucket.blob.return_value = mock_blob

        # When/Then
        with pytest.raises(ValueError, match="Failed to upload file: Upload failed"):
            await service.upload_file(file_obj, filename)

    @pytest.mark.asyncio
    async def test_download_file_success(self, service):
        """Test successful file download."""
        filename = "test.mp4"
        destination = io.BytesIO()

        mock_blob = MagicMock()
        service.bucket.blob.return_value = mock_blob

        # When
        await service.download_file(filename, destination)

        # Then
        service.bucket.blob.assert_called_once_with(filename)
        mock_blob.download_to_file.assert_called_once_with(destination)

    @pytest.mark.asyncio
    async def test_download_file_failure(self, service):
        """Test file download failure."""
        filename = "test.mp4"
        destination = io.BytesIO()

        mock_blob = MagicMock()
        mock_blob.download_to_file.side_effect = exceptions.GoogleAPIError(
            "Download failed"
        )
        service.bucket.blob.return_value = mock_blob

        # When/Then
        with pytest.raises(
            ValueError, match="Failed to download file: Download failed"
        ):
            await service.download_file(filename, destination)

    @pytest.mark.asyncio
    async def test_delete_file_success(self, service):
        """Test successful file deletion."""
        filename = "test.mp4"

        mock_blob = MagicMock()
        service.bucket.blob.return_value = mock_blob

        # When
        await service.delete_file(filename)

        # Then
        service.bucket.blob.assert_called_once_with(filename)
        mock_blob.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_file_failure(self, service):
        """Test file deletion failure."""
        filename = "test.mp4"

        mock_blob = MagicMock()
        mock_blob.delete.side_effect = exceptions.GoogleAPIError("Delete failed")
        service.bucket.blob.return_value = mock_blob

        # When/Then
        with pytest.raises(ValueError, match="Failed to delete file: Delete failed"):
            await service.delete_file(filename)

    @pytest.mark.asyncio
    async def test_file_exists_true(self, service):
        """Test file exists check - file exists."""
        filename = "test.mp4"

        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        service.bucket.blob.return_value = mock_blob

        # When
        result = await service.file_exists(filename)

        # Then
        assert result is True
        service.bucket.blob.assert_called_once_with(filename)
        mock_blob.exists.assert_called_once()

    @pytest.mark.asyncio
    async def test_file_exists_false(self, service):
        """Test file exists check - file doesn't exist."""
        filename = "test.mp4"

        mock_blob = MagicMock()
        mock_blob.exists.return_value = False
        service.bucket.blob.return_value = mock_blob

        # When
        result = await service.file_exists(filename)

        # Then
        assert result is False

    @pytest.mark.asyncio
    async def test_file_exists_error(self, service):
        """Test file exists check - API error."""
        filename = "test.mp4"

        mock_blob = MagicMock()
        mock_blob.exists.side_effect = exceptions.GoogleAPIError("Check failed")
        service.bucket.blob.return_value = mock_blob

        # When
        result = await service.file_exists(filename)

        # Then
        assert result is False

    @pytest.mark.asyncio
    async def test_generate_signed_url_success(self, service):
        """Test successful signed URL generation."""
        filename = "test.mp4"
        expiration_minutes = 30
        expected_url = "https://storage.googleapis.com/test-bucket/test.mp4?signed=..."

        mock_blob = MagicMock()
        mock_blob.generate_signed_url.return_value = expected_url
        service.bucket.blob.return_value = mock_blob

        # When
        result = await service.generate_signed_url(filename, expiration_minutes)

        # Then
        assert result == expected_url
        service.bucket.blob.assert_called_once_with(filename)
        mock_blob.generate_signed_url.assert_called_once_with(
            expiration=1800
        )  # 30 * 60

    @pytest.mark.asyncio
    async def test_generate_signed_url_default_expiration(self, service):
        """Test signed URL generation with default expiration."""
        filename = "test.mp4"
        expected_url = "https://storage.googleapis.com/test-bucket/test.mp4?signed=..."

        mock_blob = MagicMock()
        mock_blob.generate_signed_url.return_value = expected_url
        service.bucket.blob.return_value = mock_blob

        # When
        result = await service.generate_signed_url(filename)

        # Then
        mock_blob.generate_signed_url.assert_called_once_with(
            expiration=3600
        )  # 60 * 60

    @pytest.mark.asyncio
    async def test_generate_signed_url_failure(self, service):
        """Test signed URL generation failure."""
        filename = "test.mp4"

        mock_blob = MagicMock()
        mock_blob.generate_signed_url.side_effect = exceptions.GoogleAPIError(
            "URL generation failed"
        )
        service.bucket.blob.return_value = mock_blob

        # When/Then
        with pytest.raises(
            ValueError, match="Failed to generate signed URL: URL generation failed"
        ):
            await service.generate_signed_url(filename)

    @pytest.mark.asyncio
    async def test_list_files_success(self, service):
        """Test successful file listing."""
        prefix = "videos/"
        max_results = 10

        mock_blob1 = MagicMock()
        mock_blob1.name = "videos/video1.mp4"
        mock_blob2 = MagicMock()
        mock_blob2.name = "videos/video2.mp4"

        mock_client = service.client
        mock_client.list_blobs.return_value = [mock_blob1, mock_blob2]

        # When
        result = await service.list_files(prefix, max_results)

        # Then
        assert result == ["videos/video1.mp4", "videos/video2.mp4"]
        mock_client.list_blobs.assert_called_once_with(
            "test-bucket", prefix=prefix, max_results=max_results
        )

    @pytest.mark.asyncio
    async def test_list_files_no_filters(self, service):
        """Test file listing without filters."""
        mock_blob = MagicMock()
        mock_blob.name = "file.txt"

        mock_client = service.client
        mock_client.list_blobs.return_value = [mock_blob]

        # When
        result = await service.list_files()

        # Then
        assert result == ["file.txt"]
        mock_client.list_blobs.assert_called_once_with(
            "test-bucket", prefix=None, max_results=None
        )

    @pytest.mark.asyncio
    async def test_list_files_failure(self, service):
        """Test file listing failure."""
        mock_client = service.client
        mock_client.list_blobs.side_effect = exceptions.GoogleAPIError("List failed")

        # When/Then
        with pytest.raises(ValueError, match="Failed to list files: List failed"):
            await service.list_files()

    def test_generate_unique_filename_with_extension(self, service):
        """Test unique filename generation with file extension."""
        original = "video.mp4"
        result = service.generate_unique_filename(original)

        assert result.endswith(".mp4")
        assert "video_" in result
        assert result != original
        assert len(result) > len(original)

    def test_generate_unique_filename_no_extension(self, service):
        """Test unique filename generation without file extension."""
        original = "video"
        result = service.generate_unique_filename(original)

        assert "video_" in result
        assert result != original

    def test_generate_unique_filename_with_prefix(self, service):
        """Test unique filename generation with prefix."""
        original = "video.mp4"
        prefix = "uploads"
        result = service.generate_unique_filename(original, prefix)

        assert result.startswith("uploads/")
        assert "video_" in result
        assert result.endswith(".mp4")

    def test_initialization(self):
        """Test service initialization."""
        with patch("backend.storage.cloud_storage.storage.Client") as mock_client:
            mock_bucket = MagicMock()
            mock_client.return_value.bucket.return_value = mock_bucket

            service = CloudStorageService("test-bucket")

            mock_client.assert_called_once()
            mock_client.return_value.bucket.assert_called_once_with("test-bucket")
            assert service.bucket_name == "test-bucket"
            assert service.bucket == mock_bucket
