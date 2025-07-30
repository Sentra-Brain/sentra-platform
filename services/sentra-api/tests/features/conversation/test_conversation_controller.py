import uuid
import pytest
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock
from sentra_shared.domain.entities.user_entity import UserEntity
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_brain_api.features.conversation.controller import ConversationController
from sentra_brain_api.features.conversation.schemas import (
    UpdateConversationRequest,
    ConversationResponse,
    ConversationListItemResponse,
    DeleteConversationResponse,
    CreateConversationResponse
)

@pytest.fixture
def mock_user():
    return UserEntity(id=uuid.uuid4(), username="mockuser")

@pytest.fixture
def mock_service():
    service = Mock()

    # Async return for create_conversation
    service.create_conversation = AsyncMock(return_value=CreateConversationResponse(id=str(uuid.uuid4())))

    # Sync method: list_user_conversations → must return schema-compatible
    service.list_user_conversations.return_value = [
        ConversationListItemResponse(
            id=str(uuid.uuid4()),
            title="Conversation 1",
            created_at=datetime.now(timezone.utc)
        ),
        ConversationListItemResponse(
            id=str(uuid.uuid4()),
            title="Untitled",
            created_at=datetime.now(timezone.utc)
        )
    ]

    # Sync method: get_conversation → must return ConversationResponse
    service.get_conversation.return_value = ConversationResponse(
        title="Test Conversation",
        description="Test Desc",
        initial_prompt=None,
        created_at=datetime.now(timezone.utc),
        updated_at=None,
        messages=[],
        id="abc"  # BaseMongoModel includes `id`
    )

    # Sync method: update_conversation → must return schema-compatible
    service.update_conversation.return_value = {
        "conversation_id": "abc",
        "title": "Updated Title",
        "description": "Updated Desc"
    }

    # Sync method: delete_conversation → must return success response
    service.delete_conversation.return_value = DeleteConversationResponse(
        success=True,
        message="Conversation deleted successfully"
    )

    return service

@pytest.fixture
def client(mock_user, mock_service):
    app = FastAPI()
    controller = ConversationController()
    app.include_router(controller.router, prefix="/conversations")

    # Patch DI
    app.dependency_overrides[get_authenticated_user] = lambda: mock_user
    app.dependency_overrides[controller._get_service] = lambda: mock_service

    return TestClient(app)


def test_create_conversation(client, mock_service):
    response = client.post("/conversations/", json={
        "title": "Test Title",
        "description": "Something",
        "initial_prompt": "Start here",
        "content": "Hello"
    })
    assert response.status_code == 200
    body = response.json()
    assert "id" in body
    mock_service.create_conversation.assert_called_once()


def test_get_conversations(client, mock_service):
    response = client.get("/conversations/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["title"] == "Conversation 1"
    assert data[1]["title"] == "Untitled"


def test_get_conversation_by_id(client, mock_service):
    response = client.get("/conversations/abc")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "abc"
    assert body["title"] == "Test Conversation"
    mock_service.get_conversation.assert_called_once()


def test_update_conversation(client, mock_service):
    payload = {
        "title": "Updated Title",
        "description": "Updated Desc"
    }
    response = client.put("/conversations/abc", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["conversation_id"] == "abc"
    assert body["title"] == "Updated Title"
    assert body["description"] == "Updated Desc"
    mock_service.update_conversation.assert_called_once()


def test_delete_conversation(client, mock_service):
    response = client.delete("/conversations/abc")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "deleted" in body["message"].lower()
    mock_service.delete_conversation.assert_called_once()
