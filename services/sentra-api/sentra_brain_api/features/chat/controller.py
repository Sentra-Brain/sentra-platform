from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
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
        # Internal API
        @self.router.post(
            "/send",
            response_class=StreamingResponse,
            description="Send a message via SentraExecutor (internal format)",
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

        # AG-UI-compatible API
        @self.router.post(
            "/agui/stream",
            response_class=StreamingResponse,
            description="Send a message via AG-UI protocol format",
        )
        async def agui_stream_message(
            request: Request,
            current_user: UserEntity = Depends(get_authenticated_user),
            api_service: ChatApiService = Depends(self._get_service),
        ):
            body = await request.json()
            user_id = str(current_user.id)
            message = body.get("message")
            conversation_id = body.get("thread_id", "default")

            async def stream_agui():
                try:
                    async for update in api_service.send_message_stream(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        message=message,
                    ):
                        agui_event = self._to_agui_event(update)
                        yield f"data: {json.dumps(agui_event, ensure_ascii=False)}\n\n"
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                except Exception as e:
                    logger.exception("AG-UI stream failed")
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

            return StreamingResponse(
                stream_agui(),
                media_type="text/event-stream; charset=utf-8",
                headers={
                    "Cache-Control": "no-cache, no-transform",
                    "X-Accel-Buffering": "no",
                    "Connection": "keep-alive",
                },
            )

    def _to_agui_event(self, update: dict) -> dict:
        match update.get("type"):
            case "message":
                return {"type": "MESSAGE", "content": update.get("content")}
            case "tool_call":
                return {
                    "type": "TOOL_CALL_START",
                    "toolCallId": update.get("id", "call1"),
                    "toolCallName": update.get("name"),
                }
            case "tool_result":
                return {
                    "type": "TOOL_CALL_RESULT",
                    "toolCallId": update.get("id", "call1"),
                    "content": update.get("result"),
                }
            case "error":
                return {"type": "error", "message": update.get("message")}
            case _:
                return {"type": "MESSAGE", "content": str(update)}
