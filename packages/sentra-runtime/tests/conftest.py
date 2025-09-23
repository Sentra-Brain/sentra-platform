# tests/conftest.py
import pytest
import sys
import types
import pathlib

# ---------------------------------------------------------------------------
# Ensure package src paths available
# ---------------------------------------------------------------------------
_this_dir = pathlib.Path(__file__).resolve().parent
_runtime_src = _this_dir.parent / "src"
_shared_src = _this_dir.parent.parent / "sentra-shared" / "src"
for path in (_runtime_src, _shared_src):
    if path.exists() and str(path) not in sys.path:
        sys.path.insert(0, str(path))

# ---------------------------------------------------------------------------
# Stub mongo repository before imports
# ---------------------------------------------------------------------------
fake_mongo_module = types.ModuleType("sentra_core.infra.nosql.mongo_session_repository")
class _FakeMongoRepo:
    async def save(self, *a, **kw): return None
fake_repo = _FakeMongoRepo()
fake_mongo_module.MongoSessionRepository = lambda *a, **kw: fake_repo
fake_mongo_module.get_session_mongo_repository = lambda: fake_repo
fake_mongo_module.mongo_service_instance = fake_repo
sys.modules["sentra_core.infra.nosql.mongo_session_repository"] = fake_mongo_module

# ---------------------------------------------------------------------------
# anyio backend fixture
# ---------------------------------------------------------------------------
@pytest.fixture
def anyio_backend() -> str:
    """Force anyio tests to run on asyncio backend only."""
    return "asyncio"

# ---------------------------------------------------------------------------
# Stubs for google.adk / google.genai
# ---------------------------------------------------------------------------
fake_google = types.ModuleType("google")
sys.modules.setdefault("google", fake_google)
sys.modules["google.adk"] = types.ModuleType("google.adk")

# --- Event stub ---
class _StubEvent:
    def __init__(self, author: str, content=None, custom_metadata=None):
        self.author = author
        self.content = content
        self.custom_metadata = custom_metadata or {}

    def is_final_response(self) -> bool:
        return (self.custom_metadata or {}).get("type") == "message_final"

events_mod = types.ModuleType("google.adk.events")
events_mod.Event = _StubEvent
events_mod.EventActions = object
sys.modules["google.adk.events"] = events_mod
sys.modules["google.adk.events.event"] = types.ModuleType("google.adk.events.event")
sys.modules["google.adk.events.event"].Event = _StubEvent

# --- genai Content/Part stub ---
class _StubPart:
    def __init__(self, text: str | None = None):
        self.text = text

class _StubContent:
    def __init__(self, role: str, parts: list[_StubPart] | None = None):
        self.role = role
        self.parts = parts or []

sys.modules["google.genai"] = types.ModuleType("google.genai")
sys.modules["google.genai"].types = types.SimpleNamespace(Content=_StubContent, Part=_StubPart)

# --- Agent & BaseAgent stubs ---
class _StubBaseAgent: ...
sys.modules["google.adk.agents"] = types.ModuleType("google.adk.agents")
sys.modules["google.adk.agents"].BaseAgent = _StubBaseAgent
sys.modules["google.adk.agents"].Agent = _StubBaseAgent  # keep it simple

# --- RunConfig / StreamingMode stubs ---
class _StubRunConfig:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class _StubStreamingMode:
    SSE = "sse"

sys.modules["google.adk.agents.run_config"] = types.ModuleType("google.adk.agents.run_config")
sys.modules["google.adk.agents.run_config"].RunConfig = _StubRunConfig
sys.modules["google.adk.agents.run_config"].StreamingMode = _StubStreamingMode

# --- Sessions stubs ---
class _StubSession:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
sys.modules["google.adk.sessions"] = types.ModuleType("google.adk.sessions")
sys.modules["google.adk.sessions"].BaseSessionService = object
sys.modules["google.adk.sessions"].Session = _StubSession
sys.modules["google.adk.sessions.base_session_service"] = types.ModuleType(
    "google.adk.sessions.base_session_service"
)
sys.modules["google.adk.sessions.base_session_service"].ListSessionsResponse = object

# --- Memory service stub ---
class _FakeInMemoryMemoryService:
    async def add_session_to_memory(self, session): return None
    async def search_memory(self, app_name: str, user_id: str, query: str, limit: int = 5): return []

sys.modules["google.adk.memory"] = types.ModuleType("google.adk.memory")
sys.modules["google.adk.memory"].InMemoryMemoryService = _FakeInMemoryMemoryService

# --- LiteLlm stub ---
sys.modules["google.adk.models"] = types.ModuleType("google.adk.models")
sys.modules["google.adk.models.lite_llm"] = types.ModuleType("google.adk.models.lite_llm")
sys.modules["google.adk.models.lite_llm"].LiteLlm = object

# --- Runner stub with async generator ---
async def _stub_run_async(*args, **kwargs):
    yield _StubEvent(
        author="assistant",
        content=_StubContent("assistant", parts=[_StubPart("hi")]),
        custom_metadata={"type": "message_delta"},
    )
    yield _StubEvent(
        author="assistant",
        content=_StubContent("assistant", parts=[_StubPart("final")]),
        custom_metadata={"type": "message_final"},
    )

class _StubRunner:
    def __init__(self, *a, **kw): ...
    def run_async(self, *a, **kw):
        return _stub_run_async()

sys.modules["google.adk.runners"] = types.ModuleType("google.adk.runners")
sys.modules["google.adk.runners"].Runner = _StubRunner
