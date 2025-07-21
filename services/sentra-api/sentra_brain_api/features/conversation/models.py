# sentra_brain_api/features/conversation/models.py

from typing import Optional
from pydantic import BaseModel, Field



class CreateConversationRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    initial_prompt: Optional[str] = Field(
        default=None,
        description="Optional system prompt to be used as conversation initializer"
    )
    content: str = Field(..., description="First user message in the conversation")


class CreateConversationResponse(BaseModel):
    conversation_id: str
