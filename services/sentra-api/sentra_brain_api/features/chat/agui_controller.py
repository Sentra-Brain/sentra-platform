from agent_framework import AgentThread
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from ag_ui.encoder import EventEncoder
from sentra_brain_api.features.chat.persisted_agent import PersistedAgent

from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra.runtime.agents.registry import agent_registry
from sentra.runtime.adapters.hybrid_chat_message_store import ChatMessageStoreHybrid
from sentra.domain.entities.user_entity import UserEntity
from sentra.shared.logging import get_logger
import json


logger = get_logger("sentra_brain_api.features.chat.agui")


class AGUIChatController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self):

        @self.router.post(
            "/chat/agui",
            response_class=StreamingResponse,
            description="AG-UI compliant streaming endpoint with full Sentra persistence and authentication",
        )
        async def run_agent(
            request: Request,
            current_user: UserEntity = Depends(get_authenticated_user),
        ):
            """
            AG-UI RunAgentInput → persistent SentraAgent → AG-UI SSE output.
            """

            payload = await request.json()

            # Required by AG-UI protocol
            thread_id = payload["threadId"]

            # Your real persistence keys
            user_id = str(current_user.id)
            conversation_id = thread_id

            # Build a persistent agent instance
            template = agent_registry.get("sentra")
            agent = template.build(
                user_id=user_id,
                conversation_id=conversation_id,
                persist=True,
            )

            wrapped = PersistedAgent(agent)

            async def stream():
                encoder = EventEncoder()
                async for update in wrapped.run_agent(payload):
                    encoded = encoder.encode(update)
                    yield encoded

            return StreamingResponse(
                stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache, no-transform",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )
