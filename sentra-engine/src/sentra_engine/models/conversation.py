"""Pydantic models for conversation handling."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ConversationRequest(BaseModel):
    """Incoming conversation payload."""

    messages: List[str] = []
    context_source_ids: Optional[List[str]] = None
    context_document_ids: Optional[List[str]] = None


class ConversationEvent(BaseModel):
    """Event produced during a conversation.

    The structure mirrors the wire protocol used by the API layer so that
    events can be streamed directly to clients.
    """

    type: str
    content: Optional[str] = None
    task_type: Optional[str] = None
    task_run_id: Optional[str] = None
    step_id: Optional[str] = None
    label: Optional[str] = None
    status: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    plan_step_id: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None
