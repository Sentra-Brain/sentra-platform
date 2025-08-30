# sentra_engine/conversation/ports/conversation.py

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional
from sentra_engine.core.models import DeltaEvent


class ConversationEnginePort(ABC):
    @abstractmethod
    def run_fast(
        self,
        *,
        user_id: str,
        conversation_id: str,
        message_id: Optional[str],
        response_message_id: Optional[str],
        content: str,
    ) -> AsyncGenerator[DeltaEvent, None]:
        ...

    @abstractmethod
    def run_planner(
        self,
        *,
        user_id: str,
        conversation_id: str,
        message_id: Optional[str],
        response_message_id: Optional[str],
        content: str,
    ) -> AsyncGenerator[DeltaEvent, None]:
        ...
