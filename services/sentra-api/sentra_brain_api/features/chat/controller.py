# sentra_brain_api/features/chat/controller.py
from fastapi import APIRouter, Depends, Request, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
from uuid import UUID

from sentra_brain_api.core.app_state import AppState
from sentra_brain_api.core.conversation_engine.engine import ConversationEngine
from sentra_brain_api.core.conversation_engine.models.input_model import ConversationRequest
from sentra_brain_api.core.conversation_engine.models.output_model import ConversationDelta
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_brain_api.features.knowledge.rag_service import RAGQueryService
from sentra_brain_api.features.knowledge.schemas import RAGContextRequest
from sentra_core.core.logging import get_logger
from sentra_core.domain.entities.user_entity import UserEntity
import json

logger = get_logger("sentra_brain_api")


class ChatController:
    def __init__(self):
        self.router = APIRouter()
        self.rag_service = RAGQueryService()
        self._add_routes()

    def _add_routes(self):
        @self.router.post(
            "/send",
            response_class=StreamingResponse,
            description="Sends a message to the assistant and streams the response"
        )
        async def send_message(
            body: ConversationRequest,
            request: Request,
            current_user: UserEntity = Depends(get_authenticated_user)
        ):
            body.user_id = str(current_user.id)
            
            app_state: AppState = request.app.state._sentra
            engine = app_state.conversation_engine

            async def stream():
                try:
                    async for delta in engine.run(body):
                        yield f"data: {json.dumps(delta.model_dump())}\n\n"
                except Exception as e:
                    logger.error(f"Error occurred while streaming response: {e}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            return StreamingResponse(stream(), media_type="text/event-stream")

        @self.router.post(
            "/send-rag",
            response_class=StreamingResponse,
            description="Sends a message to the assistant with RAG context and streams the response"
        )
        async def send_message_with_rag(
            body: ConversationRequest,
            request: Request,
            knowledge_source_id: Optional[str] = Query(None, description="Optional knowledge source filter"),
            max_context_tokens: int = Query(3000, description="Maximum tokens for RAG context"),
            current_user: UserEntity = Depends(get_authenticated_user)
        ):
            """
            Enhanced chat endpoint that augments user messages with relevant context from the knowledge base.
            """
            body.user_id = str(current_user.id)
            
            try:
                # Get the user's latest message to use for RAG context
                user_message = ""
                if body.messages and len(body.messages) > 0:
                    user_message = body.messages[-1].content
                
                if not user_message:
                    raise HTTPException(status_code=400, detail="No user message found for RAG context")
                
                # Parse knowledge_source_id if provided
                knowledge_source_uuid = None
                if knowledge_source_id:
                    try:
                        knowledge_source_uuid = UUID(knowledge_source_id)
                    except ValueError:
                        raise HTTPException(status_code=400, detail="Invalid knowledge source ID format")
                
                # Get RAG context for the user's message
                logger.info(f"Generating RAG context for message: {user_message[:100]}...")
                rag_context = await self.rag_service.get_context_for_query(
                    query=user_message,
                    knowledge_source_id=knowledge_source_uuid,
                    max_tokens=max_context_tokens
                )
                
                # If we have context, inject it into the conversation
                if rag_context:
                    logger.info(f"Injecting RAG context ({len(rag_context)} chars)")
                    
                    # Create a system message with the context
                    context_message = {
                        "role": "system",
                        "content": f"{rag_context}\n\nBased on the above information from the knowledge base, please answer the user's question. If the information doesn't contain relevant details, please state that clearly."
                    }
                    
                    # Insert context message before the last user message
                    if len(body.messages) > 0:
                        body.messages.insert(-1, context_message)
                    else:
                        body.messages = [context_message]
                else:
                    logger.info("No relevant context found, proceeding with normal conversation")
                
                # Run the conversation with potential RAG context
                app_state: AppState = request.app.state._sentra
                engine = app_state.conversation_engine

                async def stream():
                    try:
                        async for delta in engine.run(body):
                            yield f"data: {json.dumps(delta.model_dump())}\n\n"
                    except Exception as e:
                        logger.error(f"Error occurred while streaming RAG response: {e}")
                        yield f"data: {json.dumps({'error': str(e)})}\n\n"

                return StreamingResponse(stream(), media_type="text/event-stream")
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error in RAG-enhanced chat: {e}")
                raise HTTPException(status_code=500, detail=f"RAG enhancement failed: {str(e)}")

        @self.router.get(
            "/context-preview",
            description="Preview RAG context that would be used for a given message"
        )
        async def preview_rag_context(
            q: str = Query(..., description="Query to generate context for"),
            knowledge_source_id: Optional[str] = Query(None, description="Optional knowledge source filter"),
            max_tokens: int = Query(3000, description="Maximum tokens for context"),
            current_user: UserEntity = Depends(get_authenticated_user)
        ):
            """
            Preview the RAG context that would be injected for a given query.
            Useful for debugging and understanding what information will be provided to the LLM.
            """
            try:
                # Parse knowledge_source_id if provided
                knowledge_source_uuid = None
                if knowledge_source_id:
                    try:
                        knowledge_source_uuid = UUID(knowledge_source_id)
                    except ValueError:
                        raise HTTPException(status_code=400, detail="Invalid knowledge source ID format")
                
                # Generate context
                context = await self.rag_service.get_context_for_query(
                    query=q,
                    knowledge_source_id=knowledge_source_uuid,
                    max_tokens=max_tokens
                )
                
                # Count sources and estimate tokens
                sources_used = context.count("Source:") if context else 0
                estimated_tokens = len(context) // 4 if context else 0
                
                return {
                    "query": q,
                    "context": context,
                    "sources_used": sources_used,
                    "estimated_tokens": estimated_tokens,
                    "has_context": bool(context)
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error generating context preview: {e}")
                raise HTTPException(status_code=500, detail=f"Context preview failed: {str(e)}")
