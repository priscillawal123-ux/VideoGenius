"""
Google Cloud Secret Manager service for Video Genius.
"""

import json
import logging
from typing import Any, Dict, Optional

from google.api_core import exceptions
from google.cloud import secretmanager_v1 as sm

logger = logging.getLogger(__name__)


class SecretManagerService:
    """Service for managing secrets using Google Cloud Secret Manager."""

    def __init__(self, project_id: str):
        """Initialize Secret Manager client.

        Args:
            project_id: GCP project ID
        """
        self.project_id = project_id
        self._client: Optional[sm.SecretManagerServiceClient] = None
        self._parent: Optional[str] = None
        logger.info(f"Initialized SecretManagerService for project {project_id}")

    @property
    def client(self) -> sm.SecretManagerServiceClient:
        """Lazy initialize Secret Manager client."""
        if self._client is None:
            self._client = sm.SecretManagerServiceClient()
        return self._client

    @property
    def parent(self) -> str:
        """Lazy initialize parent path."""
        if self._parent is None:
            self._parent = f"projects/{self.project_id}"
        return self._parent

    def get_secret(self, secret_name: str, version: str = "latest") -> str:
        """Retrieve a secret value.

        Args:
            secret_name: Name of the secret
            version: Version of the secret (default: latest)

        Returns:
            Secret value as string

        Raises:
            ValueError: If secret not found or access fails
        """
        try:
            name = f"{self.parent}/secrets/{secret_name}/versions/{version}"
            response = self.client.access_secret_version(request={"name": name})
            secret_value = response.payload.data.decode("UTF-8")

            logger.info(f"Retrieved secret: {secret_name}")
            return secret_value

        except exceptions.NotFound:
            logger.error(f"Secret not found: {secret_name}")
            raise ValueError(f"Secret '{secret_name}' not found")
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            raise ValueError(f"Failed to retrieve secret: {e}") from e

    def create_secret(self, secret_name: str, secret_value: str) -> str:
        """Create a new secret.

        Args:
            secret_name: Name of the secret
            secret_value: Value to store

        Returns:
            Secret name

        Raises:
            ValueError: If creation fails
        """
        try:
            secret = sm.Secret()
            secret.replication.automatic = sm.Replication.Automatic()

            response = self.client.create_secret(
                request={
                    "parent": self.parent,
                    "secret_id": secret_name,
                    "secret": secret,
                }
            )

            # Add the secret version
            self.add_secret_version(secret_name, secret_value)

            logger.info(f"Created secret: {secret_name}")
            return response.name

        except exceptions.AlreadyExists:
            logger.warning(f"Secret already exists: {secret_name}")
            # Update existing secret
            return self.add_secret_version(secret_name, secret_value)
        except Exception as e:
            logger.error(f"Failed to create secret {secret_name}: {e}")
            raise ValueError(f"Failed to create secret: {e}") from e

    def add_secret_version(self, secret_name: str, secret_value: str) -> str:
        """Add a new version to an existing secret.

        Args:
            secret_name: Name of the secret
            secret_value: New value to store

        Returns:
            Version name

        Raises:
            ValueError: If update fails
        """
        try:
            secret_path = f"{self.parent}/secrets/{secret_name}"

            payload = secret_value.encode("UTF-8")
            response = self.client.add_secret_version(
                request={
                    "parent": secret_path,
                    "payload": {"data": payload},
                }
            )

            logger.info(f"Added version to secret: {secret_name}")
            return response.name

        except Exception as e:
            logger.error(f"Failed to add version to secret {secret_name}: {e}")
            raise ValueError(f"Failed to update secret: {e}") from e

    def list_secrets(self) -> list:
        """List all secrets in the project.

        Returns:
            List of secret names
        """
        try:
            secrets = []
            for secret in self.client.list_secrets(request={"parent": self.parent}):
                secrets.append(secret.name.split("/")[-1])

            logger.info(f"Listed {len(secrets)} secrets")
            return secrets

        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            return []

    def get_secret_json(
        self, secret_name: str, version: str = "latest"
    ) -> Dict[str, Any]:
        """Retrieve a secret and parse as JSON.

        Args:
            secret_name: Name of the secret
            version: Version of the secret

        Returns:
            Parsed JSON data

        Raises:
            ValueError: If secret not found or invalid JSON
        """
        try:
            secret_value = self.get_secret(secret_name, version)
            return json.loads(secret_value)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in secret {secret_name}: {e}")
            raise ValueError(f"Invalid JSON in secret: {e}") from e

    def create_secret_json(self, secret_name: str, data: Dict[str, Any]) -> str:
        """Create a secret with JSON data.

        Args:
            secret_name: Name of the secret
            data: Data to store as JSON

        Returns:
            Secret name
        """
        json_value = json.dumps(data, indent=2)
        return self.create_secret(secret_name, json_value)
