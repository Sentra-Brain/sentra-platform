from enum import Enum
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

# Ensure sentra_core package is importable when running tests in isolation
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "sentra-core"))


class MockLLMEngine(str, Enum):
    LLAMA = "llama"
    VLLM = "vllm"


@pytest.fixture(autouse=True)
def mock_settings_and_engine(monkeypatch):
    """Provide isolated settings and LLMEngine for tests."""
    from sentra_engine.adapters import llm_adapter_factory

    mock_settings = SimpleNamespace(
        llm_engine=MockLLMEngine.VLLM,
        llama_server_url="http://llama",  # pragma: no cover - test values
        vllm_server_url="http://vllm",  # pragma: no cover - test values
        llm_request_timeout=30,
    )

    monkeypatch.setattr(llm_adapter_factory, "settings", mock_settings)
    monkeypatch.setattr(llm_adapter_factory, "LLMEngine", MockLLMEngine)
    yield
