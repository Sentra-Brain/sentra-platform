# sentra_brain_api/features/conversation/title_generation_service.py

import re
from typing import Optional
from sentra_shared.core.logging import get_logger
from sentra_brain_api.features.llm_proxy.adapter import VLLMServerClient
from sentra_brain_api.features.llm_proxy.models import ChatCompletionRequest, ChatMessage

logger = get_logger("title_generation_service")


class TitleGenerationService:
    """Service for generating conversation titles from user messages using LLM."""

    def __init__(self, vllm_client: Optional[VLLMServerClient] = None):
        self.vllm_client = vllm_client or VLLMServerClient()

    async def generate_title(self, user_message: str) -> Optional[str]:
        """
        Generate a conversation title from the first user message.
        
        Args:
            user_message: The first user message content
            
        Returns:
            Generated title or None if generation fails
        """
        if not user_message or not user_message.strip():
            logger.warning("Cannot generate title for empty or whitespace-only message")
            return None
        
        try:
            # Try LLM generation first
            llm_title = await self._generate_title_with_llm(user_message)
            if llm_title and llm_title.strip():
                return self._clean_title(llm_title)
        except Exception as e:
            logger.warning(f"LLM title generation failed: {e}")
        
        # Fallback to heuristic approach
        return self._generate_title_heuristic(user_message)
    
    async def _generate_title_with_llm(self, user_message: str) -> Optional[str]:
        """Generate title using LLM."""
        
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
            model="sentra-brain",
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt)
            ],
            max_tokens=20,
            temperature=0.3,
            stream=False
        )
        
        try:
            response = await self.vllm_client.complete_chat(request)
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content:
                    return content.strip()
        except Exception as e:
            logger.error(f"Error calling LLM for title generation: {e}")
            raise
        
        return None
    
    def _generate_title_heuristic(self, user_message: str) -> str:
        """Generate title using heuristic approach as fallback."""
        
        # Clean up the message
        cleaned = user_message.strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            "help me", "help me with", "can you help me", "i need help with",
            "how do i", "how can i", "how to", "what is", "what are", "tell me about"
        ]
        
        cleaned_lower = cleaned.lower()
        for prefix in prefixes_to_remove:
            if cleaned_lower.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                break
        
        # Split into words and take first 6-8 words
        words = cleaned.split()
        title_words = words[:8] if len(words) > 6 else words[:6]
        
        if not title_words:
            return "New Conversation"
        
        # Join and capitalize
        title = " ".join(title_words)
        
        # Add question mark if original message was a question
        if user_message.strip().endswith("?") and not title.endswith("?"):
            title += "?"
        
        return self._clean_title(title)
    
    def _clean_title(self, title: str) -> str:
        """Clean and format the title."""
        if not title:
            return "New Conversation"
        
        # Remove quotes and extra whitespace
        title = re.sub(r'^["\'`]+|["\'`]+$', '', title.strip())
        
        # Limit length
        if len(title) > 50:
            title = title[:47] + "..."
        
        # Ensure it's not empty after cleaning
        if not title.strip():
            return "New Conversation"
        
        return title.strip()