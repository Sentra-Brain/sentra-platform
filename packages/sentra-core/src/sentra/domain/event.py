from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EventActions(BaseModel):
    state_delta: dict[str, Any]


class EventMessage(BaseModel):
    id: Optional[str] = None
    role: Optional[str] = None
    response_to: Optional[str] = None


class Event(BaseModel):
    """Unified event model used across runtime, API and persistence."""

    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    type: str
    role: str = "system"
    content: Optional[str] = None
    task_type: Optional[str] = None
    task_run_id: Optional[str] = None
    step_id: Optional[str] = None
    label: Optional[str] = None
    status: Optional[str] = None
    meta: dict[str, Any] = Field(default_factory=dict)
    actions: Optional[EventActions] = None
    message: Optional[EventMessage] = None

