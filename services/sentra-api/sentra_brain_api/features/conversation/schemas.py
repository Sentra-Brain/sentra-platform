
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from sentra.infra.nosql.base_mongo_model import BaseMongoModel

class CreateConversationRequest(BaseModel):
	initial_prompt: str = Field(..., description="Initial user prompt for the conversation")
	model_config = {"from_attributes": True, "populate_by_name": True}

class CreateConversationResponse(BaseModel):
	id: UUID = Field(..., description="Unique identifier of the conversation")
	title: str = Field(..., description="Title of the conversation")
	created_at: datetime = Field(..., description="Creation timestamp")
	model_config = {"from_attributes": True, "populate_by_name": True}

class ConversationListItemResponse(BaseModel):
	id: UUID = Field(..., description="Unique identifier of the conversation")
	title: str = Field(..., description="Conversation title")
	created_at: datetime = Field(..., description="Creation timestamp")
	model_config = {"from_attributes": True, "populate_by_name": True}

class EventResponse(BaseModel):
	id: UUID = Field(..., description="Unique identifier of the event")
	role: Literal["user", "assistant", "system"] = Field(..., description="Role of the event sender")
	content: str = Field(..., description="Content of the event")
	timestamp: datetime = Field(..., description="Timestamp of the event")
	is_system_prompt: Optional[bool] = Field(
		None, description="Indicates if the event is a system prompt"
	)

class ConversationResponse(BaseMongoModel):
	title: Optional[str] = None
	description: Optional[str] = None
	initial_prompt: Optional[str] = None
	created_at: datetime
	updated_at: Optional[datetime] = None
	events: List[EventResponse]

class UpdateConversationRequest(BaseModel):
	title: Optional[str] = Field(
		None, description="Updated title for the conversation"
	)
	description: Optional[str] = Field(
		None, description="Updated description for the conversation"
	)
	model_config = {"from_attributes": True, "populate_by_name": True}

class UpdateConversationResponse(BaseModel):
	conversation_id: UUID = Field(
		..., description="Unique identifier of the updated conversation"
	)
	title: Optional[str] = Field(
		None, description="Updated title of the conversation"
	)
	description: Optional[str] = Field(
		None, description="Updated description of the conversation"
	)

class DeleteConversationResponse(BaseModel):
	success: bool = Field(
		..., description="Indicates whether the conversation was successfully deleted"
	)
	message: str = Field(
		..., description="Message providing additional information about the deletion status"
	)
	model_config = {"from_attributes": True}

class UpdateConversationStateRequest(BaseModel):
	state: Dict[str, Any] = Field(..., description="Arbitrary conversation state")

class UpdateConversationStateResponse(BaseModel):
	conversation_id: UUID = Field(..., description="Unique identifier of the conversation")
	state: Dict[str, Any] = Field(..., description="Updated conversation state")
