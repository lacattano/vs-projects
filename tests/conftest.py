"""Pytest configuration and fixtures for test suite."""

import pytest


@pytest.fixture
def anyio_backend() -> str:
    """Configure anyio backend for async tests."""
    return "asyncio"
