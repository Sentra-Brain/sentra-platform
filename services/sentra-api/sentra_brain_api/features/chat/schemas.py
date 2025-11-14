# services/sentra-api/sentra_brain_api/features/chat/schemas.py
from enum import Enum
from typing import List, Optional, Literal, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

class SessionMode(str, Enum):
    FAST = "fast"
    PLAN = "plan"


class SessionOptions(BaseModel):
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    max_tokens: Optional[int] = None



class ChatSendRequest(BaseModel):
    session_id: UUID = Field(..., description="ID of the session")
    content: str = Field(..., description="Content of the user message")
    
    # Optional fields
    event_id: Optional[UUID] = Field(
        default=None, description="Client-generated ID of the user event"
    )
    mode: SessionMode = Field(
        default=SessionMode.FAST, description="Engine mode"
    )
    options: Optional[SessionOptions] = None
    context_source_ids: Optional[List[UUID]] = Field(
        default=None, description="RAG sources"
    )
    context_document_ids: Optional[List[UUID]] = Field(
        default=None, description="RAG documents"
    )
    agent: Optional[str] = Field(default=None, description="Explicit agent selection override")