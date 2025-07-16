from fastapi import APIRouter, HTTPException, status
from .models import Conversation, Message, CreateConversationRequest, SendMessageRequest
import logging

router = APIRouter()
logger = logging.getLogger("conversations")

@router.get("/", response_model=list[Conversation])
def list_conversations():
    logger.info("Listing conversations")
    return []

@router.post("/", response_model=Conversation)
def create_conversation(request: CreateConversationRequest):
    logger.info(f"Creating conversation for user {request.user_id}")
    return Conversation(id=1, user_id=request.user_id, messages=[])

@router.get("/{conversation_id}", response_model=Conversation)
def get_conversation(conversation_id: int):
    logger.info(f"Getting conversation {conversation_id}")
    return Conversation(id=conversation_id, user_id=1, messages=[])

@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: int):
    logger.info(f"Deleting conversation {conversation_id}")
    return {"ok": True}

@router.post("/{conversation_id}/messages", response_model=Message)
def send_message(conversation_id: int, request: SendMessageRequest):
    logger.info(f"Sending message in conversation {conversation_id}")
    return Message(id=1, conversation_id=conversation_id, sender_id=request.sender_id, content=request.content, timestamp="2025-07-16T00:00:00Z")
