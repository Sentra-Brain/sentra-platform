"""Pydantic models for conversation handling."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from sentra.schemas import Event


class ConversationRequest(BaseModel):
    """Incoming conversation payload."""

    messages: List[str] = []
    context_source_ids: Optional[List[str]] = None
    context_document_ids: Optional[List[str]] = None
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    session_state: Optional[Dict[str, Any]] = None



# ``Event`` is re-exported from ``sentra.schemas`` and used across
# runtime, API and persistence layers.

