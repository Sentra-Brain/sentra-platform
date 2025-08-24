# tests/features/openai_proxy/test_controller.py

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sentra_brain_api.main import create_app
from sentra_brain_api.features.llm_proxy.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    ChatCompletionChoice,
    ChatCompletionUsage,
    ChatCompletionChunk
)
from sentra_engine.llm.adapters.factory import LlmAdapterFactory


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_llm_adapter():
    mock_adapter = AsyncMock()
    mock_adapter.chat_stream = AsyncMock()
    return mock_adapter


@pytest.fixture 
def sample_request():
    return {
        "model": "llama-3",
        "messages": [
            {"role": "user", "content": "Qué es Sentra Brain?"}
        ],
        "stream": False
    }


@pytest.fixture
def sample_response():
    class MockDeltaEvent:
        def __init__(self, type, content):
            self.type = type
            self.content = content

    return MockDeltaEvent(
        type="message_delta",
        content="Sentra Brain es una plataforma de IA."
    )


class TestOpenAIProxyController:
    def test_chat_completions_non_streaming(self, client, sample_request, sample_response, mock_llm_adapter):
        # Setup mock
        async def mock_chat_stream(prompt_context):
            yield sample_response

        mock_llm_adapter.chat_stream = mock_chat_stream

        # Patch the factory
        with patch.object(LlmAdapterFactory, 'create_adapter', return_value=mock_llm_adapter):
            # Make request
            response = client.post("/v1/chat/completions", json=sample_request)

            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["model"] == "llama-3"
            assert data["choices"][0]["message"]["role"] == "assistant"
            assert "Sentra Brain" in data["choices"][0]["message"]["content"]

    def test_chat_completions_with_streaming(self, client, sample_request, sample_response, mock_llm_adapter):
        # Setup mock for streaming
        async def mock_stream(prompt_context):
            yield sample_response

        mock_llm_adapter.chat_stream = mock_stream

        # Patch the factory
        with patch.object(LlmAdapterFactory, 'create_adapter', return_value=mock_llm_adapter):
            # Set streaming to true
            sample_request["stream"] = True

            # Make request
            response = client.post("/v1/chat/completions", json=sample_request)

            # For streaming, we expect a 200 response with text/plain content type
            assert response.status_code == 200
            assert "text/plain" in response.headers.get("content-type", "")
    
    def test_chat_completions_invalid_request(self, client):
        # Test with invalid request (missing required fields)
        invalid_request = {
            "model": "llama-3"
            # Missing messages field
        }
        
        response = client.post("/v1/chat/completions", json=invalid_request)
        assert response.status_code == 422  # Validation error
    
    def test_chat_completions_empty_messages(self, client):
        # Test with empty messages array
        empty_messages_request = {
            "model": "llama-3",
            "messages": []
        }
        
        response = client.post("/v1/chat/completions", json=empty_messages_request)
        assert response.status_code == 422  # Should fail validation


def test_chat_message_validation():
    """Test that ChatMessage model validates correctly"""
    # Valid message
    valid_message = ChatMessage(role="user", content="Hello")
    assert valid_message.role == "user"
    assert valid_message.content == "Hello"

    # Test invalid role
    with pytest.raises(ValueError):
        ChatMessage(role="invalid_role", content="Hello")  # Dynamically bypass type checking


def test_chat_completion_request_validation():
    """Test that ChatCompletionRequest model validates correctly"""
    # Valid request
    valid_request = ChatCompletionRequest(
        model="llama-3",
        messages=[ChatMessage(role="user", content="Hello")],
        stream=False,
        temperature=1.0,
        max_tokens=100,
        top_p=1.0
    )
    assert valid_request.model == "llama-3"
    assert len(valid_request.messages) == 1
    assert valid_request.stream is False  # Default value

    # Test with optional parameters
    request_with_options = ChatCompletionRequest(
        model="llama-3",
        messages=[ChatMessage(role="user", content="Hello")],
        stream=True,
        temperature=0.7,
        max_tokens=100,
        top_p=0.9
    )
    assert request_with_options.stream is True
    assert request_with_options.temperature == 0.7
    assert request_with_options.max_tokens == 100
    assert request_with_options.top_p == 0.9