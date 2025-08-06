from typing import List, Optional
from pydantic import BaseModel, Field

class ConversationRequest(BaseModel):
    user_id: Optional[str] = Field(default=None, description="ID of the user sending the message") 
    conversation_id: str = Field(..., description="ID of the conversation")
    message_id: Optional[str] = Field(default=None, description="ID of the message being sent")
    response_message_id: Optional[str] = Field(default=None, description="Pre-assigned ID for the assistant response message") 
    content: str = Field(..., description="Content of the message")
    model: Optional[str] = Field(default="sentra-brain", description="Model to use for the conversation")
    parent_message_id: Optional[str] = Field(default=None, description="ID of the parent message")
    intent_override: Optional[str] = Field(default=None, description="Intent to override")
    stream: Optional[bool] = Field(default=True, description="Whether to stream the response")

    context_source_ids: Optional[List[str]] = Field(
        default=None,
        description="List of knowledge source IDs to use for RAG"
    )
    context_document_ids: Optional[List[str]] = Field(
        default=None,
        description="List of document IDs to use for RAG"
    )

