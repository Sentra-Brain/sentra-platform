import asyncio
import json
import logging
from typing import AsyncGenerator
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sentra_brain_api.core.conversation_engine.models.input_model import ConversationRequest
from sentra_brain_api.core.conversation_engine.models.output_model import ConversationEvent
from sentra_brain_api.core.conversation_engine.prompt_factory import PromptFactory
from sentra_brain_api.core.conversation_engine.conversations_cache import ConversationsCache
from sentra_brain_api.core.conversation_engine.rag.rag_client import RagClient
from sentra_brain_api.core.constants import CONTEXT_WINDOW_SIZE, USER_CONVERSATION_CACHE_SIZE
from sentra_brain_api.core.exceptions import SentraHTTPException
from sentra_core.infra.nosql.mongo_conversation_repository import get_conversation_mongo_repository
from sentra_core.core.settings import settings
from sentra_brain_api.core.conversation_engine.llm.factory import build_llm_client
from sentra_brain_api.crosscutting.json_sanitize import json_safe


logger = logging.getLogger("sentra_brain_engine")


class ConversationEngine:
    def __init__(self, mongo_repo=None, llm_client=None, rag_client=None):

        self.mongo_repo = mongo_repo or get_conversation_mongo_repository()
        self.llm_client = llm_client or build_llm_client(
            engine=settings.llm_engine,
            vllm_url=settings.vllm_server_url,
            llama_url=settings.llama_server_url,
            request_timeout=None,
        )
        self.rag_client = rag_client or RagClient()
        self.prompt_factory = PromptFactory()
        self.cache = ConversationsCache(
            capacity=USER_CONVERSATION_CACHE_SIZE,
            on_evict=self._on_cache_evict
        )

    async def run(self, request: ConversationRequest) -> AsyncGenerator[ConversationEvent, None]:
        logger.info(f"[Engine] Starting run: user={request.user_id}, conversation={request.conversation_id}")

        now = datetime.now(timezone.utc).isoformat()
        task_run_id = None

        # Emit RAG step events if context is requested
        if request.context_source_ids  or request.context_document_ids:
            task_run_id = uuid4().hex
            
            # Start RAG search step
            step_start_event = ConversationEvent(
                type="step_start",
                task_type="rag_search",
                task_run_id=task_run_id,
                label="Searching Knowledge Base",
                status="searching",
                content="💡 Searching in the Knowledge Base..."
            )
            yield step_start_event
            await self._persist_step_event(request, step_start_event)

        rag_chunks = await self.rag_client.retrieve_relevant_chunks(
            query=request.content,
            source_ids=request.context_source_ids,
            document_ids=request.context_document_ids
        )

        # Emit RAG step end if we started a RAG search
        if task_run_id:
            step_end_event = ConversationEvent(
                type="step_end",
                task_type="rag_search",
                task_run_id=task_run_id,
                label="Knowledge Base Search Complete",
                status="completed",
                content=f"Found {len(rag_chunks)} relevant chunks",
                meta={
                    "chunks_found": len(rag_chunks),
                    "source_ids": request.context_source_ids,
                    "document_ids": request.context_document_ids
                }
            )
            yield step_end_event
            await self._persist_step_event(request, step_end_event)
        
        context = await self._load_context(request.user_id, request.conversation_id)

        user_msg = self._make_message("user", request.content, now, message_id=request.message_id)
        await self._persist_user_message(request, user_msg)


        payload = self.prompt_factory.build_payload(
            context=context,
            new_message=user_msg,
            rag_chunks=rag_chunks            
        )

        buffer = ""
        async for delta in self._stream_llm(payload):
            buffer += delta
            yield ConversationEvent(
                type="message_delta",
                content=delta
            )

        if not buffer.strip():
            logger.warning(f"No LLM response for user={request.user_id} conv={request.conversation_id}")
            yield ConversationEvent(
                type="message_final",
                content="(No response)"
            )
            return

        assistant_msg = self._make_message("assistant", buffer, now, message_id=request.response_message_id)
        await self._persist_assistant_message(request, assistant_msg)

        context.append(assistant_msg)
        self.cache.put(request.user_id, request.conversation_id, context[-CONTEXT_WINDOW_SIZE:])

        yield ConversationEvent(
            type="message_final",
            content=""
        )
        logger.info(f"[Engine] Completed run: user={request.user_id}, conversation={request.conversation_id}")

    async def _stream_llm(self, payload: dict):
        async for line in self.llm_client.chat_completion(payload):
            if not line.strip():
                continue

            if line.startswith("data:"):
                line = line[len("data:"):].strip()

            try:
                data = json.loads(line)
                delta = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                if delta:
                    yield delta
            except json.JSONDecodeError as e:
                logger.warning(f"Streaming JSON parse error: {e} | line: {line!r}")
            except Exception as e:
                logger.error(f"Unexpected error in streaming loop: {e}")

    async def _load_context(self, user_id: UUID, conversation_id: UUID) -> list[dict]:
        try:
            cached = self.cache.get(user_id, conversation_id)
            if cached is not None:
                logger.debug(f"[Cache HIT] user={user_id}, conversation={conversation_id}")
                return list(cached)
            
            logger.debug(f"[Cache MISS] user={user_id}, conversation={conversation_id}")
            doc = self.mongo_repo.get_conversation_by_id(conversation_id, user_id)
            if not doc:
                raise SentraHTTPException(
                    status_code=404,
                    code="CONVERSATION_NOT_FOUND",
                    message="Conversation not found.",
                    details=f"Conversation ID: {conversation_id}",
                    path="/chat/send",
                    suggestion="Verify the conversation_id is correct."
                )
            messages = doc.get("messages", [])
            if not isinstance(messages, list):
                raise SentraHTTPException(
                    status_code=500,
                    code="INVALID_CONVERSATION_DATA",
                    message="Invalid messages format in conversation",
                    details=f"Expected list, got: {type(messages).__name__}",
                    path="/chat/send"
                )
            trimmed = messages[-CONTEXT_WINDOW_SIZE:]
            self.cache.put(user_id, conversation_id, trimmed)
            return trimmed
        except SentraHTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to load context: {e}")
            raise SentraHTTPException(
                status_code=500,
                code="CONTEXT_LOAD_FAILED",
                message="Failed to load conversation context.",
                details=str(e),
                path="/chat/send",
                suggestion="Try again or contact support."
            )

    def _make_message(self, role: str, content: str, timestamp: str, **extra) -> dict:
        mid = extra.pop("message_id", None)
        rid = extra.pop("response_message_id", None)
        final_id = str(mid or rid or uuid4().hex)

        safe_extra = {k: json_safe(v) for k, v in extra.items() if v is not None}

        return {
            "id": final_id,
            "role": role,
            "content": content,
            "timestamp": timestamp,
            **safe_extra
        }        

    async def _persist_user_message(self, request: ConversationRequest, message: dict):
        try:
            self.mongo_repo.append_message(
                conversation_id=request.conversation_id,
                user_id=request.user_id,
                message=message
            )
        except Exception as e:
            logger.error(f"Failed to persist user message: {e}")
            raise SentraHTTPException(
                status_code=500,
                code="USER_MESSAGE_STORE_FAILED",
                message="Failed to store user message.",
                details=str(e),
                path="/chat/send"
            )

    async def _persist_assistant_message(self, request: ConversationRequest, message: dict):
        try:
            self.mongo_repo.append_message(
                conversation_id=request.conversation_id,
                user_id=request.user_id,
                message=message
            )
        except Exception as e:
            logger.error(f"Failed to persist assistant message: {e}")
            raise SentraHTTPException(
                status_code=500,
                code="ASSISTANT_MESSAGE_STORE_FAILED",
                message="Failed to store assistant response.",
                details=str(e),
                path="/chat/send"
            )

    async def _persist_step_event(self, request: ConversationRequest, event: ConversationEvent):
        """Persist step events as system messages in MongoDB"""
        try:
            system_message = {
                "id": event.event_id,
                "role": "system",
                "content": event.content,
                "timestamp": event.timestamp,
                "event_type": event.type,
                "task_type": event.task_type,
                "task_run_id": event.task_run_id,
                "step_id": event.step_id,
                "label": event.label,
                "status": event.status,
                "meta": event.meta
            }
            
            self.mongo_repo.append_message(
                conversation_id=request.conversation_id,
                user_id=request.user_id,
                message=system_message
            )
        except Exception as e:
            logger.error(f"Failed to persist step event: {e}")
            # Don't raise exception for step events to avoid breaking the conversation flow
            # but log the error for monitoring

    def _on_cache_evict(self, user_id: str, conversation_id: str, messages: list[dict]):
        logger.info(f"[Cache] Evicted: user_id={user_id}, conversation_id={conversation_id}, messages={len(messages)}")
        logger.debug(f"[Cache] Last messages before eviction: {messages[-3:]}")
