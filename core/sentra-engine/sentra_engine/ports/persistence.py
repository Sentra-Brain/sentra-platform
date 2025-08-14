# sentra_engine/ports/persistence.py
from abc import ABC, abstractmethod
from sentra_engine.core.models import Message, StepEvent


class PersistencePort(ABC):
    @abstractmethod
    async def append_message(self, conversation_id: str, message: Message) -> None:
        """Persist a message in a conversation."""
        raise NotImplementedError

    @abstractmethod
    async def append_step_event(self, conversation_id: str, event: StepEvent) -> None:
        """Persist a step event for a conversation."""
        raise NotImplementedError

    @abstractmethod
    async def load_conversation(self, conversation_id: str) -> list[Message]:
        """Load messages for a given conversation."""
        raise NotImplementedError
