# conftest.py
from pathlib import Path
from unittest.mock import MagicMock
from dotenv import load_dotenv
import sys
import os
import types
import pytest

# Load .env.test
env_path = Path(__file__).resolve().parent / ".env.test"
load_dotenv(dotenv_path=env_path, override=True)

# Support relative PYTHONPATH from .env
pythonpath = os.environ.get("PYTHONPATH")
if pythonpath:
    resolved_path = (Path(__file__).resolve().parent / pythonpath).resolve()
    if resolved_path.exists():
        sys.path.insert(0, str(resolved_path))

# Set TESTING environment variable
os.environ.setdefault("TESTING", "true")

os.environ.update({
    "DATABASE_URL": "sqlite:///./test_qna.db",
    "INITIAL_ADMIN_USERNAME": "admin",
    "INITIAL_ADMIN_EMAIL": "admin@example.com",
    "INITIAL_ADMIN_PASSWORD": "P@ssw0rd!",
    "SECRET_KEY": "dummy_secret_key",
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "MONGO_URL": "mongodb://localhost:27017",
    "LLM_ENGINE": "vllm",
    "LLAMA_SERVER_URL": "http://llama:8080",
    "VLLM_SERVER_URL": "http://vllm:8000",
    "RABBITMQ_HOST": "localhost",
    "RABBITMQ_PORT": "5672",
    "RABBITMQ_USER": "guest",
    "RABBITMQ_PASSWORD": "guest",
    "RABBITMQ_QUEUE": "test_queue",
    "RAG_SERVER_URL": "http://localhost:8001",
    "RAG_QUERY_TIMEOUT": "10",
})

# 🚨 Patch mongo_session_repository BEFORE it's imported anywhere
fake_mongo_module = types.ModuleType("sentra.infra.nosql.mongo_session_repository")
fake_repo = MagicMock()
fake_mongo_module.MongoSessionRepository = MagicMock(return_value=fake_repo)  # type: ignore[attr-defined]
fake_mongo_module.get_session_mongo_repository = lambda: fake_repo  # type: ignore[attr-defined]
fake_mongo_module.mongo_service_instance = fake_repo  # type: ignore[attr-defined]
sys.modules["sentra.infra.nosql.mongo_session_repository"] = fake_mongo_module

# 🚨 Patch ConversationEngine so it never calls real LLM/RAG
fake_engine = MagicMock()
sys.modules["sentra.runtime.engine"] = types.ModuleType(
    "sentra.runtime.engine"
)
sys.modules["sentra.runtime.engine"].ConversationEngine = MagicMock(return_value=fake_engine) # type: ignore[attr-defined]

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
sys.modules["google.adk.agents"].Agent = _StubBaseAgent
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

# ✅ Now safe to import rest of your dependencies
from sentra.infra.sql.postgres_settings import settings as pg_settings
from sentra.infra.nosql.mongo_settings import settings as mongo_settings
from sentra.infra.amqp.rabbitmq_settings import settings as rabbitmq_settings
from sentra.infra.sql.postgres_service import get_db
from fastapi.testclient import TestClient

@pytest.fixture(scope="session", autouse=True)
def load_settings():
    pg_settings.secret_key = "your_secret_key"
    pg_settings.algorithm = "HS256"
    pg_settings.access_token_expire_minutes = 30
    pg_settings.database_url = "sqlite:///./test_qna.db"
    pg_settings.initial_admin_username = "admin"
    pg_settings.initial_admin_email = "admin@example.com"
    pg_settings.initial_admin_password = "P@ssw0rd!"
    mongo_settings.mongo_url = "mongodb://localhost:27017"
    rabbitmq_settings.rabbitmq_host = "localhost"
    rabbitmq_settings.rabbitmq_port = 5672
    rabbitmq_settings.rabbitmq_user = "guest"
    rabbitmq_settings.rabbitmq_password = "guest"
    rabbitmq_settings.rabbitmq_queue = "test_queue"
    rag_server_url="http://localhost:8001"
    yield

@pytest.fixture(scope='module')
def mock_db_session():
    yield MagicMock()

@pytest.fixture
def client(mock_db_session):
    from sentra_brain_api.main import create_app
    from sentra_brain_api.core.lifecycle_config import AppLifecycleConfig

    app = create_app(AppLifecycleConfig(init_mcp=False, init_db=False))
    app.dependency_overrides[get_db] = lambda: mock_db_session
    yield TestClient(app)
    app.dependency_overrides.clear()
