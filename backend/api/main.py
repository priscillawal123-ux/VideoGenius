"""
Main FastAPI application for Video Genius with Google Cloud optimizations.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware

from backend.api.routes.auth import router as auth_router
from backend.api.routes.gcp import router as gcp_router
from backend.api.routes.tasks import router as tasks_router
from backend.api.routes.webhooks import router as webhooks_router
# from backend.api.routes.videos import router as videos_router  # Legacy - modules don't exist
from backend.core.config import get_settings
from backend.core.exception_handlers import add_exception_handlers
from backend.core.logging import setup_logging
# from backend.core.monitoring import setup_monitoring
# from backend.core.rate_limiting import setup_rate_limiting

# Setup logging
setup_logging()
settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup/shutdown events."""
    logger.info("Starting Video Genius API...")

    # Startup tasks
    logger.info("Application startup complete")

    yield

    # Shutdown tasks
    logger.info("Shutting down Video Genius API...")


def create_application() -> FastAPI:
    """Create and configure FastAPI application with Google Cloud optimizations."""
    app = FastAPI(
        title="Video Genius API",
        description="""
        AI-powered video generation platform for creating engaging videos from text scripts.

        ## Features

        * **Video Generation**: Generate videos from text scripts using AI
        * **User Authentication**: JWT-based authentication system
        * **Cloud Storage**: Google Drive and Cloud Storage integration
        * **BigQuery Analytics**: Video generation analytics and tracking
        * **Real-time Status**: Monitor video generation progress

        ## Authentication

        Most endpoints require authentication. Use the `/auth/login` endpoint to obtain a JWT token,
        then include it in the Authorization header as `Bearer <token>`.

        ## Rate Limits

        * Video generation: 10 requests per hour for free users
        * API calls: 1000 requests per hour

        ## Support

        For support, contact: support@videogenius.com.br
        """,
        version="1.0.0",
        contact={
            "name": "Video Genius Support",
            "email": "support@videogenius.com.br",
            "url": "https://videogenius.com.br/support",
        },
        license_info={
            "name": "Proprietary",
            "url": "https://videogenius.com.br/license",
        },
        servers=[
            {
                "url": "https://videogenius.com.br",
                "description": "Production server",
            },
            {
                "url": "http://localhost:8080",
                "description": "Development server",
            },
        ],
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add trusted host middleware
    # app.add_middleware(
    #     TrustedHostMiddleware,
    #     allowed_hosts=settings.allowed_hosts,
    # )

    # Add global exception handlers
    add_exception_handlers(app)

    # Setup monitoring and tracing (disabled for Cloud Run)
    # setup_monitoring(app)

    # Setup rate limiting (disabled for Cloud Run)
    # setup_rate_limiting(app)

    # Include routers
    app.include_router(auth_router)
    app.include_router(gcp_router, prefix="/gcp", tags=["gcp"])
    app.include_router(tasks_router, tags=["tasks"])
    app.include_router(webhooks_router, tags=["webhooks"])
    # app.include_router(videos_router)  # Legacy - modules don't exist

    @app.get("/")
    async def root() -> dict:
        """Root endpoint."""
        return {
            "message": "Video Genius API",
            "status": "running",
            "version": "1.0.0",
        }

    @app.get("/health")
    async def health_check() -> dict:
        """Health check endpoint with detailed status."""
        return {
            "status": "healthy",
            "message": "Server is running",
            "environment": settings.environment,
            "gcp_project": settings.google_project_id,
            "features": {
                "circuit_breaker": settings.enable_circuit_breaker,
                "caching": settings.enable_caching,
                "uvloop": settings.use_uvloop,
            },
        }

    @app.get("/ready")
    async def readiness_check() -> dict:
        """Readiness check endpoint for Kubernetes/load balancers."""
        # Add actual dependency checks here (GCP services, database, etc.)
        return {
            "status": "ready",
            "checks": {
                "gcp_services": "ok",
                "database": "ok",
                "cache": "ok",
            },
        }

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn

    # Use uvloop for better performance if enabled
    if settings.use_uvloop:
        try:
            import uvloop

            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            logger.info("Using uvloop event loop policy")
        except ImportError:
            logger.warning("uvloop not available, using default event loop")

    # Start server with optimized settings
    uvicorn.run(
        "backend.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
        access_log=True,
        server_header=False,  # Security: don't expose server info
        date_header=False,  # Security: don't expose server time
    )
