# services/sentra-api/sentra_brain_api/features/chat/controller.py

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_brain_api.features.chat.schemas import ChatSendRequest
from sentra.domain.entities.user_entity import UserEntity
from sentra.runtime.agents.registry import agent_registry
from sentra.shared.logging import get_logger
import json

logger = get_logger("sentra_brain_api.features.chat")
class ChatController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self):
        @self.router.post(
            "/send",
            response_class=StreamingResponse,
            description="Send a message via SentraAgent (MAF PoC)",
        )
        async def send_message(
            body: ChatSendRequest,
            request: Request,
            current_user: UserEntity = Depends(get_authenticated_user),
        ):
            user_id = str(current_user.id)
            conversation_id = str(body.session_id)

            # Build agent bound to this user+conversation
            template = agent_registry.get("sentra")
            agent = template.build(user_id=user_id, conversation_id=conversation_id)

            async def stream():
                try:
                    async for update in agent.run_stream(body.content):
                        payload = jsonable_encoder(update)
                        yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                        
                    yield f"data: {json.dumps({'session_id': conversation_id, 'status': 'complete'})}\n\n"

                except Exception as e:
                    logger.exception("Agent run failed")
                    err_payload = {"session_id": conversation_id, "error": str(e)}
                    yield f"data: {json.dumps(err_payload, ensure_ascii=False)}\n\n"

            return StreamingResponse(
                stream(),
                media_type="text/event-stream; charset=utf-8",
                headers={
                    "Cache-Control": "no-cache, no-transform",
                    "X-Accel-Buffering": "no",
                    "Connection": "keep-alive",
                },
            )