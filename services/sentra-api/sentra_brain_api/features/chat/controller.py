# services/sentra-api/sentra_brain_api/features/chat/controller.py

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_brain_api.features.chat.schemas import ChatSendRequest
from sentra.domain.entities.user_entity import UserEntity
from sentra.runtime.agents.sentra_agent import build_sentra_agent
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

            # Instantiate our SentraAgent (BaseAgent subclass)
            agent = build_sentra_agent(user_id=user_id, conversation_id=conversation_id)
            thread = agent.get_new_thread()

            async def stream():
                try:
                    # Run and stream updates directly from MAF
                    response = await agent.run(body.content, thread=thread, stream=True)
                    async for update in response:
                        payload = jsonable_encoder(update)
                        yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

                    # Indicate end of stream
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
