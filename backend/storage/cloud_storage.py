"""
Cloud Storage operations service.
"""

import logging
import uuid
from typing import BinaryIO, Dict, Optional

from google.api_core import exceptions
from google.cloud import storage

logger = logging.getLogger(__name__)


class CloudStorageService:
    """Service for Cloud Storage operations."""

    def __init__(self, bucket_name: str):
        """Initialize Cloud Storage service.

        Args:
            bucket_name: GCS bucket name
        """
        self.client = storage.Client()
        self.bucket_name = bucket_name
        self.bucket = self.client.bucket(bucket_name)

    async def upload_file(
        self,
        file_obj: BinaryIO,
        filename: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """Upload a file to Cloud Storage.

        Args:
            file_obj: File-like object to upload
            filename: Destination filename
            content_type: MIME type of the file
            metadata: Additional metadata

        Returns:
            Public URL of the uploaded file

        Raises:
            ValueError: If upload fails
        """
        try:
            blob = self.bucket.blob(filename)

            # Set content type if provided
            if content_type:
                blob.content_type = content_type

            # Set metadata if provided
            if metadata:
                blob.metadata = metadata

            # Upload the file
            blob.upload_from_file(file_obj)

            logger.info(f"File uploaded: {filename}")
            return blob.public_url

        except exceptions.GoogleAPIError as e:
            logger.error(f"Upload error: {e}")
            raise ValueError(f"Failed to upload file: {e}") from e

    async def download_file(self, filename: str, destination: BinaryIO) -> None:
        """Download a file from Cloud Storage.

        Args:
            filename: Source filename in bucket
            destination: File-like object to write to

        Raises:
            ValueError: If download fails
        """
        try:
            blob = self.bucket.blob(filename)
            blob.download_to_file(destination)

            logger.info(f"File downloaded: {filename}")

        except exceptions.GoogleAPIError as e:
            logger.error(f"Download error: {e}")
            raise ValueError(f"Failed to download file: {e}") from e

    async def delete_file(self, filename: str) -> None:
        """Delete a file from Cloud Storage.

        Args:
            filename: Filename to delete

        Raises:
            ValueError: If deletion fails
        """
        try:
            blob = self.bucket.blob(filename)
            blob.delete()

            logger.info(f"File deleted: {filename}")

        except exceptions.GoogleAPIError as e:
            logger.error(f"Delete error: {e}")
            raise ValueError(f"Failed to delete file: {e}") from e

    async def file_exists(self, filename: str) -> bool:
        """Check if a file exists in Cloud Storage.

        Args:
            filename: Filename to check

        Returns:
            True if file exists, False otherwise
        """
        try:
            blob = self.bucket.blob(filename)
            return blob.exists()

        except exceptions.GoogleAPIError:
            return False

    async def generate_signed_url(
        self, filename: str, expiration_minutes: int = 60
    ) -> str:
        """Generate a signed URL for temporary access.

        Args:
            filename: Filename to generate URL for
            expiration_minutes: URL expiration time in minutes

        Returns:
            Signed URL

        Raises:
            ValueError: If URL generation fails
        """
        try:
            blob = self.bucket.blob(filename)
            url = blob.generate_signed_url(
                expiration=expiration_minutes * 60  # Convert to seconds
            )

            logger.info(f"Signed URL generated for: {filename}")
            return url

        except exceptions.GoogleAPIError as e:
            logger.error(f"Signed URL error: {e}")
            raise ValueError(f"Failed to generate signed URL: {e}") from e

    async def list_files(
        self, prefix: Optional[str] = None, max_results: Optional[int] = None
    ) -> list[str]:
        """List files in the bucket.

        Args:
            prefix: File prefix to filter by
            max_results: Maximum number of results

        Returns:
            List of filenames

        Raises:
            ValueError: If listing fails
        """
        try:
            blobs = self.client.list_blobs(
                self.bucket_name, prefix=prefix, max_results=max_results
            )

            filenames = [blob.name for blob in blobs]
            logger.info(f"Listed {len(filenames)} files")
            return filenames

        except exceptions.GoogleAPIError as e:
            logger.error(f"List error: {e}")
            raise ValueError(f"Failed to list files: {e}") from e

    def generate_unique_filename(
        self, original_filename: str, prefix: Optional[str] = None
    ) -> str:
        """Generate a unique filename.

        Args:
            original_filename: Original filename
            prefix: Optional prefix for the filename

        Returns:
            Unique filename
        """
        unique_id = str(uuid.uuid4())
        name_parts = original_filename.rsplit(".", 1)

        if len(name_parts) == 2:
            base_name, extension = name_parts
            filename = f"{base_name}_{unique_id}.{extension}"
        else:
            filename = f"{original_filename}_{unique_id}"

        if prefix:
            filename = f"{prefix}/{filename}"

        return filename
