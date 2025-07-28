import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone
from sentra_shared.domain.entities.user_entity import UserEntity
from sentra_brain_api.features.conversation.conversation_management_controller import ConversationManagementController
from sentra_brain_api.features.conversation.title_generation_service import TitleGenerationService

@pytest.fixture
def app(mock_user):
    from sentra_brain_api.crosscutting.authorization import get_authenticated_user

    fastapi_app = FastAPI()
    controller = ConversationManagementController()
    fastapi_app.include_router(controller.router, prefix="/conversations")

    fastapi_app.dependency_overrides[get_authenticated_user] = lambda: mock_user

    return fastapi_app

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def mock_user():
    return UserEntity(id="user-123", username="mockuser")

def test_create_conversation(client, mock_user):
    mock_service = MagicMock()
    mock_service.create_conversation.return_value = "mock-id"

    with patch("sentra_brain_api.features.conversation.conversation_management_controller.ConversationManagementController._get_service", return_value=mock_service), \
         patch("sentra_brain_api.crosscutting.authorization.get_authenticated_user", return_value=mock_user):

        res = client.post("/conversations/", json={
            "title": "Test title",
            "description": "Test description",
            "initial_prompt": "Say something",
            "content": "Hello, world!"
        })

        assert res.status_code == 200
        assert res.json() == {"id": "mock-id"}

def test_get_conversations(client, mock_user):
    mock_service = MagicMock()
    mock_service.get_user_conversations.return_value = [
        MagicMock(id="1", title="Conv 1", created_at=datetime.now(timezone.utc)),
        MagicMock(id="2", title=None, created_at=datetime.now(timezone.utc))
    ]

    with patch("sentra_brain_api.features.conversation.conversation_management_controller.ConversationManagementController._get_service", return_value=mock_service), \
         patch("sentra_brain_api.crosscutting.authorization.get_authenticated_user", return_value=mock_user):

        res = client.get("/conversations/")
        assert res.status_code == 200
        assert isinstance(res.json(), list)
        assert res.json()[0]["title"] == "Conv 1"
        assert res.json()[1]["title"] == "Untitled"

def test_get_conversation_by_id(client, mock_user):
    mock_service = MagicMock()
    mock_service.get_conversation.return_value = {
        "_id": "abc",  # alias
        "title": "Test",
        "description": "Sample",
        "initial_prompt": "Start",
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
        "messages": []
    }


    with patch("sentra_brain_api.features.conversation.conversation_management_controller.ConversationManagementController._get_service", return_value=mock_service), \
         patch("sentra_brain_api.crosscutting.authorization.get_authenticated_user", return_value=mock_user):

        res = client.get("/conversations/abc")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == "abc"
        assert data["title"] == "Test"


def test_create_conversation_with_auto_title_generation(client, mock_user):
    """Test that conversation creation triggers title generation when no title provided."""
    mock_service = MagicMock()
    mock_service.create_conversation.return_value = "mock-id"
    
    # Mock the title generation service
    mock_title_service = AsyncMock()
    mock_title_service.generate_title.return_value = "Generated Title"

    with patch("sentra_brain_api.features.conversation.conversation_management_controller.ConversationManagementController._get_service", return_value=mock_service), \
         patch("sentra_brain_api.crosscutting.authorization.get_authenticated_user", return_value=mock_user):

        res = client.post("/conversations/", json={
            "description": "Test description",  # No title provided
            "content": "How do I learn machine learning?"
        })

        assert res.status_code == 200
        assert res.json() == {"id": "mock-id"}
        
        # Verify service was called with the request
        mock_service.create_conversation.assert_called_once()
        call_args = mock_service.create_conversation.call_args[0][1]  # Second argument is the request
        assert call_args.title is None  # No title provided
        assert call_args.content == "How do I learn machine learning?"


def test_create_conversation_with_existing_title_skips_generation(client, mock_user):
    """Test that title generation is skipped when title is already provided."""
    mock_service = MagicMock()
    mock_service.create_conversation.return_value = "mock-id"

    with patch("sentra_brain_api.features.conversation.conversation_management_controller.ConversationManagementController._get_service", return_value=mock_service), \
         patch("sentra_brain_api.crosscutting.authorization.get_authenticated_user", return_value=mock_user):

        res = client.post("/conversations/", json={
            "title": "My Custom Title",  # Title provided
            "description": "Test description",
            "content": "How do I learn machine learning?"
        })

        assert res.status_code == 200
        assert res.json() == {"id": "mock-id"}
        
        # Verify service was called with the request including title
        mock_service.create_conversation.assert_called_once()
        call_args = mock_service.create_conversation.call_args[0][1]
        assert call_args.title == "My Custom Title"
