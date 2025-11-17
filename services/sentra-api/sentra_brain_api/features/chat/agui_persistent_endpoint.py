from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from ag_ui.encoder import EventEncoder
from agent_framework_ag_ui._agent import AgentFrameworkAgent

from sentra.runtime.agents.registry import agent_registry
from sentra.runtime.adapters.hybrid_chat_message_store import ChatMessageStoreHybrid


def register_persistent_agui(app: FastAPI, path="/chat/agui") -> None:
    """
    AG-UI endpoint with full Sentra-style persistence.
    """
    template = agent_registry.get("sentra")

    @app.post(path)
    async def agui_entry(request: Request):

        payload = await request.json()

        thread_id = payload["thread_id"]
        user_id = payload.get("user_id", "agui-user")
        conversation_id = thread_id

        # Build persistent agent with correct keys
        agent = template.build(
            user_id=user_id,
            conversation_id=conversation_id,
            persist=True,
        )
        wrapped = AgentFrameworkAgent(agent)

        async def stream():
            encoder = EventEncoder()
            async for update in wrapped.run_agent(payload):
                yield encoder.encode(update)

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
