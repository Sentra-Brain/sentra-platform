from __future__ import annotations

from sentra.schemas import Event
from sentra_brain_api.features.chat.schemas import SessionEvent


def event_to_wire(ev: Event) -> SessionEvent:
    """Serialize an ``Event`` for wire transmission."""

    return SessionEvent(**ev.model_dump(exclude_none=True))
