# sentra_brain_api/features/chat/controller_adk.py
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import StreamingResponse
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_core.logging import get_logger
from sentra_core.domain.entities.user_entity import UserEntity
from sentra_core.infra.nosql.mongo_session_repository import (
    MongoSessionRepository,
    get_session_mongo_repository,
)
from sentra_brain_api.features.chat.schemas import (
    SessionRequest,
    SessionEvent,
)
from sentra_brain_api.features.chat.mappers import engine_event_to_wire
from sentra_engine.app import run_conversation
from sentra_engine.models import ConversationRequest as EngineRequest

logger = get_logger("sentra_brain_api.chat.v2")


class ChatControllerADK:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self):
        @self.router.post(
            "/send",
            response_class=StreamingResponse,
            description="Sends a message using the ADK engine and streams the assistant response",
        )
        async def send_message_v2(
            body: SessionRequest,
            request: Request,
            mongo_repo: MongoSessionRepository = Depends(get_session_mongo_repository),
            current_user: UserEntity = Depends(get_authenticated_user),
        ):
            body.user_id = current_user.id

            engine_request = EngineRequest(
                messages=[body.content],
                context_source_ids=[
                    str(cid) for cid in body.context_source_ids
                ]
                if body.context_source_ids
                else None,
                context_document_ids=[
                    str(cid) for cid in body.context_document_ids
                ]
                if body.context_document_ids
                else None,
                user_id=str(body.user_id),
                conversation_id=str(body.session_id),
            )

            async def stream():
                try:
                    async for ev in run_conversation(engine_request):
                        out = engine_event_to_wire(ev)
                        yield f"data: {out.model_dump_json()}\n\n"
                except Exception as e:
                    logger.exception("Streaming failed")
                    err_evt = SessionEvent(
                        type="step_error",
                        task_type="chat_pipeline",
                        label="Streaming failed",
                        status="error",
                        content=str(e),
                        meta={"path": "/chat/send"},
                    )
                    yield f"data: {err_evt.model_dump_json()}\n\n"

            return StreamingResponse(
                stream(),
                media_type="text/event-stream; charset=utf-8",
                headers={
                    "Cache-Control": "no-cache, no-transform",
                    "X-Accel-Buffering": "no",
                    "Connection": "keep-alive",
                },
            )
