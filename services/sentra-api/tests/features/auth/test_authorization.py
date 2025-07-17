# import pytest
# from unittest.mock import patch, MagicMock
# from jose import jwt
# from fastapi import HTTPException
# from dataclasses import dataclass
# from sentra_brain_api.crosscutting.authorization import get_authenticated_user, get_admin_user
# from sentra_brain_api.core.config import settings

# @dataclass
# class FakeUser:
#     id: int
#     username: str
#     roles: str
#     disabled: bool

# @pytest.fixture
# def valid_token():
#     data = {"sub": "testuser", "roles": "user"}
#     return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)

# @pytest.fixture
# def valid_admin_token():
#     data = {"sub": "adminuser", "roles": "user,admin"}
#     return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)

# class TestAuthorizationFunctions:

#     def test_get_authenticated_user_success(self, valid_token):
#         mock_user = FakeUser(id=1, username="testuser", roles="user", disabled=False)

#         with patch("sentra_brain_api.features.user.repository.UserRepository") as mock_repo_class:
#             mock_repo_class.return_value.get_by_username.return_value = mock_user

#             user = get_authenticated_user(token=valid_token, db=MagicMock())
#             assert user.username == "testuser"
#             assert user.disabled is False

#     def test_get_authenticated_user_user_not_found(self, valid_token):
#         with patch("sentra_brain_api.features.user.repository.UserRepository") as mock_repo_class:
#             mock_repo_class.return_value.get_by_username.return_value = None

#             with pytest.raises(HTTPException) as exc_info:
#                 get_authenticated_user(token=valid_token, db=MagicMock())
#             assert exc_info.value.status_code == 401

#     def test_get_authenticated_user_disabled(self, valid_token):
#         mock_user = FakeUser(id=1, username="testuser", roles="user", disabled=True)

#         with patch("sentra_brain_api.features.user.repository.UserRepository") as mock_repo_class:
#             mock_repo_class.return_value.get_by_username.return_value = mock_user

#             with pytest.raises(HTTPException) as exc_info:
#                 get_authenticated_user(token=valid_token, db=MagicMock())
#             assert exc_info.value.status_code == 403

#     def test_get_admin_user_success(self, valid_admin_token):
#         mock_user = FakeUser(id=1, username="adminuser", roles="user,admin", disabled=False)

#         with patch("sentra_brain_api.features.user.repository.UserRepository") as mock_repo_class:
#             mock_repo_class.return_value.get_by_username.return_value = mock_user

#             user = get_admin_user(token=valid_admin_token, db=MagicMock())
#             assert "admin" in user.roles

#     def test_get_admin_user_forbidden(self, valid_token):
#         mock_user = FakeUser(id=1, username="testuser", roles="user", disabled=False)

#         with patch("sentra_brain_api.features.user.repository.UserRepository") as mock_repo_class:
#             mock_repo_class.return_value.get_by_username.return_value = mock_user

#             with pytest.raises(HTTPException) as exc_info:
#                 get_admin_user(token=valid_token, db=MagicMock())
#             assert exc_info.value.status_code == 403
