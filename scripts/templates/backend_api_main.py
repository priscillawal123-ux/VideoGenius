# Video Genius - FastAPI Main Application Template
# Versão: 1.0.0

"""
Main FastAPI application for Video Genius.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from backend.core.config import get_settings
from backend.core.logging import setup_logging

# Setup logging
setup_logging()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting Video Genius API...")

    yield

    # Shutdown
    print("🛑 Shutting down Video Genius API...")


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Video Genius API",
        description="AI-powered video generation platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )

    return app


app = create_application()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Video Genius API", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}