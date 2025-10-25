# packages/sentra-runtime/src/sentra/runtime/models/conversation.py
"""Pydantic models for conversation handling."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


from pydantic import BaseModel


class ConversationRequest(BaseModel):
    """Incoming conversation payload."""

    messages: List[str] = []
    context_source_ids: Optional[List[str]] = None
    context_document_ids: Optional[List[str]] = None
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    session_state: Optional[Dict[str, Any]] = None
    agent: Optional[str] = None  # explicit agent selection (e.g. "default_agent", "legal")
