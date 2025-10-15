"""
Cloud Storage client with Google Cloud best practices and optimizations.
"""

import asyncio
import logging
from typing import Any, Dict, Optional, BinaryIO, Callable, cast

from cachetools import TTLCache
from google.api_core import exceptions, retry
from google.cloud import storage
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker pattern for external service calls."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return True
        return (
            asyncio.get_event_loop().time() - self.last_failure_time
        ) > self.recovery_timeout

    def _on_success(self) -> None:
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class CloudStorageClient:
    """Optimized Cloud Storage client with caching and circuit breaker."""

    def __init__(
        self, project_id: str, bucket_name: str, credentials_path: Optional[str] = None
    ):
        """Initialize Cloud Storage client with optimizations.

        Args:
            project_id: GCP project ID
            bucket_name: GCS bucket name
            credentials_path: Path to service account key (optional)
        """
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.credentials_path = credentials_path
        self._client: Optional[storage.Client] = None
        self._bucket: Optional[storage.Bucket] = None

        # Configure retry strategy
        self.retry_config = retry.Retry(
            initial=1.0,
            maximum=16.0,
            multiplier=2.0,
            deadline=60.0,
            predicate=retry.if_exception_type(
                exceptions.ServiceUnavailable,
                exceptions.TooManyRequests,
                exceptions.InternalServerError,
                exceptions.ResourceExhausted,
            ),
        )

        # Cache for metadata (TTL: 5 minutes)
        self.metadata_cache = TTLCache(maxsize=500, ttl=300)

        # Circuit breaker for upload/download operations
        self._circuit_breaker: Optional[CircuitBreaker] = None

    @property
    def client(self) -> storage.Client:
        """Lazy initialize Cloud Storage client."""
        if self._client is None:
            if self.credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self._client = storage.Client(
                    project=self.project_id, credentials=credentials
                )
            else:
                self._client = storage.Client(project=self.project_id)
        return self._client

    @property
    def bucket(self) -> storage.Bucket:
        """Lazy initialize bucket."""
        if self._bucket is None:
            self._bucket = self.client.bucket(self.bucket_name)
        return self._bucket

    @property
    def circuit_breaker(self) -> CircuitBreaker:
        """Lazy initialize circuit breaker."""
        if self._circuit_breaker is None:
            self._circuit_breaker = CircuitBreaker()
        return self._circuit_breaker

    async def upload_file(
        self,
        source_path: str,
        destination_blob_name: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """Upload file to Cloud Storage with optimizations.

        Args:
            source_path: Local file path
            destination_blob_name: GCS blob name
            content_type: MIME type
            metadata: Additional metadata

        Returns:
            Public URL of uploaded file

        Raises:
            ValueError: If upload fails
        """

        async def _upload():
            try:
                blob = self.bucket.blob(destination_blob_name)

                # Set content type if provided
                if content_type:
                    blob.content_type = content_type

                # Set metadata if provided
                if metadata:
                    blob.metadata = metadata

                # Upload with retry
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: blob.upload_from_filename(
                        source_path, retry=self.retry_config
                    ),
                )

                # Make public if it's a video or image
                if content_type and (
                    content_type.startswith("video/")
                    or content_type.startswith("image/")
                ):
                    blob.make_public()

                logger.info(f"File uploaded successfully: {destination_blob_name}")
                return blob.public_url

            except Exception as e:
                logger.error(f"Upload error: {e}")
                raise ValueError(f"Failed to upload file: {e}") from e

        return await self.circuit_breaker.call(_upload)

    async def download_file(self, blob_name: str, destination_path: str) -> None:
        """Download file from Cloud Storage with optimizations.

        Args:
            blob_name: GCS blob name
            destination_path: Local destination path

        Raises:
            ValueError: If download fails
        """

        async def _download():
            try:
                blob = self.bucket.blob(blob_name)

                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: blob.download_to_filename(
                        destination_path, retry=self.retry_config
                    ),
                )

                logger.info(f"File downloaded successfully: {blob_name}")

            except Exception as e:
                logger.error(f"Download error: {e}")
                raise ValueError(f"Failed to download file: {e}") from e

        await self.circuit_breaker.call(_download)

    async def get_file_metadata(
        self, blob_name: str, use_cache: bool = True
    ) -> Dict[str, Any]:
        """Get file metadata with caching.

        Args:
            blob_name: GCS blob name
            use_cache: Whether to use caching

        Returns:
            File metadata

        Raises:
            ValueError: If metadata retrieval fails
        """
        if use_cache and blob_name in self.metadata_cache:
            logger.info("Returning cached metadata")
            return self.metadata_cache[blob_name]

        async def _get_metadata():
            try:
                blob = self.bucket.blob(blob_name)
                await asyncio.get_event_loop().run_in_executor(
                    None, lambda: blob.reload(retry=self.retry_config)
                )

                metadata = {
                    "name": blob.name,
                    "size": blob.size,
                    "content_type": blob.content_type,
                    "created": blob.time_created,
                    "updated": blob.updated,
                    "public_url": blob.public_url if blob.public_url else None,
                    "metadata": blob.metadata or {},
                }

                logger.info(f"Metadata retrieved for: {blob_name}")
                return metadata

            except Exception as e:
                logger.error(f"Metadata retrieval error: {e}")
                raise ValueError(f"Failed to get metadata: {e}") from e

        metadata = await self.circuit_breaker.call(_get_metadata)

        if use_cache:
            self.metadata_cache[blob_name] = metadata

        return metadata

    async def delete_file(self, blob_name: str) -> None:
        """Delete file from Cloud Storage.

        Args:
            blob_name: GCS blob name

        Raises:
            ValueError: If deletion fails
        """

        async def _delete():
            try:
                blob = self.bucket.blob(blob_name)
                await asyncio.get_event_loop().run_in_executor(
                    None, lambda: blob.delete(retry=self.retry_config)
                )

                # Invalidate cache
                if blob_name in self.metadata_cache:
                    del self.metadata_cache[blob_name]

                logger.info(f"File deleted successfully: {blob_name}")

            except Exception as e:
                logger.error(f"Delete error: {e}")
                raise ValueError(f"Failed to delete file: {e}") from e

        await self.circuit_breaker.call(_delete)

    async def list_files(
        self, prefix: Optional[str] = None, max_results: int = 1000
    ) -> list:
        """List files in bucket with optional prefix.

        Args:
            prefix: File prefix filter
            max_results: Maximum number of results

        Returns:
            List of blob names

        Raises:
            ValueError: If listing fails
        """

        async def _list():
            try:
                blobs = self.client.list_blobs(
                    self.bucket, prefix=prefix, max_results=max_results
                )

                blob_names = [blob.name for blob in blobs]
                logger.info(f"Listed {len(blob_names)} files with prefix: {prefix}")
                return blob_names

            except Exception as e:
                logger.error(f"List error: {e}")
                raise ValueError(f"Failed to list files: {e}") from e

        return await self.circuit_breaker.call(_list)

    async def generate_signed_url(
        self, blob_name: str, expiration_minutes: int = 60
    ) -> str:
        """Generate signed URL for private file access.

        Args:
            blob_name: GCS blob name
            expiration_minutes: URL expiration time

        Returns:
            Signed URL

        Raises:
            ValueError: If URL generation fails
        """

        async def _generate_url():
            try:
                blob = self.bucket.blob(blob_name)

                url = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: blob.generate_signed_url(
                        expiration=expiration_minutes * 60, method="GET"
                    ),
                )

                logger.info(f"Signed URL generated for: {blob_name}")
                return url

            except Exception as e:
                logger.error(f"Signed URL generation error: {e}")
                raise ValueError(f"Failed to generate signed URL: {e}") from e

        return await self.circuit_breaker.call(_generate_url)
