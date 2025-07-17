from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from sentra_brain_api.core.config import settings
from sentra_brain_api.infra.postgres_service import get_db, init_db

@pytest.fixture(scope="session", autouse=True)
def load_settings():
    # Set up the settings for the tests
    settings.secret_key = "your_secret_key"
    settings.algorithm = "HS256"
    settings.access_token_expire_minutes = 30
    settings.database_url = "sqlite:///./test_qna.db"
    settings.initial_admin_username = "admin"
    settings.initial_admin_email = "admin@example.com"
    settings.initial_admin_password = "P@ssw0rd!"

    
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
