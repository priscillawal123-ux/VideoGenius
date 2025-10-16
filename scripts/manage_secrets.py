#!/usr/bin/env python3
"""
Video Genius - Secret Manager Python CLI Tool
Manage secrets using Google Cloud Secret Manager

This is a Python alternative to the bash script, providing better security
and integration with the Video Genius codebase.
"""

import argparse
import logging
import sys
from typing import Optional

import google.auth.exceptions
from google.api_core import exceptions
from google.auth import default
from google.cloud import secretmanager_v1 as sm

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class SecretManager:
    """Google Cloud Secret Manager client wrapper."""

    def __init__(self, project_id: Optional[str] = None):
        """Initialize Secret Manager client.

        Args:
            project_id: GCP project ID. If None, uses
                GOOGLE_CLOUD_PROJECT env var.
        """
        try:
            credentials, effective_project = default()
            self.project_id = project_id or effective_project

            if not self.project_id:
                raise ValueError(
                    "No project ID found. Set GOOGLE_CLOUD_PROJECT "
                    "or pass --project-id"
                )

            self.client = sm.SecretManagerServiceClient()
            self.parent = f"projects/{self.project_id}"

            logger.info(f"Connected to GCP project: {self.project_id}")

        except google.auth.exceptions.DefaultCredentialsError:
            logger.error(
                "Authentication failed. Please set up Google Cloud " "credentials:"
            )
            logger.error("  1. Run: gcloud auth application-default login")
            logger.error(
                "  2. Or set GOOGLE_APPLICATION_CREDENTIALS to a "
                "service account key file"
            )
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to initialize Secret Manager client: {e}")
            sys.exit(1)

    def list_secrets(self) -> None:
        """List all secrets in the project."""
        try:
            secrets = self.client.list_secrets(request={"parent": self.parent})

            print("NAME".ljust(30), "CREATED")
            print("-" * 50)

            for secret in secrets:
                name = secret.name.split("/")[-1]
                # Convert protobuf timestamp to datetime
                from datetime import datetime

                created_dt = datetime.fromtimestamp(secret.create_time.seconds)
                created = created_dt.strftime("%Y-%m-%d %H:%M:%S")
                print(f"{name.ljust(30)} {created}")

        except exceptions.PermissionDenied:
            logger.error(
                "Permission denied. Ensure your account has "
                "'Secret Manager Secret Accessor' role"
            )
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            sys.exit(1)

    def create_secret(self, name: str, value: str) -> None:
        """Create or update a secret.

        Args:
            name: Secret name
            value: Secret value
        """
        try:
            secret_id = f"{self.parent}/secrets/{name}"

            # Check if secret exists
            try:
                self.client.get_secret(request={"name": secret_id})
                # Secret exists, add new version
                logger.info(f"Updating existing secret: {name}")
                self.client.add_secret_version(
                    request={
                        "parent": secret_id,
                        "payload": {"data": value.encode("UTF-8")},
                    }
                )
            except exceptions.NotFound:
                # Secret doesn't exist, create it
                logger.info(f"Creating new secret: {name}")
                self.client.create_secret(
                    request={
                        "parent": self.parent,
                        "secret_id": name,
                        "secret": {"replication": {"automatic": {}}},
                    }
                )
                # Add the first version
                self.client.add_secret_version(
                    request={
                        "parent": secret_id,
                        "payload": {"data": value.encode("UTF-8")},
                    }
                )

            logger.info(f"Secret '{name}' updated successfully")

        except exceptions.PermissionDenied:
            logger.error(
                "Permission denied. Ensure your account has "
                "'Secret Manager Secret Version Manager' role"
            )
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to create/update secret: {e}")
            sys.exit(1)

    def get_secret(self, name: str, version: str = "latest") -> None:
        """Get secret value.

        Args:
            name: Secret name
            version: Secret version (default: latest)
        """
        try:
            secret_id = f"{self.parent}/secrets/{name}/versions/{version}"

            response = self.client.access_secret_version(request={"name": secret_id})
            value = response.payload.data.decode("UTF-8")

            print(value)

        except exceptions.NotFound:
            logger.error(f"Secret '{name}' or version '{version}' not found")
            sys.exit(1)
        except exceptions.PermissionDenied:
            logger.error(
                "Permission denied. Ensure your account has "
                "'Secret Manager Secret Accessor' role"
            )
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to get secret: {e}")
            sys.exit(1)

    def delete_secret(self, name: str) -> None:
        """Delete a secret.

        Args:
            name: Secret name
        """
        try:
            secret_id = f"{self.parent}/secrets/{name}"

            # Check if secret exists
            self.client.get_secret(request={"name": secret_id})

            # Confirm deletion
            try:
                confirm = input(
                    f"Are you sure you want to delete secret '{name}'? (y/N): "
                )
                if confirm.lower() not in ["y", "yes"]:
                    logger.info("Operation cancelled")
                    return
            except KeyboardInterrupt:
                logger.info("Operation cancelled")
                return

            # Delete all versions first
            versions = self.client.list_secret_versions(request={"parent": secret_id})
            for version in versions:
                if version.state.name != "DESTROYED":
                    self.client.destroy_secret_version(request={"name": version.name})

            # Delete the secret
            self.client.delete_secret(request={"name": secret_id})
            logger.info(f"Secret '{name}' deleted successfully")

        except exceptions.NotFound:
            logger.error(f"Secret '{name}' not found")
            sys.exit(1)
        except exceptions.PermissionDenied:
            logger.error(
                "Permission denied. Ensure your account has "
                "'Secret Manager Admin' role"
            )
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to delete secret: {e}")
            sys.exit(1)

    def setup_initial_secrets(self) -> None:
        """Setup initial secrets for Video Genius."""
        logger.info("Setting up initial secrets for Video Genius...")

        # JWT Secret Key
        import secrets

        jwt_secret = secrets.token_hex(32)
        self.create_secret("jwt-secret-key", jwt_secret)
        logger.info("JWT secret key created")

        # YouTube API Key (if environment variable exists)
        import os

        youtube_key = os.getenv("YOUTUBE_API_KEY")
        if youtube_key:
            self.create_secret("youtube-api-key", youtube_key)
            logger.info("YouTube API key secret created")
        else:
            logger.warning(
                "YOUTUBE_API_KEY not set. Set the environment variable "
                "and run again."
            )

        # YouTube Client Secrets (if file exists)
        if os.path.exists("client_secrets.json"):
            with open("client_secrets.json", "r") as f:
                client_secrets = f.read()
            self.create_secret("youtube-client-secrets", client_secrets)
            logger.info("YouTube client secrets created")
        else:
            logger.warning(
                "client_secrets.json not found. Download from " "Google Cloud Console."
            )

        logger.info("Initial secrets setup completed")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Video Genius - Secret Manager Python CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_secrets.py list
  python manage_secrets.py create my-secret "secret-value"
  python manage_secrets.py get my-secret
  python manage_secrets.py setup
        """,
    )

    parser.add_argument(
        "--project-id",
        help="GCP project ID (optional, uses GOOGLE_CLOUD_PROJECT if not set)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list command
    subparsers.add_parser("list", help="List all secrets")

    # create command
    create_parser = subparsers.add_parser("create", help="Create or update a secret")
    create_parser.add_argument("name", help="Secret name")
    create_parser.add_argument("value", help="Secret value")

    # get command
    get_parser = subparsers.add_parser("get", help="Get secret value")
    get_parser.add_argument("name", help="Secret name")
    get_parser.add_argument(
        "version", nargs="?", default="latest", help="Secret version (default: latest)"
    )

    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a secret")
    delete_parser.add_argument("name", help="Secret name")

    # setup command
    subparsers.add_parser("setup", help="Setup initial secrets for Video Genius")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize client
    sm_client = SecretManager(project_id=args.project_id)

    # Execute command
    if args.command == "list":
        sm_client.list_secrets()
    elif args.command == "create":
        sm_client.create_secret(args.name, args.value)
    elif args.command == "get":
        sm_client.get_secret(args.name, args.version)
    elif args.command == "delete":
        sm_client.delete_secret(args.name)
    elif args.command == "setup":
        sm_client.setup_initial_secrets()


if __name__ == "__main__":
    main()

