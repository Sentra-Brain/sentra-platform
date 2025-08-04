import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from sentra_brain_api.features.conversation.title.title_generation_service import TitleGenerationService
from sentra_brain_api.features.llm_proxy.models import (
    ChatCompletionResponse, 
    ChatCompletionChoice, 
    ChatMessage, 
    ChatCompletionUsage
)


class TestTitleGenerationService:
    """Test cases for TitleGenerationService."""

    @pytest.fixture
    def mock_vllm_client(self):
        """Mock VLLMServerClient for testing."""
        client = AsyncMock()
        return client

    @pytest.fixture
    def title_service(self, mock_vllm_client):
        """TitleGenerationService instance with mocked LLM client."""
        return TitleGenerationService(vllm_client=mock_vllm_client)

    @pytest.mark.asyncio
    async def test_generate_title_with_llm_success(self, title_service, mock_vllm_client):
        """Test successful title generation using LLM."""
        # Mock LLM response
        mock_response = ChatCompletionResponse(
            id="test-id",
            object="chat.completion",
            created=1234567890,
            model="sentra-brain",
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content="Patent Registration Europe"),
                    finish_reason="stop"
                )
            ],
            usage=ChatCompletionUsage(
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15
            )
        )
        mock_vllm_client.complete_chat.return_value = mock_response

        result = await title_service.generate_llm_title("How do I register a patent in Europe?")
        
        assert result == "Patent Registration Europe"
        mock_vllm_client.complete_chat.assert_called_once()

    # @pytest.mark.asyncio
    # async def test_generate_title_llm_failure_uses_heuristic(self, title_service, mock_vllm_client):
    #     """Test that heuristic is used when LLM fails."""
    #     # Mock LLM to raise an exception
    #     mock_vllm_client.complete_chat.side_effect = Exception("LLM unavailable")

    #     result = await title_service.generate_llm_title("How do I register a patent in Europe?")
        
    #     # Should fall back to heuristic
    #     assert result is not None
    #     assert len(result) > 0
    #     mock_vllm_client.complete_chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_title_empty_message_returns_none(self, title_service):
        """Test that empty messages return None."""
        assert await title_service.generate_llm_title("") is None
        assert await title_service.generate_llm_title("   ") is None
        assert await title_service.generate_llm_title(None) is None

    # @pytest.mark.asyncio
    # async def test_generate_title_llm_empty_response_uses_heuristic(self, title_service, mock_vllm_client):
    #     """Test that heuristic is used when LLM returns empty response."""
    #     mock_response = ChatCompletionResponse(
    #         id="test-id",
    #         object="chat.completion",
    #         created=1234567890,
    #         model="sentra-brain",
    #         choices=[
    #             ChatCompletionChoice(
    #                 index=0,
    #                 message=ChatMessage(role="assistant", content=""),
    #                 finish_reason="stop"
    #             )
    #         ],
    #         usage=ChatCompletionUsage(
    #             prompt_tokens=10,
    #             completion_tokens=0,
    #             total_tokens=10
    #         )
    #     )
    #     mock_vllm_client.complete_chat.return_value = mock_response

    #     result = await title_service.generate_llm_title("How do I fix my computer?")
        
    #     # Should fall back to heuristic
    #     assert result is not None
    #     assert "fix" in result.lower() or "computer" in result.lower()

    def test_generate_title_heuristic_basic(self, title_service):
        """Test basic heuristic title generation."""
        result = title_service._generate_title_heuristic("How do I register a patent in Europe?")
        assert result == "register a patent in Europe?"
        
        result = title_service._generate_title_heuristic("Help me write a business plan")
        assert result == "write a business plan"
        
        result = title_service._generate_title_heuristic("What is machine learning?")
        assert result == "machine learning?"

    def test_generate_title_heuristic_long_message(self, title_service):
        """Test heuristic with very long messages."""
        long_message = "I need help with creating a comprehensive business plan that includes market research, financial projections, competitive analysis, and marketing strategies for my new startup company"
        result = title_service._generate_title_heuristic(long_message)
        
        # Should be truncated to reasonable length
        assert len(result.split()) <= 8
        assert "creating a comprehensive business plan" in result

    def test_generate_title_heuristic_empty_after_cleanup(self, title_service):
        """Test heuristic when message becomes empty after cleanup."""
        result = title_service._generate_title_heuristic("help me")
        assert result == "New Conversation"
        
        result = title_service._generate_title_heuristic("how do i")
        assert result == "New Conversation"

    def test_clean_title_removes_quotes(self, title_service):
        """Test that title cleaning removes quotes."""
        assert title_service._clean_title('"Machine Learning Basics"') == "Machine Learning Basics"
        assert title_service._clean_title("'Python Programming'") == "Python Programming"
        assert title_service._clean_title("`Code Review Tips`") == "Code Review Tips"

    def test_clean_title_length_limit(self, title_service):
        """Test that long titles are truncated."""
        long_title = "This is a very long title that exceeds the maximum length limit and should be truncated"
        result = title_service._clean_title(long_title)
        assert len(result) <= 50
        assert result.endswith("...")

    def test_clean_title_empty_returns_default(self, title_service):
        """Test that empty titles return default."""
        assert title_service._clean_title("") == "New Conversation"
        assert title_service._clean_title("   ") == "New Conversation"
        assert title_service._clean_title('""') == "New Conversation"

    # @pytest.mark.asyncio
    # async def test_generate_title_with_llm_request_format(self, title_service, mock_vllm_client):
    #     """Test that LLM request is properly formatted."""
    #     mock_response = ChatCompletionResponse(
    #         id="test-id",
    #         object="chat.completion", 
    #         created=1234567890,
    #         model="sentra-brain",
    #         choices=[
    #             ChatCompletionChoice(
    #                 index=0,
    #                 message=ChatMessage(role="assistant", content="Test Title"),
    #                 finish_reason="stop"
    #             )
    #         ],
    #         usage=ChatCompletionUsage(
    #             prompt_tokens=15,
    #             completion_tokens=2,
    #             total_tokens=17
    #         )
    #     )
    #     mock_vllm_client.complete_chat.return_value = mock_response

    #     await title_service.generate_title("Test message")
        
    #     # Verify the request was made with correct parameters
    #     call_args = mock_vllm_client.complete_chat.call_args[0][0]
    #     assert call_args.model == "sentra-brain"
    #     assert call_args.max_tokens == 20
    #     assert call_args.temperature == 0.3
    #     assert call_args.stream is False
    #     assert len(call_args.messages) == 2
    #     assert call_args.messages[0].role == "system"
    #     assert call_args.messages[1].role == "user"
    #     assert "Test message" in call_args.messages[1].content

    def test_generate_title_heuristic_preserves_questions(self, title_service):
        """Test that question marks are preserved in heuristic titles."""
        result = title_service._generate_title_heuristic("What is the weather today?")
        assert result.endswith("?")
        
        result = title_service._generate_title_heuristic("Tell me about Python")
        assert not result.endswith("?")

    def test_generate_title_heuristic_removes_common_prefixes(self, title_service):
        """Test that common prefixes are removed in heuristic generation."""
        test_cases = [
            ("help me with machine learning", "machine learning"),
            ("can you help me understand AI", "understand ai"),  # Fixed case
            ("i need help with coding", "coding"),
            ("how do i install Python", "install python"),  # Fixed case
            ("how can i learn programming", "learn programming"),
            ("what is machine learning", "machine learning"),
            ("tell me about data science", "data science")
        ]
        
        for input_msg, expected_content in test_cases:
            result = title_service._generate_title_heuristic(input_msg)
            assert expected_content in result.lower()