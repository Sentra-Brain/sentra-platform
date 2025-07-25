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

def test_create_refresh_token(auth_service):
    # Test refresh token creation
    data = {"sub": "testuser", "roles": "user"}
    token = auth_service.create_refresh_token(data, timedelta(days=7))
    decoded = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert decoded["sub"] == "testuser"
    assert decoded["roles"] == "user"
    assert decoded["type"] == "refresh"

def test_validate_refresh_token_success(auth_service):
    # Test successful refresh token validation
    data = {"sub": "testuser", "roles": "user"}
    token = auth_service.create_refresh_token(data, timedelta(days=7))
    
    # Mock user retrieval
    mock_user = MagicMock(spec=UserEntity)
    mock_user.username = "testuser"
    mock_user.disabled = False
    auth_service.user_repo.get_by_username.return_value = mock_user
    
    result = auth_service.validate_refresh_token(token)
    assert result == mock_user

def test_validate_refresh_token_invalid_type(auth_service):
    # Test refresh token validation with wrong token type
    data = {"sub": "testuser", "roles": "user"}  # Missing "type": "refresh"
    token = auth_service.create_access_token(data, timedelta(minutes=15))
    
    result = auth_service.validate_refresh_token(token)
    assert result is None

def test_validate_refresh_token_user_not_found(auth_service):
    # Test refresh token validation when user not found
    data = {"sub": "testuser", "roles": "user"}
    token = auth_service.create_refresh_token(data, timedelta(days=7))
    
    auth_service.user_repo.get_by_username.return_value = None
    auth_service.user_repo.get_by_email.return_value = None
    
    result = auth_service.validate_refresh_token(token)
    assert result is None

def test_validate_refresh_token_disabled_user(auth_service):
    # Test refresh token validation with disabled user
    data = {"sub": "testuser", "roles": "user"}
    token = auth_service.create_refresh_token(data, timedelta(days=7))
    
    mock_user = MagicMock(spec=UserEntity)
    mock_user.username = "testuser"
    mock_user.disabled = True
    auth_service.user_repo.get_by_username.return_value = mock_user
    
    result = auth_service.validate_refresh_token(token)
    assert result is None

def test_validate_refresh_token_expired(auth_service):
    # Test refresh token validation with expired token
    data = {"sub": "testuser", "roles": "user"}
    token = auth_service.create_refresh_token(data, timedelta(microseconds=1))  # Very short expiry
    
    import time
    time.sleep(0.001)  # Wait for token to expire
    
    result = auth_service.validate_refresh_token(token)
    assert result is None
