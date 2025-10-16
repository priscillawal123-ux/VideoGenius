"""
Secret Manager client with Google Cloud best practices and optimizations.
"""

import asyncio
import logging
from typing import Optional

from cachetools import TTLCache
from google.api_core import exceptions, retry
from google.cloud import secretmanager

logger = logging.getLogger(__name__)


class SecretManagerClient:
    """Optimized Secret Manager client with caching and circuit breaker."""

    def __init__(self, project_id: str):
        """Initialize Secret Manager client with optimizations.

        Args:
            project_id: GCP project ID
        """
        self.client = secretmanager.SecretManagerServiceClient()
        self.project_id = project_id

        # Configure retry strategy
        self.retry_config = retry.Retry(
            initial=1.0,
            maximum=8.0,
            multiplier=2.0,
            deadline=30.0,
            predicate=retry.if_exception_type(
                exceptions.ServiceUnavailable,
                exceptions.TooManyRequests,
                exceptions.InternalServerError,
                exceptions.ResourceExhausted,
            ),
        )

        # Cache for secrets (TTL: 10 minutes for sensitive data)
        self.secret_cache = TTLCache(maxsize=50, ttl=600)

        # Circuit breaker for secret operations
        self.circuit_breaker = CircuitBreaker()

    def _get_secret_name(self, secret_id: str, version: str = "latest") -> str:
        """Build the full secret name.

        Args:
            secret_id: Secret identifier
            version: Secret version

        Returns:
            Full secret name
        """
        return f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"

    async def get_secret(
        self, secret_id: str, version: str = "latest", use_cache: bool = True
    ) -> str:
        """Retrieve secret value with caching and circuit breaker.

        Args:
            secret_id: Secret identifier
            version: Secret version
            use_cache: Whether to use caching

        Returns:
            Secret value as string

        Raises:
            ValueError: If secret retrieval fails
        """
        cache_key = f"{secret_id}:{version}"

        if use_cache and cache_key in self.secret_cache:
            logger.info(f"Returning cached secret: {secret_id}")
            return self.secret_cache[cache_key]

        async def _get_secret():
            try:
                secret_name = self._get_secret_name(secret_id, version)

                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.access_secret_version(
                        request={"name": secret_name}, retry=self.retry_config
                    ),
                )

                secret_value = response.payload.data.decode("UTF-8")
                logger.info(f"Secret retrieved successfully: {secret_id}")
                return secret_value

            except Exception as e:
                logger.error(f"Secret retrieval error: {e}")
                raise ValueError(f"Failed to retrieve secret {secret_id}: {e}") from e

        secret_value = await self.circuit_breaker.call(_get_secret)

        if use_cache:
            self.secret_cache[cache_key] = secret_value

        return secret_value

    async def get_secret_json(
        self, secret_id: str, version: str = "latest", use_cache: bool = True
    ) -> dict:
        """Retrieve secret value as JSON with caching.

        Args:
            secret_id: Secret identifier
            version: Secret version
            use_cache: Whether to use caching

        Returns:
            Secret value as dictionary

        Raises:
            ValueError: If secret retrieval or JSON parsing fails
        """
        import json

        secret_value = await self.get_secret(secret_id, version, use_cache)

        try:
            return json.loads(secret_value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse secret {secret_id} as JSON: {e}") from e

    async def create_secret(
        self, secret_id: str, secret_value: str, labels: Optional[dict] = None
    ) -> None:
        """Create a new secret.

        Args:
            secret_id: Secret identifier
            secret_value: Secret value
            labels: Optional labels

        Raises:
            ValueError: If secret creation fails
        """

        async def _create_secret():
            try:
                parent = f"projects/{self.project_id}"

                # Create the secret
                secret = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.create_secret(
                        request={
                            "parent": parent,
                            "secret_id": secret_id,
                            "secret": {"labels": labels or {}},
                        },
                        retry=self.retry_config,
                    ),
                )

                # Add the secret version
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.add_secret_version(
                        request={
                            "parent": secret.name,
                            "payload": {"data": secret_value.encode("UTF-8")},
                        },
                        retry=self.retry_config,
                    ),
                )

                logger.info(f"Secret created successfully: {secret_id}")

            except Exception as e:
                logger.error(f"Secret creation error: {e}")
                raise ValueError(f"Failed to create secret {secret_id}: {e}") from e

        await self.circuit_breaker.call(_create_secret)

    async def update_secret(self, secret_id: str, secret_value: str) -> None:
        """Update an existing secret with new value.

        Args:
            secret_id: Secret identifier
            secret_value: Secret value

        Raises:
            ValueError: If secret update fails
        """

        async def _update_secret():
            try:
                secret_name = f"projects/{self.project_id}/secrets/{secret_id}"

                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.add_secret_version(
                        request={
                            "parent": secret_name,
                            "payload": {"data": secret_value.encode("UTF-8")},
                        },
                        retry=self.retry_config,
                    ),
                )

                # Invalidate cache
                cache_key = f"{secret_id}:latest"
                if cache_key in self.secret_cache:
                    del self.secret_cache[cache_key]

                logger.info(f"Secret updated successfully: {secret_id}")

            except Exception as e:
                logger.error(f"Secret update error: {e}")
                raise ValueError(f"Failed to update secret {secret_id}: {e}") from e

        await self.circuit_breaker.call(_update_secret)

    async def delete_secret(self, secret_id: str) -> None:
        """Delete a secret and all its versions.

        Args:
            secret_id: Secret identifier

        Raises:
            ValueError: If secret deletion fails
        """

        async def _delete_secret():
            try:
                secret_name = f"projects/{self.project_id}/secrets/{secret_id}"

                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.delete_secret(
                        request={"name": secret_name}, retry=self.retry_config
                    ),
                )

                # Clear all cache entries for this secret
                keys_to_delete = [
                    k for k in self.secret_cache.keys() if k.startswith(f"{secret_id}:")
                ]
                for key in keys_to_delete:
                    del self.secret_cache[key]

                logger.info(f"Secret deleted successfully: {secret_id}")

            except Exception as e:
                logger.error(f"Secret deletion error: {e}")
                raise ValueError(f"Failed to delete secret {secret_id}: {e}") from e

    async def list_secrets(self, filter_str: Optional[str] = None) -> list:
        """List secrets in the project.

        Args:
            filter_str: Optional filter string

        Returns:
            List of secret names

        Raises:
            ValueError: If listing fails
        """

        async def _list_secrets():
            try:
                parent = f"projects/{self.project_id}"

                secrets = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.list_secrets(
                        request={"parent": parent, "filter": filter_str or ""},
                        retry=self.retry_config,
                    ),
                )

                secret_names = [secret.name.split("/")[-1] for secret in secrets]
                logger.info(f"Listed {len(secret_names)} secrets")
                return secret_names

            except Exception as e:
                logger.error(f"Secret listing error: {e}")
                raise ValueError(f"Failed to list secrets: {e}") from e

        return await self.circuit_breaker.call(_list_secrets)
