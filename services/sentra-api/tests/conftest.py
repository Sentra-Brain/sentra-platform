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
    "RABBITMQ_QUEUE": "test_queue"
})

# 🚨 Patch mongo_session_repository BEFORE it's imported anywhere
fake_mongo_module = types.ModuleType("sentra_core.infra.nosql.mongo_session_repository")
fake_repo = MagicMock()
fake_mongo_module.MongoSessionRepository = MagicMock(return_value=fake_repo)  # type: ignore[attr-defined]
fake_mongo_module.get_session_mongo_repository = lambda: fake_repo  # type: ignore[attr-defined]
fake_mongo_module.mongo_service_instance = fake_repo  # type: ignore[attr-defined]
sys.modules["sentra_core.infra.nosql.mongo_session_repository"] = fake_mongo_module

# 🚨 Patch ConversationEngine so it never calls real LLM/RAG
fake_engine = MagicMock()
sys.modules["sentra_engine.engine"] = types.ModuleType(
    "sentra_engine.engine"
)
sys.modules["sentra_engine.engine"].ConversationEngine = MagicMock(return_value=fake_engine) # type: ignore[attr-defined]

# ✅ Now safe to import rest of your dependencies
from sentra_core.infra.sql.postgres_settings import settings as pg_settings
from sentra_core.infra.nosql.mongo_settings import settings as mongo_settings
from sentra_core.infra.amqp.rabbitmq_settings import settings as rabbitmq_settings
from sentra_core.infra.sql.postgres_service import get_db
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
