from __future__ import annotations

from google.adk.events.event import Event
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.sessions.session import Session
from google.genai import types
from typing_extensions import override

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - only for type checkers
    from sentra_core.infra.nosql.mongo_conversation_repository import (
        MongoConversationRepository,
    )
from sentra_engine.models import ConversationEvent

from .persistence_adapter import ConversationPersistenceAdapter


class MongoSessionService(InMemorySessionService):
    """Session service that persists messages to MongoDB."""

    def __init__(
        self,
        *,
        repo: MongoConversationRepository,
        user_id: str,
        conversation_id: str,
    ) -> None:
        super().__init__()
        self._persistence = ConversationPersistenceAdapter(
            repo=repo, user_id=user_id, conversation_id=conversation_id
        )

    async def save_message(
        self,
        message: types.Content,
        *,
        is_user_message: bool = False,
        is_final: bool = False,
    ) -> None:
        """Persist a message as a :class:`ConversationEvent`."""
        if not message or not message.parts:
            return
        text_parts = [part.text for part in message.parts if part.text]
        content = "".join(text_parts) if text_parts else None
        event_type = (
            "user_message" if is_user_message else "message_final" if is_final else "message_delta"
        )
        conv_event = ConversationEvent(type=event_type, content=content)
        await self._persistence.persist_event(conv_event)

    @override
    async def append_event(self, session: Session, event: Event) -> Event:
        # First let the parent service update session state
        await super().append_event(session=session, event=event)
        if event.content:
            await self.save_message(
                event.content,
                is_user_message=event.author == "user",
                is_final=event.is_final_response(),
            )
        return event
