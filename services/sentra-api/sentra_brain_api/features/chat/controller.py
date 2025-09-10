# services/sentra-api/sentra_brain_api/features/chat/controller.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from sentra_brain_api.adapters.persistence_adapter import MongoPersistenceAdapter
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
 
from sentra_brain_api.features.chat.schemas import ChatSendRequest
from sentra.domain.entities.user_entity import UserEntity
from sentra.domain.models.event import SentraEvent, SentraEventType
from sentra.infra.nosql.mongo_session_repository import MongoSessionRepository, get_session_mongo_repository
from sentra.runtime.app import run_conversation
from sentra.runtime.models import ConversationRequest as EngineRequest
from sentra.shared.logging import get_logger

logger = get_logger("sentra_brain_api.features.chat")

class ChatController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self):
        @self.router.post(
            "/send",
            response_class=StreamingResponse,
            description="Sends a message using the ADK engine and streams the assistant response",
        )
        async def send_message(
            body: ChatSendRequest,
            request: Request,
            mongo_repo: MongoSessionRepository = Depends(get_session_mongo_repository),
            current_user: UserEntity = Depends(get_authenticated_user),
        ):
            adapter = MongoPersistenceAdapter(repo=mongo_repo, user_id=str(current_user.id))
            conversation_id = str(body.session_id)
            await adapter.persist_user_message(
                conversation_id,
                text=body.content,
                event_id=body.event_id,
            )
            recent = await adapter.get_recent_context(conversation_id, limit=50)

            session_state = await adapter.get_session_state(conversation_id)

            engine_request = EngineRequest(
                messages=[*recent, body.content],
                user_id=str(current_user.id),
                conversation_id=conversation_id,
                context_source_ids=[str(cid) for cid in body.context_source_ids] if body.context_source_ids else None,
                context_document_ids=[str(cid) for cid in body.context_document_ids] if body.context_document_ids else None,
                session_state=session_state,
            )

            async def stream():
                try:
                    async for ev in run_conversation(engine_request):
                        await adapter.append_event(conversation_id, ev)
                        yield f"data: {ev.model_dump_json()}\n\n"
                except Exception as e:
                    logger.exception("Streaming failed")
                    err_evt = SentraEvent.error(
                        str(e),
                        status="error",
                        meta={"path": "/chat/send"},
                    )
                    await adapter.append_event(conversation_id, err_evt)
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