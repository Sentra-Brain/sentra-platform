from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_brain_api.features.session.api_service import SessionApiService
from sentra_brain_api.features.session.schemas import (
    CreateSessionRequest,
    CreateSessionResponse,
    DeleteSessionResponse,
    EventResponse,
    SessionListItemResponse,
    SessionResponse,
    UpdateSessionRequest,
    UpdateSessionResponse,
    UpdateSessionStateRequest,
    UpdateSessionStateResponse,
)
from sentra_brain_api.features.chat.schemas import SessionRequest, SessionEvent
from sentra_brain_api.features.chat.mappers import engine_event_to_wire
from sentra_core.domain.entities.user_entity import UserEntity
from sentra_core.domain.event_entity import EventEntity
from sentra_core.infra.nosql.mongo_session_repository import (
    MongoSessionRepository,
    get_session_mongo_repository,
)
from sentra_core.infra.sql.postgres_service import get_db
from sentra_core.logging import get_logger
from sentra_core.settings import settings

from sentra_core.services.mongo_session_service import get_session_service
from sentra_engine import run_conversation
from sentra_engine.models import ConversationRequest as EngineRequest

logger = get_logger("sentra_brain_api.session")


class SessionController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _get_service(
        self,
        db: Session = Depends(get_db),
        mongo_repo: MongoSessionRepository = Depends(get_session_mongo_repository),
    ) -> SessionApiService:
        return SessionApiService(db=db, mongo_repo=mongo_repo)

    def _add_routes(self):
        @self.router.post(
            "/",
            response_model=CreateSessionResponse,
            description="Creates a new session for the current user",
        )
        async def create_session(
            body: CreateSessionRequest,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: SessionApiService = Depends(self._get_service),
        ):
            return await service.create_session(current_user, body)

        @self.router.post(
            "/{session_id}/generate-title",
            response_model=UpdateSessionResponse,
            description="Generate a better session title using LLM",
        )
        async def generate_llm_title_for_session(
            session_id: UUID,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: SessionApiService = Depends(self._get_service),
        ):
            return await service.generate_llm_title_for_session(current_user, session_id)

        @self.router.get(
            "/",
            response_model=list[SessionListItemResponse],
            description="Retrieves all sessions for the current user",
        )
        def get_sessions(
            current_user: UserEntity = Depends(get_authenticated_user),
            service: SessionApiService = Depends(self._get_service),
        ):
            return service.list_user_sessions(current_user)

        @self.router.get(
            "/{session_id}",
            response_model=SessionResponse,
            description="Retrieve a specific session by its ID",
        )
        def get_session_by_id(
            session_id: UUID,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: SessionApiService = Depends(self._get_service),
        ):
            return service.get_session(current_user, session_id)

        @self.router.put(
            "/{session_id}",
            response_model=UpdateSessionResponse,
            description="Update title and description of a session",
        )
        def update_session(
            session_id: UUID,
            request: UpdateSessionRequest,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: SessionApiService = Depends(self._get_service),
        ):
            return service.update_session(current_user, session_id, request)

        @self.router.delete(
            "/{session_id}",
            response_model=DeleteSessionResponse,
            description="Delete a session",
        )
        def delete_session(
            session_id: UUID,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: SessionApiService = Depends(self._get_service),
        ):
            return service.delete_session(current_user, session_id)

        @self.router.get(
            "/{session_id}/events",
            response_model=list[EventResponse],
            description="Retrieve events for the session",
        )
        def get_events(
            session_id: UUID,
            since: datetime | None = Query(None),
            current_user: UserEntity = Depends(get_authenticated_user),
            service: SessionApiService = Depends(self._get_service),
        ):
            return service.get_events(current_user, session_id, since)

        @self.router.post(
            "/{session_id}/state",
            response_model=UpdateSessionStateResponse,
            description="Update session state",
        )
        def update_state(
            session_id: UUID,
            body: UpdateSessionStateRequest,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: SessionApiService = Depends(self._get_service),
        ):
            return service.update_state(current_user, session_id, body)
        @self.router.post(
            "/{session_id}/messages",
            response_class=StreamingResponse,
            deprecated=True,
            description="Deprecated: send a message in a session and stream the response",
        )
        async def send_message(
            session_id: UUID,
            body: SessionRequest,
            current_user: UserEntity = Depends(get_authenticated_user),
        ):
            session_service = get_session_service()

            # 1. Persist the user message as an event
            user_event = EventEntity(
                event_id=uuid4().hex,
                timestamp=datetime.now(timezone.utc),
                type="message_final",
                author="user",
                content=body.content,
                message={"id": str(body.message_id or uuid4()), "role": "user"},
            )
            await session_service.append_event(str(session_id), user_event)

            # 2. Build the engine request
            engine_request = EngineRequest(
                user_id=str(current_user.id),
                conversation_id=str(session_id),  # TODO: rename to session_id in models
                messages=[body.content],
                context_source_ids=[str(cid) for cid in body.context_source_ids] if body.context_source_ids else None,
                context_document_ids=[str(cid) for cid in body.context_document_ids] if body.context_document_ids else None,
            )

            # 3. Stream assistant events back
            async def stream():
                try:
                    async for ev in run_conversation(engine_request):
                        out = engine_event_to_wire(ev)
                        yield f"data: {out.model_dump_json()}\n\n"
                except Exception as e:
                    logger.exception("Streaming failed")
                    err_evt = SessionEvent(
                        event_id=uuid4().hex,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        type="step_error",
                        task_type="chat_pipeline",
                        label="Streaming failed",
                        status="error",
                        content=str(e),
                        meta={"path": f"/sessions/{session_id}/messages"},
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
