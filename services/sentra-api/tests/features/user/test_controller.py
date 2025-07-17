# import pytest
# from fastapi.testclient import TestClient
# from unittest.mock import MagicMock
# from sentra_brain_api.main import create_app
# from sentra_brain_api.crosscutting.authorization import get_authenticated_user
# from sentra_brain_api.infra.postgres_service import get_db
# from sentra_brain_api.features.user.models import User

# # Sample mock user objects (replace as needed)
# class MockUser:
#     def __init__(self, id, username, email, full_name):
#         self.id = id
#         self.username = username
#         self.email = email
#         self.full_name = full_name

# mock_new_user = MockUser(2, "newuser", "newuser@example.com", "New User")
# mock_updated_user = MockUser(1, "updateduser", "updateduser@example.com", "Updated User")

# @pytest.fixture
# def mediator():
#     return MagicMock()

# @pytest.fixture
# def authenticated_user():
#     return User(
#         id=1,
#         username="testuser",
#         email="testuser@example.com",
#         full_name="Test User",
#         roles=["user"]
#     )

# @pytest.fixture
# def client(mediator, authenticated_user):
#     app = create_app(mediator=mediator)

#     app.dependency_overrides[get_authenticated_user] = lambda: authenticated_user
#     app.dependency_overrides[get_db] = lambda: MagicMock()  # Avoid real DB

#     with TestClient(app) as client:
#         yield client


# class TestUserController:

#     def test_create_user(self, client, mediator):
#         mediator.send_async.return_value = mock_new_user

#         response = client.post("/user/signup", json={
#             "username": "newuser",
#             "email": "newuser@example.com",
#             "full_name": "New User",
#             "password": "password123"
#         })

#         assert response.status_code == 200
#         data = response.json()["user"]
#         assert data["username"] == "newuser"
#         assert data["email"] == "newuser@example.com"
#         assert data["full_name"] == "New User"
#         mediator.send_async.assert_called_once()

#     def test_create_user_value_error(self, client, mediator):
#         mediator.send_async.side_effect = ValueError("Test error")

#         response = client.post("/user/signup", json={
#             "username": "newuser",
#             "email": "newuser@example.com",
#             "full_name": "New User",
#             "password": "password123"
#         })

#         assert response.status_code == 400
#         assert response.json() == {"detail": "Test error"}
#         mediator.send_async.assert_called_once()

#     def test_me(self, client):
#         response = client.get("/user/me")

#         assert response.status_code == 200
#         data = response.json()
#         assert data["username"] == "testuser"
#         assert data["email"] == "testuser@example.com"
#         assert data["full_name"] == "Test User"

#     def test_update_user(self, client, mediator):
#         mediator.send_async.return_value = mock_updated_user

#         response = client.put("/user/1", json={
#             "username": "updateduser",
#             "email": "updateduser@example.com",
#             "full_name": "Updated User"
#         })

#         assert response.status_code == 200
#         data = response.json()
#         assert data["username"] == mock_updated_user.username
#         assert data["email"] == mock_updated_user.email
#         assert data["full_name"] == mock_updated_user.full_name
#         mediator.send_async.assert_called_once()

#     def test_update_user_value_error(self, client, mediator):
#         mediator.send_async.side_effect = ValueError("Test error")

#         response = client.put("/user/1", json={
#             "username": "updateduser",
#             "email": "updateduser@example.com",
#             "full_name": "Updated User"
#         })

#         assert response.status_code == 400
#         assert response.json() == {"detail": "Test error"}
#         mediator.send_async.assert_called_once()
