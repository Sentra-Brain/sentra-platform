# sentra-brain_api/features/conversation/schemas.py

from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from sentra_core.model.base_mongo_model import BaseMongoModel


class CreateConversationRequest(BaseModel):
    # id: UUID = Field(..., description="Unique identifier of the conversation")
    initial_prompt: str = Field(..., description="Initial User Prompt for the conversation")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

class CreateConversationResponse(BaseModel):
    id: UUID = Field(..., description="Unique identifier of the conversation")
    title: str = Field(..., description="Title of the conversation")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

class ConversationListItemResponse(BaseModel):
    id: UUID = Field(..., description="Unique identifier of the conversation")
    title: str = Field(..., description="Conversation title")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

class MessageResponse(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(..., description="Timestamp of the message")

class ConversationResponse(BaseMongoModel):
    title: Optional[str] = None    
    description: Optional[str] = None
    initial_prompt: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[MessageResponse]


class UpdateConversationRequest(BaseModel):
    title: Optional[str] = Field(None, description="Updated title for the conversation")
    description: Optional[str] = Field(None, description="Updated description for the conversation")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }
    
class UpdateConversationResponse(BaseModel):
    conversation_id: UUID = Field(..., description="Unique identifier of the updated conversation")
    title: Optional[str] = Field(None, description="Updated title of the conversation")
    description: Optional[str] = Field(None, description="Updated description of the conversation")




class DeleteConversationResponse(BaseModel):
    success: bool = Field(..., description="Indicates whether the conversation was successfully deleted")
    message: str = Field(..., description="Message providing additional information about the deletion status")

    model_config = {
        "from_attributes": True
    }
