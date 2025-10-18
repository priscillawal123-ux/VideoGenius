"""
Dependency injection container.
"""

from dependency_injector import containers, providers
from backend.core.config import get_settings
# from backend.infrastructure.database.bigquery_client import BigQueryClient
# from backend.interfaces.repositories.bigquery_video_repository import (
#     BigQueryVideoRepository,
# )
# from backend.domain.services.video_generator_service import VideoGeneratorService
# from backend.domain.services.video_processor import VideoProcessor
# from backend.application.use_cases.generate_video_use_case import GenerateVideoUseCase
# from backend.services.auth_service import AuthService
from backend.services.script_generator import ScriptGeneratorService
# from backend.infrastructure.messaging.cloud_tasks_client import CloudTasksClient
# from backend.infrastructure.messaging.pubsub_client import PubSubClient
# from backend.infrastructure.external_apis.vertex_ai_client import VertexAIClient
# from backend.infrastructure.repositories.sqlalchemy_user_repository import (
#     SQLAlchemyUserRepository,
# )
# from backend.infrastructure.services.vertex_ai_service import VertexAIService
# from backend.infrastructure.services.logging_notification_service import (
#     LoggingNotificationService,
# )
# from backend.database.session import get_db
# from backend.domain.repositories.video_repository import VideoRepository


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""

    # Configuration
    config = providers.Singleton(get_settings)

    # # Database
    # db_session = providers.Resource(get_db)

    # # Infrastructure Clients (commented - modules don't exist)
    # # bigquery_client = providers.Factory(...)
    # # vertex_ai_client = providers.Singleton(...)
    # # cloud_tasks_client = providers.Factory(...)
    # # pubsub_client = providers.Singleton(...)

    # # Repositories (commented - modules don't exist)
    # # video_repository = providers.Factory(...)
    # # user_repository = providers.Singleton(...)

    # # Domain Services (commented - modules don't exist)
    # # video_generator_service = providers.Singleton(...)
    # # video_processor = providers.Singleton(...)

    # # Infrastructure Services (commented - modules don't exist)
    # # vertex_ai_service = providers.Singleton(...)
    # # notification_service = providers.Singleton(...)

    # # Auth Service (commented - AuthService doesn't exist as class)
    # auth_service = providers.Factory(
    #     AuthService,
    # )

    # # Script Generator Service
    script_generator_service = providers.Singleton(
        ScriptGeneratorService,
        project_id=config.provided.google_project_id,
        location=config.provided.vertex_ai_location,
    )

    # # Use Cases (commented - modules don't exist)
    # # generate_video_use_case = providers.Singleton(...)


# Container instance
container = Container()


# Dependency functions for FastAPI routes
# def get_auth_service() -> AuthService:
#     """Get AuthService from container."""
#     return container.auth_service()


def get_script_service() -> ScriptGeneratorService:
    """Get ScriptGeneratorService from container."""
    return container.script_generator_service()

# Legacy functions commented out - modules don't exist
# def get_db_client() -> BigQueryClient:
# def get_cloud_tasks_client() -> CloudTasksClient:
# def get_pubsub_client() -> PubSubClient:
# def get_generate_video_use_case() -> GenerateVideoUseCase:
# def get_video_repository() -> VideoRepository:
