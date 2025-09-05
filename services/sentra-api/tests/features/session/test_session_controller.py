# import uuid
# import pytest
# from datetime import datetime, timezone
# from fastapi import FastAPI
# from fastapi.testclient import TestClient
# from unittest.mock import AsyncMock, Mock
# from sentra.domain.entities.user_entity import UserEntity
# from sentra_brain_api.crosscutting.authorization import get_authenticated_user
# from sentra_brain_api.features.session.controller import SessionController
# from sentra_brain_api.features.session.schemas import (
#     UpdateSessionRequest,
#     SessionResponse,
#     SessionListItemResponse,
#     DeleteSessionResponse,
#     CreateSessionResponse
# )

# @pytest.fixture
# def mock_user():
#     return UserEntity(id=uuid.uuid4(), username="mockuser")

# @pytest.fixture
# def mock_service():
#     service = Mock()

#     # Async return for create_session
#     service.create_session = AsyncMock(return_value=CreateSessionResponse(id=str(uuid.uuid4())))

#     # Sync method: list_user_sessions → must return schema-compatible
#     service.list_user_sessions.return_value = [
#         SessionListItemResponse(
#             id=str(uuid.uuid4()),
#             title="Conversation 1",
#             created_at=datetime.now(timezone.utc)
#         ),
#         SessionListItemResponse(
#             id=str(uuid.uuid4()),
#             title="Untitled",
#             created_at=datetime.now(timezone.utc)
#         )
#     ]

#     # Sync method: get_session → must return SessionResponse
#     service.get_session.return_value = SessionResponse(
#         title="Test Conversation",
#         description="Test Desc",
#         initial_prompt=None,
#         created_at=datetime.now(timezone.utc),
#         updated_at=None,
#         messages=[],
#         id="abc"  # BaseMongoModel includes `id`
#     )

#     # Sync method: update_session → must return schema-compatible
#     service.update_session.return_value = {
#         "session_id": "abc",
#         "title": "Updated Title",
#         "description": "Updated Desc"
#     }

#     # Sync method: delete_session → must return success response
#     service.delete_session.return_value = DeleteSessionResponse(
#         success=True,
#         message="Conversation deleted successfully"
#     )

#     return service

# @pytest.fixture
# def client(mock_user, mock_service):
#     app = FastAPI()
#     controller = SessionController()
#     app.include_router(controller.router, prefix="/sessions")

#     # Patch DI
#     app.dependency_overrides[get_authenticated_user] = lambda: mock_user
#     app.dependency_overrides[controller._get_service] = lambda: mock_service

#     return TestClient(app)


# def test_create_session(client, mock_service):
#     response = client.post("/sessions/", json={
#         "title": "Test Title",
#         "description": "Something",
#         "initial_prompt": "Start here",
#         "content": "Hello"
#     })
#     assert response.status_code == 200
#     body = response.json()
#     assert "id" in body
#     mock_service.create_session.assert_called_once()


# def test_get_sessions(client, mock_service):
#     response = client.get("/sessions/")
#     assert response.status_code == 200
#     data = response.json()
#     assert isinstance(data, list)
#     assert len(data) == 2
#     assert data[0]["title"] == "Session 1"
#     assert data[1]["title"] == "Untitled"


# def test_get_session_by_id(client, mock_service):
#     response = client.get("/sessions/abc")
#     assert response.status_code == 200
#     body = response.json()
#     assert body["id"] == "abc"
#     assert body["title"] == "Test Conversation"
#     mock_service.get_session.assert_called_once()


# def test_update_session(client, mock_service):
#     payload = {
#         "title": "Updated Title",
#         "description": "Updated Desc"
#     }
#     response = client.put("/sessions/abc", json=payload)
#     assert response.status_code == 200
#     body = response.json()
#     assert body["session_id"] == "abc"
#     assert body["title"] == "Updated Title"
#     assert body["description"] == "Updated Desc"
#     mock_service.update_session.assert_called_once()


# def test_delete_session(client, mock_service):
#     response = client.delete("/sessions/abc")
#     assert response.status_code == 200
#     body = response.json()
#     assert body["success"] is True
#     assert "deleted" in body["message"].lower()
#     mock_service.delete_session.assert_called_once()
