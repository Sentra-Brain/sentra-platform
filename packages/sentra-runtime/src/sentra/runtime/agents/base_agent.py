# packages/sentra-runtime/src/sentra/runtime/agents/base_agent.py
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from sentra.runtime.adapters.hybrid_chat_message_store import ChatMessageStoreHybrid
from sentra.runtime.adapters.rag_context_provider import RagContextProvider
from sentra.shared.settings import settings

class BaseAgent(ChatAgent):
    """Base ChatAgent that injects Sentra config and persistence (Mongo + RAG)."""

    def __init__(
        self,
        *,
        name: str,
        description: str,
        instructions: str,
        user_id: str,
        conversation_id: str,
        model_id: str | None = None,
        tools: list | None = None,
        top_k: int = 5,
        persist: bool = True,        
    ):
        client = OpenAIChatClient(
            base_url=settings.openai_api_base,
            api_key=settings.openai_api_key or "none",
            model_id=model_id or settings.model_id,
        )

        store_factory = (
            (lambda: ChatMessageStoreHybrid(conversation_id, user_id))
            if persist and user_id and conversation_id
            else None
        )
        memory = RagContextProvider(chat_client=client, user_id=user_id or "", top_k=top_k)
        
        super().__init__(
            name=name,
            description=description,
            instructions=instructions,
            chat_client=client,
            tools=tools or [],
            chat_message_store_factory=store_factory,
            context_providers=[memory],
            model_id=model_id or settings.model_id,
        )
