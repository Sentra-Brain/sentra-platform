from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from sentra_core.infra.nosql.base_mongo_model import BaseMongoModel


class CreateSessionRequest(BaseModel):
    initial_prompt: str = Field(..., description="Initial user prompt for the session")

    model_config = {"from_attributes": True, "populate_by_name": True}


class CreateSessionResponse(BaseModel):
    id: UUID = Field(..., description="Unique identifier of the session")
    title: str = Field(..., description="Title of the session")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True, "populate_by_name": True}


class SessionListItemResponse(BaseModel):
    id: UUID = Field(..., description="Unique identifier of the session")
    title: str = Field(..., description="Session title")
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


class SessionResponse(BaseMongoModel):
    title: Optional[str] = None
    description: Optional[str] = None
    initial_prompt: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    events: List[EventResponse]


class UpdateSessionRequest(BaseModel):
    title: Optional[str] = Field(
        None, description="Updated title for the session"
    )
    description: Optional[str] = Field(
        None, description="Updated description for the session"
    )

    model_config = {"from_attributes": True, "populate_by_name": True}


class UpdateSessionResponse(BaseModel):
    session_id: UUID = Field(
        ..., description="Unique identifier of the updated session"
    )
    title: Optional[str] = Field(
        None, description="Updated title of the session"
    )
    description: Optional[str] = Field(
        None, description="Updated description of the session"
    )


class DeleteSessionResponse(BaseModel):
    success: bool = Field(
        ..., description="Indicates whether the session was successfully deleted"
    )
    message: str = Field(
        ..., description="Message providing additional information about the deletion status"
    )

    model_config = {"from_attributes": True}


class UpdateSessionStateRequest(BaseModel):
    state: Dict[str, Any] = Field(..., description="Arbitrary session state")


class UpdateSessionStateResponse(BaseModel):
    session_id: UUID = Field(..., description="Unique identifier of the session")
    state: Dict[str, Any] = Field(..., description="Updated session state")
