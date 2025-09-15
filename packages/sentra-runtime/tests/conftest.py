import pytest
import types
from unittest.mock import MagicMock
import sys
import pathlib

# Ensure package src path available for imports when running tests directly.
_this_dir = pathlib.Path(__file__).resolve().parent
_runtime_src = _this_dir.parent / "src"
if str(_runtime_src) not in sys.path:
    sys.path.insert(0, str(_runtime_src))
# Also include sentra-shared package source for settings import
_shared_src = _this_dir.parent.parent / "sentra-shared" / "src"
if _shared_src.exists() and str(_shared_src) not in sys.path:
    sys.path.insert(0, str(_shared_src))

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
class _StubEvent:  # pragma: no cover - simple attribute carrier for tests
    def __init__(self, author: str, content=None, custom_metadata=None):
        self.author = author
        self.content = content
        self.custom_metadata = custom_metadata or {}

    def is_final_response(self) -> bool:
        return (self.custom_metadata or {}).get("type") == "message_final"


events_mod = types.ModuleType("google.adk.events")
events_mod.Event = _StubEvent
events_mod.EventActions = MagicMock()
sys.modules["google.adk.events"] = events_mod
# Provide nested module path import ``google.adk.events.event`` expected by runtime
events_event_mod = types.ModuleType("google.adk.events.event")
events_event_mod.Event = events_mod.Event
sys.modules["google.adk.events.event"] = events_event_mod

sys.modules["google.adk.models"] = types.ModuleType("google.adk.models")
sys.modules["google.adk.models.lite_llm"] = types.ModuleType("google.adk.models.lite_llm")
sys.modules["google.adk.models.lite_llm"].LiteLlm = MagicMock()
sys.modules["google.adk.agents"] = types.ModuleType("google.adk.agents")
class _StubBaseAgent:  # pragma: no cover - simple isinstance target
    pass

sys.modules["google.adk.agents"].Agent = MagicMock()
sys.modules["google.adk.agents"].BaseAgent = _StubBaseAgent
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

# Memory service stub (async methods expected by runtime.memory)
class _FakeInMemoryMemoryService:  # pragma: no cover - simple test stub
    async def add_session_to_memory(self, session):
        return None

    async def search_memory(self, app_name: str, user_id: str, query: str, limit: int = 5):
        return []

sys.modules["google.adk.memory"] = types.ModuleType("google.adk.memory")
sys.modules["google.adk.memory"].InMemoryMemoryService = _FakeInMemoryMemoryService
sys.modules["google.genai"] = types.ModuleType("google.genai")

class _StubPart:  # pragma: no cover
    def __init__(self, text: str | None = None):
        self.text = text

class _StubContent:  # pragma: no cover
    def __init__(self, role: str, parts: list[_StubPart] | None = None):
        self.role = role
        self.parts = parts or []

sys.modules["google.genai"].types = types.SimpleNamespace(Content=_StubContent, Part=_StubPart)
