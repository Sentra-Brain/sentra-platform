
from sentra.runtime.adapters.hybrid_chat_message_store import ChatMessageStoreHybrid
from sentra.runtime.agents.registry import agent_registry

class ChatApiService:
    def __init__(self):
        self.registry = agent_registry

    async def send_message_stream(self, user_id: str, conversation_id: str, message: str):
        template = self.registry.get("sentra")
        agent = template.build(user_id=user_id, conversation_id=conversation_id)

        # Restore previous thread if available
        store = ChatMessageStoreHybrid(conversation_id, user_id)
        serialized = await store.load_thread_state()
        thread = None
        if serialized:
            thread = await agent.deserialize_thread(serialized)

        async for update in agent.run_stream(message, thread=thread):
            yield update

        # Persist thread state after completion
        if thread:
            serialized_state = await thread.serialize()
            await store.save_thread_state(serialized_state)