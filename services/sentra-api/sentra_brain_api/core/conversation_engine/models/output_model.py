from pydantic import BaseModel, Field
from typing import Optional

class ConversationDelta(BaseModel):
    role: str = "assistant"
    content: str
    final: bool = False

class ConversationResponse(BaseModel):
    content: str = Field(..., description="Final response content from the assistant.")
