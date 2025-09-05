"""Domain service for managing chat sessions."""

from typing import Optional
from uuid import UUID

from sentra.domain.entities.session_entity import SessionEntity
from sentra.domain.entities.user_entity import UserEntity
from sentra.domain.repository.session_repository import SessionRepository
from sentra.infra.nosql.mongo_session_repository import MongoSessionRepository


class SessionService:
    def __init__(self, sql_repo: SessionRepository, mongo_repo: MongoSessionRepository):
        self.sql_repo = sql_repo
        self.mongo_repo = mongo_repo

    def create_session(self, user: UserEntity, session: SessionEntity, initial_user_prompt: str | None = None) -> SessionEntity:
        session = self.sql_repo.create(session)

        self.mongo_repo.create_session(
            session_id=session.id,
            user_id=user.id,
            title=session.title,
            created_at=session.created_at.isoformat(),
        )

        return session

    def get_user_sessions(self, user_id: UUID) -> list[SessionEntity]:
        return self.sql_repo.get_sessions_by_user_id(user_id)

    def get_session(self, session_id: UUID, user_id: UUID) -> dict:
        return self.mongo_repo.get_session_by_id(session_id, user_id)

    def update_session(
        self, session_id: UUID, user_id: UUID, title: Optional[str], description: Optional[str]
    ) -> Optional[SessionEntity]:
        session = self.sql_repo.get(session_id)
        if not session:
            return None

        if title:
            session.title = title
        if description:
            session.description = description

        self.sql_repo.update(session)

        self.mongo_repo.get_sessions_collection().update_one(
            {"_id": session_id, "user_id": user_id},
            {"$set": {"title": title, "description": description}},
        )

        return session

    def delete_session(self, session_id: UUID, user_id: UUID) -> bool:
        deleted = False

        session = self.sql_repo.get(session_id)
        if session and session.created_by_id == user_id:
            self.sql_repo.delete(session_id)
            deleted = True

        result = self.mongo_repo.get_sessions_collection().delete_one(
            {"_id": session_id, "user_id": user_id}
        )

        return deleted or result.deleted_count > 0

    def update_title(self, session_id: UUID, user_id: UUID, title: str):
        self.sql_repo.update_title(session_id, title)
        self.mongo_repo.update_session(session_id, {"title": title})

    def update_state(self, session_id: UUID, user_id: UUID, state: dict) -> bool:
        updated = self.mongo_repo.update_session(session_id, {"state": state})
        return updated > 0
