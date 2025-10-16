"""
Centralized configuration management for Video Genius.
"""

from src.core.config import global_config


class AppConfig:
    """Centralized application configuration."""

    def __init__(self):
        self.global_config = global_config
        # Domain configs will be loaded lazily to avoid circular imports
        self._auth = None
        self._database = None
        self._storage = None
        self._videos = None

    @property
    def auth(self):
        """Get auth configuration."""
        if self._auth is None:
            from src.auth.config import AuthConfig

            self._auth = AuthConfig()
        return self._auth

    @property
    def database(self):
        """Get database configuration."""
        if self._database is None:
            from src.database.config import DatabaseConfig

            self._database = DatabaseConfig()
        return self._database

    @property
    def storage(self):
        """Get storage configuration."""
        if self._storage is None:
            from src.storage.config import StorageConfig

            self._storage = StorageConfig()
        return self._storage

    @property
    def videos(self):
        """Get videos configuration."""
        if self._videos is None:
            from src.videos.config import VideoConfig

            self._videos = VideoConfig()
        return self._videos

    @property
    def google_project_id(self) -> str:
        """Get Google Cloud project ID."""
        return self.database.google_project_id

    @property
    def bigquery_dataset(self) -> str:
        """Get BigQuery dataset name."""
        return self.database.bigquery_dataset

    @property
    def cloud_storage_bucket(self) -> str:
        """Get Cloud Storage bucket name."""
        return self.storage.cloud_storage_bucket


# Global application configuration instance
config = AppConfig()


def get_config() -> AppConfig:
    """Get application configuration."""
    return config
