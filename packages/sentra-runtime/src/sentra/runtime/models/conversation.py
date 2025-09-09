# packages/sentra-runtime/src/sentra/runtime/models/conversation.py
"""Pydantic models for conversation handling."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ConversationRequest(BaseModel):
    """Incoming conversation payload."""

    messages: List[str] = []
    context_source_ids: Optional[List[str]] = None
    context_document_ids: Optional[List[str]] = None
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    session_state: Optional[Dict[str, Any]] = None


class EventActions(BaseModel):
    """Container for action side effects."""

    state_delta: Dict[str, Any]


class EventMessage(BaseModel):
    """Metadata about an associated chat message."""

    id: Optional[str] = None
    role: Optional[str] = None
    response_to: Optional[str] = None


class EngineEvent(BaseModel):
    """Event produced during a conversation.

    The structure mirrors the wire protocol used by the API layer so that
    events can be streamed directly to clients.
    """

    event_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    type: str
    content: Optional[str] = None
    author: Optional[str] = None
    task_type: Optional[str] = None
    task_run_id: Optional[str] = None
    step_id: Optional[str] = None
    label: Optional[str] = None
    status: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    actions: Optional[EventActions] = None
    message: Optional[EventMessage] = None
