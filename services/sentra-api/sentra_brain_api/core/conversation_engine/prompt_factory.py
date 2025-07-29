from typing import Optional
from sentra_brain_api.core.constants import CONTEXT_WINDOW_SIZE

class PromptFactory:
    def __init__(self, system_prompt: Optional[str] = None):
        self.default_system_prompt = system_prompt or (
            "You are Sentra, a private AI assistant deployed securely in a business environment. "
            "Be helpful, accurate, and concise. Maintain user privacy. Avoid speculation."
        )

    def build_payload(
        self,
        context: list[dict],
        new_message: dict,
        *,
        temperature: float = 0.7,
        top_p: float = 0.95,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        max_tokens: int = 1024,
    ) -> dict:
        """
        Constructs the final payload for the LLM server, including:
        - system prompt
        - initial user intent (if present)
        - trimmed conversation window
        - the new message
        - generation config
        """
        messages = []

        # 1. System prompt
        messages.append({
            "role": "system",
            "content": self.default_system_prompt
        })

        # 2. Highlight initial user intent
        if context:
            first_user = next((m for m in context if m["role"] == "user"), None)
            if first_user:
                messages.append({
                    "role": "user",
                    "content": f"(initial intent) {first_user['content']}"
                })

        # 3. Context window
        trimmed = context[-CONTEXT_WINDOW_SIZE:]
        messages.extend(trimmed)

        # 4. Current input
        messages.append(new_message)

        # 5. Final payload
        return {
            "messages": messages,
            "stream": True,  # Always stream for OpenAI-compatible LLMs
            "temperature": temperature,
            "top_p": top_p,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "max_tokens": max_tokens
        }
