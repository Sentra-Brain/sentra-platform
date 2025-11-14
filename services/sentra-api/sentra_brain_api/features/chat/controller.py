# services/sentra-api/sentra_brain_api/features/chat/controller.py
from fastapi import APIRouter, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_brain_api.features.chat.api_service import ChatApiService
from sentra_brain_api.features.chat.schemas import ChatSendRequest
from sentra.domain.entities.user_entity import UserEntity
from sentra.shared.logging import get_logger
import json

logger = get_logger("sentra_brain_api.features.chat")

class ChatController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _get_service(self) -> ChatApiService:
        return ChatApiService()

    def _add_routes(self):
        @self.router.post(
            "/send",
            response_class=StreamingResponse,
            description="Send a message via SentraExecutor",
        )
        async def send_message(
            body: ChatSendRequest,
            request: Request,
            current_user: UserEntity = Depends(get_authenticated_user),
            api_service: ChatApiService = Depends(self._get_service),
        ):
            user_id = str(current_user.id)
            conversation_id = str(body.session_id)

            async def stream():
                try:
                    async for update in api_service.send_message_stream(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        message=body.content,
                    ):
                        payload = jsonable_encoder(update)
                        yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                    # End-of-stream signal
                    yield f"data: {json.dumps({'conversation_id': conversation_id, 'status': 'complete'})}\n\n"
                except Exception as e:
                    logger.exception("Chat stream failed")
                    yield f"data: {json.dumps({'conversation_id': conversation_id, 'error': str(e)})}\n\n"

            return StreamingResponse(
                stream(),
                media_type="text/event-stream; charset=utf-8",
                headers={
                    "Cache-Control": "no-cache, no-transform",
                    "X-Accel-Buffering": "no",
                    "Connection": "keep-alive",
                },
            )
