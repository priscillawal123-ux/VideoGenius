"""
Main FastAPI application for Video Genius with modular architecture.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.settings import get_config
from src.videos.router import router as videos_router

# Get configuration
config = get_config()


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=config.global_config.app_name,
        description="AI-powered video generation platform",
        version=config.global_config.app_version,
        docs_url="/docs" if config.global_config.environment == "development" else None,
        redoc_url=(
            "/redoc" if config.global_config.environment == "development" else None
        ),
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.global_config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=config.global_config.cors_headers,
    )

    # Include routers
    app.include_router(videos_router)

    @app.get("/")
    async def root() -> dict:
        """Root endpoint."""
        return {
            "message": f"{config.global_config.app_name} API",
            "status": "running",
            "version": config.global_config.app_version,
        }

    @app.get("/health")
    async def health_check() -> dict:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "message": "Server is running",
            "version": config.global_config.app_version,
        }

    return app


app = create_application()
