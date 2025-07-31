from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sentra_brain_api.core.app_state import AppState
from sentra_brain_api.core.conversation_engine.engine import ConversationEngine
from sentra_brain_api.core.conversation_engine.models.input_model import ConversationRequest
from sentra_brain_api.core.conversation_engine.models.output_model import ConversationDelta
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_core.core.logging import get_logger
from sentra_core.domain.entities.user_entity import UserEntity
import json

logger = get_logger("sentra_brain_api")


class ChatController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self):
        @self.router.post(
            "/send",
            response_class=StreamingResponse,
            description="Sends a message to the assistant and streams the response"
        )
        async def send_message(
            body: ConversationRequest,
            request: Request,
            current_user: UserEntity = Depends(get_authenticated_user)
        ):
            body.user_id = str(current_user.id)
            
            app_state: AppState = request.app.state._sentra
            engine = app_state.conversation_engine

            async def stream():
                try:
                    async for delta in engine.run(body):
                        yield f"data: {json.dumps(delta.model_dump())}\n\n"
                except Exception as e:
                    logger.error(f"Error occurred while streaming response: {e}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            return StreamingResponse(stream(), media_type="text/event-stream")
