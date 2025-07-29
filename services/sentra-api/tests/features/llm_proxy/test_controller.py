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
    ChatCompletionUsage
)
from sentra_brain_api.features.llm_proxy.controller import get_vllm_client


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_vllm_client():
    mock_client = AsyncMock()
    mock_client.close = AsyncMock()
    return mock_client


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
    return ChatCompletionResponse(
        id="chatcmpl-test123",
        created=1234567890,
        model="llama-3",
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatMessage(role="assistant", content="Sentra Brain es una plataforma de IA."),
                finish_reason="stop"
            )
        ],
        usage=ChatCompletionUsage(
            prompt_tokens=10,
            completion_tokens=15,
            total_tokens=25
        )
    )


class TestOpenAIProxyController:
    
    def test_chat_completions_non_streaming(self, client, sample_request, sample_response, mock_vllm_client):
        # Setup mock
        mock_vllm_client.complete_chat.return_value = sample_response
        
        # Override the dependency 
        app = client.app
        app.dependency_overrides[get_vllm_client] = lambda: mock_vllm_client
        
        try:
            # Make request
            response = client.post("/v1/chat/completions", json=sample_request)
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["model"] == "llama-3"
            assert data["choices"][0]["message"]["role"] == "assistant"
            assert "Sentra Brain" in data["choices"][0]["message"]["content"]
        finally:
            # Clean up override
            app.dependency_overrides.clear()
    
    def test_chat_completions_with_streaming(self, client, sample_request, mock_vllm_client):
        # Setup mock for streaming
        async def mock_stream():
            yield sample_response  # This would be chunks in real implementation
        mock_vllm_client.stream_chat.return_value = mock_stream()
        
        # Override the dependency 
        app = client.app
        app.dependency_overrides[get_vllm_client] = lambda: mock_vllm_client
        
        try:
            # Set streaming to true
            sample_request["stream"] = True
            
            # Make request
            response = client.post("/v1/chat/completions", json=sample_request)
            
            # For streaming, we expect a 200 response with text/plain content type
            assert response.status_code == 200
            assert "text/plain" in response.headers.get("content-type", "")
        finally:
            # Clean up override
            app.dependency_overrides.clear()
    
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
        ChatMessage(role="invalid_role", content="Hello")


def test_chat_completion_request_validation():
    """Test that ChatCompletionRequest model validates correctly"""
    # Valid request
    valid_request = ChatCompletionRequest(
        model="llama-3",
        messages=[ChatMessage(role="user", content="Hello")]
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
        max_tokens=100
    )
    assert request_with_options.stream is True
    assert request_with_options.temperature == 0.7
    assert request_with_options.max_tokens == 100