import pytest
from unittest.mock import MagicMock, patch
from datetime import timedelta
from jose import jwt
from sentra_brain_api.features.auth.auth_service import AuthService
from sentra_brain_api.domain.user_entity import UserEntity
from sentra_brain_api.core.config import settings

class FakeUserRepository():
    _instance = None
    def __init__(self):
        self.users = {
            "testuser": UserEntity(
                id=1,
                username="testuser",
            )
        }
    
    def get_by_username(self, username: str) -> UserEntity | None:
        return self.users.get(username)

    def get_by_email(self, email: str) -> UserEntity | None:
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
@pytest.fixture
def user_repo():
    repo = MagicMock(spec=FakeUserRepository)
    repo.get_by_username.return_value = None
    repo.get_by_email.return_value = None
    return repo

@pytest.fixture
def auth_service(user_repo):
    return AuthService(user_repo)

def test_authenticate_user_success(auth_service):
    # Mock the password verification process
    with patch('passlib.context.CryptContext.verify', return_value=True):
        # Create a mock user with the necessary attributes
        mock_user = MagicMock(spec=UserEntity) 
        mock_user.username = "testuser"
        auth_service.user_repo.get_by_username.return_value = mock_user 
        result = auth_service.authenticate_user("testuser", "password")
        assert result.username == "testuser"

def test_authenticate_user_failure(auth_service):
    # Simulate a user not found scenario
    auth_service.user_repo.get_by_username.return_value = None
    result = auth_service.authenticate_user("wronguser", "password")
    assert result is None  # Ensure authentication fails

def test_create_access_token(auth_service):
    # Test JWT token creation
    data = {"sub": "testuser", "roles": "user"}
    token = auth_service.create_access_token(data, timedelta(minutes=15))
    decoded = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert decoded["sub"] == "testuser"  # Verify token content
    assert decoded["roles"] == "user"

def test_get_password_hash(auth_service):
    # Test password hashing
    password = "password123"
    hashed_password = auth_service.get_password_hash(password)
    assert hashed_password != password  # Ensure the password is hashed

def test_verify_password(auth_service):
    # Test password verification
    password = "password123"
    hashed_password = auth_service.get_password_hash(password)
    assert auth_service._verify_password(password, hashed_password)  # Ensure the password verifies correctly
