# sentra_brain_api/features/chat/controller.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sentra.runtime.models import ConversationRequest
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra.shared.logging import get_logger
from sentra.domain.entities.user_entity import UserEntity
from sentra.infra.nosql.mongo_session_repository import (
    MongoSessionRepository,
    get_session_mongo_repository,
)
from sentra_brain_api.features.chat.schemas import SessionRequest
from sentra_brain_api.features.chat.mappers import event_to_wire
from sentra_brain_api.adapters.persistence_adapter import MongoPersistenceAdapter
from sentra.schemas import Event

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
        async def send_message_v2(
            body: SessionRequest,
            request: Request,
            mongo_repo: MongoSessionRepository = Depends(get_session_mongo_repository),
            current_user: UserEntity = Depends(get_authenticated_user),
        ):
            body.user_id = current_user.id

            adapter = MongoPersistenceAdapter(repo=mongo_repo, user_id=str(current_user.id))
            conversation_id = str(body.session_id)
            await adapter.persist_user_message(
                conversation_id,
                text=body.content,
                id=str(body.id) if body.id else None,
            )
            recent = await adapter.get_recent_context(conversation_id, limit=50)

            session_state = await adapter.get_session_state(conversation_id)

            engine_request = ConversationRequest(
                messages=[*recent, body.content],
                user_id=str(body.user_id),
                conversation_id=conversation_id,
                context_source_ids=[str(cid) for cid in body.context_source_ids] if body.context_source_ids else None,
                context_document_ids=[str(cid) for cid in body.context_document_ids] if body.context_document_ids else None,
                session_state=session_state,
            )

            async def stream():
                try:
                    from sentra.runtime.app import run_conversation

                    async for ev in run_conversation(engine_request):
                        out = event_to_wire(ev)
                        await adapter.append_event(conversation_id, ev)
                        yield f"data: {out.model_dump_json()}\n\n"
                except Exception as e:
                    logger.exception("Streaming failed")
                    err_evt = Event(
                        type="step_error",
                        role="system",
                        task_type="chat_pipeline",
                        label="Streaming failed",
                        status="error",
                        content=str(e),
                        meta={"path": "/chat/send"},
                    )
                    out = event_to_wire(err_evt)
                    await adapter.append_event(conversation_id, err_evt)
                    yield f"data: {out.model_dump_json()}\n\n"

            return StreamingResponse(
                stream(),
                media_type="text/event-stream; charset=utf-8",
                headers={
                    "Cache-Control": "no-cache, no-transform",
                    "X-Accel-Buffering": "no",
                    "Connection": "keep-alive",
                },
            )