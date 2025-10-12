"""
Pytest configuration and shared fixtures for Video Genius tests.

This module provides common test fixtures and configuration used
across all test modules.
"""

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.core.config import settings


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client fixture.

    Returns:
        TestClient: Configured FastAPI test client
    """
    return TestClient(app)


@pytest.fixture
def test_settings():
    """Test settings fixture.

    Returns:
        Settings: Application settings for testing
    """
    return settings


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test.

    This fixture runs automatically before each test.
    """
    # Set test environment if needed
    pass