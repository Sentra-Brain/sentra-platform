"""Pydantic models for conversation handling."""
from __future__ import annotations

from typing import List

from pydantic import BaseModel


class ConversationRequest(BaseModel):
    """Incoming conversation payload."""

    messages: List[str] = []


class ConversationEvent(BaseModel):
    """Event produced during a conversation."""

    message: str
