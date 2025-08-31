import pytest


@pytest.fixture
def anyio_backend() -> str:
    """Force anyio tests to run on asyncio backend only."""
    return "asyncio"
