# services/sentra-api/sentra_brain_api/features/chat/mappers.py
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sentra.runtime.models.conversation import EngineEvent
from sentra_brain_api.features.chat.schemas import SessionEvent


def engine_event_to_wire(ev: EngineEvent) -> SessionEvent:
    """Serialize an ``EngineEvent`` for wire transmission.

    Ensures the source event has required ``event_id`` and ``timestamp``
    attributes, populating them if missing.
    """

    if ev.event_id is None:
        ev.event_id = uuid4().hex
    if ev.timestamp is None:
        ev.timestamp = datetime.now(timezone.utc)

    data = ev.model_dump(exclude_none=True)
    data["event_id"] = str(ev.event_id)
    ts = ev.timestamp
    if isinstance(ts, datetime):
        data["timestamp"] = ts.isoformat()
    else:
        data["timestamp"] = str(ts)
    return SessionEvent(**data)
