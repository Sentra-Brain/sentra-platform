import re
from typing import Optional
from sentra_core.core.logging import get_logger
from sentra_engine.adapters.llm_adapter_factory import LlmAdapterFactory
from sentra_brain_api.features.llm_proxy.models import ChatCompletionRequest, ChatMessage
from sentra_engine.core.models import PromptContext

logger = get_logger("title_generation_service")


class TitleGenerationService:
    """Service for generating conversation titles."""

    def __init__(self):
        pass

    def generate_initial_title(self, initial_prompt: str) -> str:
        """
        Heuristic fallback title generator used immediately when creating a conversation.

        Args:
            initial_prompt: First user message content
        Returns:
            A cleaned, short title
        """
        if not initial_prompt or not initial_prompt.strip():
            return "New Conversation"

        logger.debug(f"Generating initial heuristic title for: {initial_prompt[:100]}")
        return self._generate_title_heuristic(initial_prompt)

    async def generate_llm_title(self, user_message: str) -> Optional[str]:
        """
        Generate refined LLM-based title asynchronously.
        Should be used after conversation has started.

        Args:
            user_message: First user message content
        Returns:
            Cleaned LLM title, or None if LLM fails
        """
        if not user_message or not user_message.strip():
            logger.warning("Empty message received for LLM title generation")
            return None

        try:
            logger.debug("Calling LLM to generate title")
            llm_title = await self._generate_title_with_llm(user_message)
            return self._clean_title(llm_title)
        except Exception as e:
            logger.warning(f"LLM title generation failed: {e}")
            return None

    def _convert_to_prompt_context(self, request: ChatCompletionRequest) -> PromptContext:
        return PromptContext(messages=request.messages)

    async def _generate_title_with_llm(self, user_message: str) -> Optional[str]:
        system_prompt = """Suggest a short, human-readable title for the following message. Be concise and properly capitalized.

        Guidelines:
        - Keep title under 6 words
        - Capitalize it properly (title case)
        - Avoid punctuation unless it's a question mark
        - Make it descriptive but brief

        Examples:
        "How do I register a patent in Europe?" → "Registering a Patent in Europe"
        "What's the weather like today?" → "Weather Today?"
        "Help me write a business plan" → "Business Plan Writing Help"
        "I need to fix my computer" → "Computer Repair Help"

        Just return the title, nothing else."""

        user_prompt = f"Message: {user_message}"

        request = ChatCompletionRequest(
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ],
            model="gpt-4",
            max_tokens=20,
            temperature=0.3,
            top_p=1.0,
            stream=False,
        )

        if not request.model:
            raise ValueError("Model is required for LLM title generation")

        llm_adapter = LlmAdapterFactory.create_adapter(request.model)
        prompt_context = self._convert_to_prompt_context(request)

        chunks = []
        async for chunk in llm_adapter.chat_stream(prompt_context):
            for choice in chunk.choices:
                if choice.message and choice.message.content:
                    chunks.append(choice.message.content)

        if chunks:
            return "".join(chunks).strip()

        return None

    def _generate_title_heuristic(self, user_message: str) -> str:
        cleaned = user_message.strip()

        prefixes_to_remove = [
            "help me", "help me with", "can you help me", "i need help with",
            "how do i", "how can i", "how to", "what is", "what are", "tell me about",
        ]

        cleaned_lower = cleaned.lower()
        for prefix in prefixes_to_remove:
            if cleaned_lower.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                break

        words = cleaned.split()
        title_words = words[:6] if len(words) > 4 else words[:4]

        if not title_words:
            return "New Conversation"

        title = " ".join(title_words)

        if user_message.strip().endswith("?") and not title.endswith("?"):
            title += "?"

        return self._clean_title(title)

    def _clean_title(self, title: Optional[str]) -> str:
        if not title:
            return "New Conversation"

        title = re.sub(r'^\"|\"$|^\'|\'$|^`|`$', '', title.strip())
        if len(title) > 50:
            title = title[:47] + "..."

        return title.strip() or "New Conversation"
