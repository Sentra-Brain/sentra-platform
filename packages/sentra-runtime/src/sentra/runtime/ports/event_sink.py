# sentra/runtime/ports/event_sink.py
from typing import Protocol

from sentra.domain.models.event import SentraEvent


class EventSink(Protocol):
    async def on_event(self, event: SentraEvent) -> None: ...
