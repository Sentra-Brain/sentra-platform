"""Base class for all Sentra agents using Microsoft Agent Framework (MAF)."""

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from sentra.shared.settings import settings
from sentra.runtime.adapters.mongo_chat_message_store import MongoChatMessageStore
from sentra.runtime.adapters.rag_context_provider import RagContextProvider


class BaseAgent(ChatAgent):
    """Base ChatAgent that injects standard Sentra configuration and persistence."""

    def __init__(
        self,
        *,
        name: str,
        description: str,
        instructions: str,
        user_id: str,
        conversation_id: str,
        tools: list | None = None,
        top_k: int = 5,
    ):
        """Initialize an agent with preconfigured context and persistence."""
        self.chat_client = OpenAIChatClient(
            endpoint=settings.open_api_base,
            api_key=settings.open_api_key or "none",
            ai_model_id=settings.model_id,
        )

        self.store = MongoChatMessageStore(conversation_id, user_id)

        self.memory = RagContextProvider(
            chat_client=self.chat_client,
            user_id=user_id,
            top_k=top_k,
        )

        super().__init__(
            name=name,
            description=description,
            instructions=instructions,
            chat_client=self.chat_client,
            tools=tools or [],
            chat_message_store_factory=lambda: self.store,
            context_providers=[self.memory],
        )
