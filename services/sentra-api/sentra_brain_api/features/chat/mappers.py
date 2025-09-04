from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List
from datetime import datetime, timezone
import inspect
import uuid

from sentra_brain_api.features.chat.schemas import PlanOutlineStep, SessionEvent

def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()

def _id() -> str:
    return uuid.uuid4().hex

def _to_mapping(obj: Any) -> Dict[str, Any]:
    # dataclass instance (no classes)
    if is_dataclass(obj) and not inspect.isclass(obj):
        return asdict(obj)

    # pydantic v2
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump()  # type: ignore[attr-defined]
        except Exception:
            pass

    # explicit dict
    if isinstance(obj, dict):
        return dict(obj)

    # fallback 
    keys = (
        "type", "content", "label", "status", "meta",
        "plan_step_id", "steps", "task_type", "task_run_id", "step_id",
        "event_id", "timestamp",
    )
    d: Dict[str, Any] = {}
    for k in keys:
        if hasattr(obj, k):
            d[k] = getattr(obj, k)
    return d or {"type": "step_error", "content": str(obj)}

def engine_event_to_wire(ev: Any) -> SessionEvent:
    d: Dict[str, Any] = _to_mapping(ev)

    # Defaults
    d.setdefault("event_id", _id())
    d.setdefault("timestamp", _ts())

    # Normalize steps
    if d.get("type") == "plan_outline":
        raw_steps = d.get("steps") or []
        norm: List[PlanOutlineStep] = []
        for s in raw_steps:
            if isinstance(s, PlanOutlineStep):
                norm.append(s)
            elif is_dataclass(s) and not inspect.isclass(s):
                norm.append(PlanOutlineStep(**asdict(s)))
            elif isinstance(s, dict):
                norm.append(PlanOutlineStep(**s))
            elif hasattr(s, "model_dump"):
                norm.append(PlanOutlineStep(**s.model_dump()))  # type: ignore[attr-defined]
            else:
                # Last resort: loose attributes
                norm.append(
                    PlanOutlineStep(
                        step_id=str(getattr(s, "step_id", _id())),
                        title=str(getattr(s, "title", "Step")),
                        description=str(getattr(s, "description", "")),
                        action=str(getattr(s, "action", "respond")),  # type: ignore[arg-type]
                        args_hint=getattr(s, "args_hint", None),
                    )
                )
        d["steps"] = norm

    return SessionEvent(**d)
