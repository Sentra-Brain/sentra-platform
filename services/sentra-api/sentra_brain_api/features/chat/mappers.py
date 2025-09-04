from __future__ import annotations

from typing import List

from sentra_core.schemas.engine_event import EngineEvent
from sentra_brain_api.features.chat.schemas import PlanOutlineStep, SessionEvent


def engine_event_to_wire(ev: EngineEvent) -> SessionEvent:
    """Serialize an ``EngineEvent`` for wire transmission."""
    data = ev.model_dump()
    data["event_id"] = str(ev.event_id)
    data["timestamp"] = ev.timestamp.isoformat()

    if ev.type == "plan_outline" and isinstance(ev.content, dict):
        raw_steps = ev.content.get("steps") or []
        steps: List[PlanOutlineStep] = []
        for s in raw_steps:
            if isinstance(s, PlanOutlineStep):
                steps.append(s)
            elif isinstance(s, dict):
                steps.append(PlanOutlineStep(**s))
        data["steps"] = steps
        data.pop("content", None)

    return SessionEvent(**data)
