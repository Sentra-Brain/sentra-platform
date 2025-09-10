import pytest
import types
from unittest.mock import MagicMock
import sys

# Stub mongo repository before imports
fake_mongo_module = types.ModuleType("sentra_core.infra.nosql.mongo_session_repository")
fake_repo = MagicMock()
fake_mongo_module.MongoSessionRepository = MagicMock(return_value=fake_repo)  # type: ignore[attr-defined]
fake_mongo_module.get_session_mongo_repository = lambda: fake_repo  # type: ignore[attr-defined]
fake_mongo_module.mongo_service_instance = fake_repo  # type: ignore[attr-defined]
sys.modules["sentra_core.infra.nosql.mongo_session_repository"] = fake_mongo_module


@pytest.fixture
def anyio_backend() -> str:
    """Force anyio tests to run on asyncio backend only."""
    return "asyncio"


# Stub out heavy google dependencies so tests can import engine modules.
fake_google = types.ModuleType("google")
sys.modules.setdefault("google", fake_google)
sys.modules["google.adk"] = types.ModuleType("google.adk")

# Add events stub
sys.modules["google.adk.events"] = types.ModuleType("google.adk.events")
sys.modules["google.adk.events"].Event = MagicMock()
sys.modules["google.adk.events"].EventActions = MagicMock()

sys.modules["google.adk.models"] = types.ModuleType("google.adk.models")
sys.modules["google.adk.models.lite_llm"] = types.ModuleType("google.adk.models.lite_llm")
sys.modules["google.adk.models.lite_llm"].LiteLlm = MagicMock()
sys.modules["google.adk.agents"] = types.ModuleType("google.adk.agents")
sys.modules["google.adk.agents"].Agent = MagicMock()
sys.modules["google.adk.agents.run_config"] = types.ModuleType("google.adk.agents.run_config")
sys.modules["google.adk.agents.run_config"].RunConfig = MagicMock()
sys.modules["google.adk.agents.run_config"].StreamingMode = MagicMock()
sys.modules["google.adk.runners"] = types.ModuleType("google.adk.runners")
sys.modules["google.adk.runners"].Runner = MagicMock()
sys.modules["google.adk.sessions"] = types.ModuleType("google.adk.sessions")
sys.modules["google.adk.sessions"].BaseSessionService = MagicMock()
sys.modules["google.adk.sessions"].Session = MagicMock()
sys.modules["google.adk.sessions.base_session_service"] = types.ModuleType(
    "google.adk.sessions.base_session_service"
)
sys.modules["google.adk.sessions.base_session_service"].ListSessionsResponse = MagicMock()
sys.modules["google.genai"] = types.ModuleType("google.genai")
sys.modules["google.genai"].types = types.SimpleNamespace(Content=MagicMock, Part=MagicMock)
