"""Pytest configuration and fixtures for test suite."""

import pytest


@pytest.fixture
def anyio_backend():
    """Configure anyio backend for async tests."""
    return "asyncio"
