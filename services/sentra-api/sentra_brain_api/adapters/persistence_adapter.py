# sentra_brain_api/adapters/persistence_adapter.py
import asyncio
from collections.abc import Mapping
from typing import Any
from uuid import uuid4

from sentra_engine.ports.persistence import PersistencePort
from sentra_engine.core.models import Message, StepEvent

def _message_to_store(m: Message) -> dict[str, Any]:
    # Avoid asdict; explicitly map the fields we persist
    return {
        "id": m.id,
        "role": m.role,
        "content": m.content,
        "timestamp": m.timestamp,
        "meta": m.meta,
    }

def _dict_to_message(d: Mapping[str, Any]) -> Message:
    return Message(
        id=str(d.get("id") or uuid4().hex),
        role=str(d.get("role") or "system"),
        content=str(d.get("content") or ""),
        timestamp=d.get("timestamp"),
        meta=d.get("meta"),
    )

class MongoPersistenceAdapter(PersistencePort):
    def __init__(self, *, repo, user_id: str):
        self.repo = repo
        self.user_id = user_id

    async def append_message(self, conversation_id: str, message: Message) -> None:
        payload = _message_to_store(message)
        await asyncio.to_thread(
            self.repo.append_message,
            conversation_id=conversation_id,
            user_id=self.user_id,
            message=payload,
        )

    async def append_step_event(self, conversation_id: str, event: StepEvent) -> None:
        # Not used in fast mode
        return None

    async def load_conversation(self, conversation_id: str) -> list[Message]:
        doc = await asyncio.to_thread(
            self.repo.get_conversation_by_id, conversation_id, self.user_id
        )
        raw: list[Any] = (doc.get("messages") if doc else []) or []
        out: list[Message] = []

        for m in raw:
            if isinstance(m, Message):
                out.append(m)
            elif isinstance(m, Mapping):
                out.append(_dict_to_message(m))
            elif hasattr(m, "model_dump"):           # pydantic v2
                out.append(_dict_to_message(m.model_dump()))  # type: ignore[attr-defined]
            elif hasattr(m, "dict"):                  # pydantic v1
                out.append(_dict_to_message(m.dict()))        # type: ignore[attr-defined]
            else:
                # last-resort: try object's __dict__ or stringify
                try:
                    d = vars(m)
                    if isinstance(d, dict):
                        out.append(_dict_to_message(d))
                        continue
                except Exception:
                    pass
                out.append(Message(id=uuid4().hex, role="system", content=str(m)))

        return out
