from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: str
    timestamp: str

class Conversation(BaseModel):
    id: int
    user_id: int
    messages: List[Message]

class CreateConversationRequest(BaseModel):
    user_id: int

class SendMessageRequest(BaseModel):
    conversation_id: int
    sender_id: int
    content: str
