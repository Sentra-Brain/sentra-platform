# sentra_brain_api/features/conversation/models.py

from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

from sentra_brain_api.core.base_mongo_model import BaseMongoModel


class CreateConversationRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    initial_prompt: Optional[str] = Field(
        default=None,
        description="Optional system prompt to be used as conversation initializer"
    )
    content: str = Field(..., description="First user message in the conversation")


class CreateConversationResponse(BaseModel):
    id: str = Field(..., description="Unique identifier of the conversation")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

class ConversationListItemModel(BaseModel):
    id: str = Field(..., description="Unique identifier of the conversation")
    title: str = Field(..., description="Conversation title")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }
class MessageModel(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(..., description="Timestamp of the message")
    
    model_config = {
        "from_attributes": True
    }

class ConversationModel(BaseMongoModel):   
    title: Optional[str] = None
    description: Optional[str] = None
    initial_prompt: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None 
    messages: List[MessageModel]

class UpdateConversationRequest(BaseModel):
    title: Optional[str] = Field(None, description="Updated title for the conversation")
    description: Optional[str] = Field(None, description="Updated description for the conversation")

class UpdateConversationResponse(BaseModel):
    conversation_id: str = Field(..., description="Unique identifier of the updated conversation")
    title: Optional[str] = Field(None, description="Updated title of the conversation")
    description: Optional[str] = Field(None, description="Updated description of the conversation")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

class DeleteConversationResponse(BaseModel):
    success: bool = Field(..., description="Indicates whether the conversation was successfully deleted")
    message: str = Field(..., description="Message providing additional information about the deletion status")

    model_config = {
        "from_attributes": True
    }

