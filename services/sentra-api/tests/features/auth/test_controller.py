import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sentra_brain_api.main import app
from sentra_brain_api.infra.postgres_service import get_db
from sentra_brain_api.features.auth.auth_service import AuthService
from sentra_brain_api.domain.user_entity import UserEntity

client = TestClient(app)

@pytest.fixture
def user_entity():
    return UserEntity(
        id=1,
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashedpassword",
        roles="user",
        disabled=False
    )

@pytest.fixture(autouse=True)
def override_dependencies(user_entity):
    fake_db = MagicMock()

    fake_user_repo = MagicMock()
    fake_user_repo.get_by_username.return_value = user_entity

    fake_db.query.return_value = fake_user_repo
    app.dependency_overrides[get_db] = lambda: fake_db

    yield

    app.dependency_overrides.clear()

class TestAuthController:

    @patch("sentra_brain_api.features.auth.auth_service.AuthService.authenticate_user")
    @patch("sentra_brain_api.features.auth.auth_service.AuthService.create_access_token")
    @patch("sentra_brain_api.features.auth.auth_service.AuthService.create_refresh_token")
    def test_authenticate_success(self, mock_create_refresh_token, mock_create_access_token, mock_authenticate_user, user_entity):
        mock_authenticate_user.return_value = user_entity
        mock_create_access_token.return_value = "fake-access-token"
        mock_create_refresh_token.return_value = "fake-refresh-token"

        response = client.post("/auth/token", data={"username": "testuser", "password": "password"})

        assert response.status_code == 200
        assert response.json() == {
            "access_token": "fake-access-token",
            "refresh_token": "fake-refresh-token",
            "token_type": "bearer"
        }

        mock_authenticate_user.assert_called_once_with("testuser", "password")
        mock_create_access_token.assert_called_once()
        mock_create_refresh_token.assert_called_once()

    @patch("sentra_brain_api.features.auth.auth_service.AuthService.authenticate_user")
    def test_authenticate_invalid_credentials(self, mock_authenticate_user):
        mock_authenticate_user.return_value = None

        response = client.post("/auth/token", data={"username": "wronguser", "password": "wrongpass"})
        assert response.status_code == 401
    
        body = response.json()["detail"]
        assert body["error"]["code"] == "AUTH_FAILED"
        assert body["error"]["message"] == "Incorrect username or password"

        mock_authenticate_user.assert_called_once_with("wronguser", "wrongpass")

    @patch("sentra_brain_api.features.auth.auth_service.AuthService.validate_refresh_token")
    @patch("sentra_brain_api.features.auth.auth_service.AuthService.create_access_token")
    def test_refresh_token_success(self, mock_create_access_token, mock_validate_refresh_token, user_entity):
        mock_validate_refresh_token.return_value = user_entity
        mock_create_access_token.return_value = "new-access-token"

        response = client.post("/auth/refresh", json={"refresh_token": "valid-refresh-token"})

        assert response.status_code == 200
        assert response.json() == {
            "access_token": "new-access-token",
            "token_type": "bearer"
        }

        mock_validate_refresh_token.assert_called_once_with("valid-refresh-token")
        mock_create_access_token.assert_called_once()

    @patch("sentra_brain_api.features.auth.auth_service.AuthService.validate_refresh_token")
    def test_refresh_token_invalid(self, mock_validate_refresh_token):
        mock_validate_refresh_token.return_value = None

        response = client.post("/auth/refresh", json={"refresh_token": "invalid-refresh-token"})

        assert response.status_code == 401
        body = response.json()["detail"]
        assert body["error"]["code"] == "INVALID_REFRESH_TOKEN"
        assert body["error"]["message"] == "Invalid or expired refresh token"

        mock_validate_refresh_token.assert_called_once_with("invalid-refresh-token")
