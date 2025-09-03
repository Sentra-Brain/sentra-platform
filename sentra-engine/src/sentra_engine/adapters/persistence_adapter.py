import asyncio
from datetime import datetime
from typing import Any, Dict, Set, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - only for type checkers
    from sentra_core.infra.nosql.mongo_conversation_repository import (
        MongoConversationRepository,
    )
from sentra_engine.models import ConversationEvent


class ConversationPersistenceAdapter:
    """Persist conversation events using ``sentra-core`` repositories.

    Events are written to the Mongo conversations repository and de-duplicated
    using a per-process in-memory cache.  Each stored event includes a
    timestamp so chronological order can be reconstructed when replaying.
    """

    def __init__(
        self,
        *,
        repo: "MongoConversationRepository",
        user_id: str,
        conversation_id: str,
    ) -> None:
        self.repo = repo
        self.user_id = user_id
        self.conversation_id = conversation_id
        self._seen: Set[str] = set()

    def _event_key(self, event: ConversationEvent) -> str:
        """Return a stable identifier for an event."""
        if event.step_id:
            return f"{event.step_id}:{event.type}"
        if event.task_run_id:
            return f"{event.task_run_id}:{event.type}"
        return f"{event.type}:{event.content}"

    async def persist_event(self, event: ConversationEvent) -> None:
        """Persist an event if it hasn't been stored before."""
        key = self._event_key(event)
        if key in self._seen:
            return

        payload: Dict[str, Any] = event.model_dump(exclude_none=True)
        payload.setdefault("id", key)
        payload.setdefault("timestamp", datetime.utcnow().isoformat())

        await asyncio.to_thread(
            self.repo.append_message,
            conversation_id=self.conversation_id,
            user_id=self.user_id,
            message=payload,
        )
        self._seen.add(key)
