from __future__ import annotations

from datetime import datetime

from sentra.runtime.models.conversation import EngineEvent
from sentra_brain_api.features.chat.schemas import SessionEvent


def engine_event_to_wire(ev: EngineEvent) -> SessionEvent:
    """Serialize an ``EngineEvent`` for wire transmission."""
    data = ev.model_dump(exclude_none=True)
    if ev.event_id is not None:
        data["event_id"] = str(ev.event_id)
    ts = ev.timestamp
    if isinstance(ts, datetime):
        data["timestamp"] = ts.isoformat()
    else:
        data["timestamp"] = str(ts)
    return SessionEvent(**data)
