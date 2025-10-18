"""
Dependency injection container.
"""

from dependency_injector import containers, providers
from backend.core.config import get_settings
from backend.infrastructure.database.bigquery_client import BigQueryClient
from backend.interfaces.repositories.bigquery_video_repository import (
    BigQueryVideoRepository,
)
from backend.domain.services.video_generator_service import VideoGeneratorService
from backend.domain.services.video_processor import VideoProcessor
from backend.application.use_cases.generate_video_use_case import GenerateVideoUseCase
from backend.services.auth_service import AuthService
from backend.services.script_generator import ScriptGeneratorService
from backend.infrastructure.messaging.cloud_tasks_client import CloudTasksClient
from backend.infrastructure.messaging.pubsub_client import PubSubClient
from backend.infrastructure.external_apis.vertex_ai_client import VertexAIClient
from backend.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from backend.infrastructure.services.vertex_ai_service import VertexAIService
from backend.infrastructure.services.logging_notification_service import (
    LoggingNotificationService,
)
from backend.database.session import get_db
from backend.domain.repositories.video_repository import VideoRepository


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""

    # Configuration
    config = providers.Singleton(get_settings)

    # Database
    db_session = providers.Resource(get_db)

    # Infrastructure Clients
    # Use Factory to allow tests to patch BigQueryClient class before instantiation
    bigquery_client = providers.Factory(
        BigQueryClient,
        project_id=config.provided.google_project_id,
        dataset_id=config.provided.bigquery_dataset,
    )

    vertex_ai_client = providers.Singleton(
        VertexAIClient,
        project_id=config.provided.google_project_id,
        location=config.provided.vertex_ai_location,
    )

    # Use Factory so tests can patch CloudTasksClient easily
    cloud_tasks_client = providers.Factory(
        CloudTasksClient,
        project_id=config.provided.google_project_id,
        location=config.provided.vertex_ai_location,
    )

    pubsub_client = providers.Singleton(
        PubSubClient, project_id=config.provided.google_project_id
    )

    # Repositories
    # Use Factory so repository and its client are instantiated at call-time
    # allowing tests that patch BigQueryClient to take effect.
    video_repository = providers.Factory(
        BigQueryVideoRepository, bigquery_client=bigquery_client
    )

    user_repository = providers.Singleton(
        SQLAlchemyUserRepository, db_session=db_session
    )

    # Domain Services
    video_generator_service = providers.Singleton(
        VideoGeneratorService, video_repository=video_repository
    )

    video_processor = providers.Singleton(
        VideoProcessor, video_repository=video_repository
    )

    # Infrastructure Services
    vertex_ai_service = providers.Singleton(
        VertexAIService,
        project_id=config.provided.google_project_id,
        location=config.provided.vertex_ai_location,
    )

    # Application Services
    notification_service = providers.Singleton(LoggingNotificationService)

    # Auth Service
    auth_service = providers.Factory(
        AuthService,
        user_repository=user_repository,
    )

    script_generator_service = providers.Singleton(
        ScriptGeneratorService,
        project_id=config.provided.google_project_id,
        location=config.provided.vertex_ai_location,
    )

    # Use Cases
    generate_video_use_case = providers.Singleton(
        GenerateVideoUseCase,
        video_repository=video_repository,
        video_generator_service=video_generator_service,
        vertex_ai_service=vertex_ai_service,
        notification_service=notification_service,
    )


# Container instance
container = Container()


# Dependency functions for FastAPI routes
def get_auth_service() -> AuthService:
    """Get AuthService from container."""
    return container.auth_service()


def get_script_service() -> ScriptGeneratorService:
    """Get ScriptGeneratorService from container."""
    return container.script_generator_service()


def get_db_client() -> BigQueryClient:
    """Get BigQueryClient from container."""
    # Instantiate at call time so tests can patch BigQueryClient class before
    # this function is called (patch target: backend.infrastructure.database.bigquery_client.BigQueryClient)
    cfg = container.config()
    from backend.infrastructure.database.bigquery_client import BigQueryClient

    return BigQueryClient(
        project_id=cfg.google_project_id, dataset_id=cfg.bigquery_dataset
    )


def get_cloud_tasks_client() -> CloudTasksClient:
    """Get CloudTasksClient from container."""
    # Instantiate at call time so tests can patch CloudTasksClient class before
    # this function is called (patch target: backend.infrastructure.messaging.cloud_tasks_client.CloudTasksClient)
    cfg = container.config()
    # Import via compatibility shim so tests that patch
    # 'backend.services.cloud_tasks_client.CloudTasksClient' are honored.
    from backend.services.cloud_tasks_client import CloudTasksClient

    return CloudTasksClient(
        project_id=cfg.google_project_id, location=cfg.vertex_ai_location
    )


def get_pubsub_client() -> PubSubClient:
    """Get PubSubClient from container."""
    return container.pubsub_client()


def get_generate_video_use_case() -> GenerateVideoUseCase:
    """Get GenerateVideoUseCase from container."""
    return container.generate_video_use_case()


def get_video_repository() -> VideoRepository:
    """Get video repository from container."""
    return container.video_repository()
