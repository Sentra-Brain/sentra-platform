from pydantic import BaseModel, Field

class ConversationDelta(BaseModel):
    role: str = "assistant"
    content: str
    final: bool = False

class ConversationResponse(BaseModel):
    content: str = Field(..., description="Final response content from the assistant.")
