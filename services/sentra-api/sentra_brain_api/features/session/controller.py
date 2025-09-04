from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_brain_api.features.session.api_service import SessionApiService
from sentra_brain_api.features.session.schemas import (
    CreateSessionRequest,
    CreateSessionResponse,
    DeleteSessionResponse,
    SessionListItemResponse,
    SessionResponse,
    UpdateSessionRequest,
    UpdateSessionResponse,
)
from sentra_core.domain.entities.user_entity import UserEntity
from sentra_core.infra.nosql.mongo_session_repository import (
    MongoSessionRepository,
    get_session_mongo_repository,
)
from sentra_core.infra.sql.postgres_service import get_db


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
