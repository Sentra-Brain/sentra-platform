from pathlib import Path
from unittest.mock import MagicMock
from dotenv import load_dotenv
import sys
import os

from fastapi.testclient import TestClient
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
if "TESTING" not in os.environ:
    # This is to ensure that the application knows it's in test mode
    # and can skip certain initializations like database connections.
    os.environ["TESTING"] = "true"

os.environ.update({
    "DATABASE_URL": "sqlite:///./test_qna.db",
    "INITIAL_ADMIN_USERNAME": "admin",
    "INITIAL_ADMIN_EMAIL": "admin@example.com",
    "INITIAL_ADMIN_PASSWORD": "P@ssw0rd!",
    "SECRET_KEY": "dummy_secret_key",
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "MONGO_URL": "mongodb://localhost:27017"
})
from sentra_core.infra.sql.postgres_settings import settings as pg_settings
from sentra_core.infra.nosql.mongo_settings import settings as mongo_settings
from sentra_core.infra.amqp.rabbitmq_settings import settings as rabbitmq_settings
from sentra_core.infra.sql.postgres_service import get_db, init_db

@pytest.fixture(scope="session", autouse=True)
def load_settings():
    # Set up the settings for the tests
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

    # Mock init_db to avoid its execution
    # monkeypatch.setattr('sentra_brain_api.infra.postgres_service.init_db', lambda: None)
    yield

@pytest.fixture(scope='module')
def mock_db_session():
    # Create a mock database session
    session = MagicMock()
    yield session

@pytest.fixture
def client(mock_db_session):
    from sentra_brain_api.main import app 
    def get_db_override():
        return mock_db_session

    app.dependency_overrides[get_db] = get_db_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
