# sentra_brain_api/features/conversation/models.py

from pydantic import BaseModel


class CreateConversationRequest(BaseModel):
    user_id: str


class CreateConversationResponse(BaseModel):
    conversation_id: str
