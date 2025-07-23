import asyncio
import json
import logging
from typing import AsyncGenerator
from datetime import datetime, timezone

from sentra_brain_api.core.conversation_engine.models.input_model import ConversationRequest
from sentra_brain_api.core.conversation_engine.models.output_model import ConversationDelta
from sentra_brain_api.core.conversation_engine.prompt_factory import PromptFactory
from sentra_brain_api.core.conversation_engine.llama_server_client import LlamaServerClient
from sentra_brain_api.core.conversation_engine.conversations_cache import ConversationsCache
from sentra_brain_api.core.constants import CONTEXT_WINDOW_SIZE, USER_CONVERSATION_CACHE_SIZE
from sentra_brain_api.core.exceptions import SentraHTTPException
from sentra_brain_api.infra.mongo_conversation_repository import get_conversation_mongo_repository

logger = logging.getLogger("sentra_brain_engine")


class ConversationEngine:
    def __init__(self, mongo_repo=None, llama_client=None):
        self.mongo_repo = mongo_repo or get_conversation_mongo_repository()
        self.llama_client = llama_client or LlamaServerClient()
        self.prompt_factory = PromptFactory()
        self.cache = ConversationsCache(
            capacity=USER_CONVERSATION_CACHE_SIZE,
            on_evict=self._on_cache_evict
        )

    async def run(self, request: ConversationRequest) -> AsyncGenerator[ConversationDelta, None]:
        logger.info(f"[Engine] Starting run: user={request.user_id}, conversation={request.conversation_id}")

        now = datetime.now(timezone.utc).isoformat()

        context = await self._load_context(request.user_id, request.conversation_id)
        user_msg = self._make_message("user", request.content, now)
        await self._persist_user_message(request, user_msg)

        context.append(user_msg)
        context = context[-CONTEXT_WINDOW_SIZE:]

        payload = self.prompt_factory.build_payload(
            context=context,
            new_message=user_msg
        )

        buffer = ""
        async for delta in self._llama_stream(payload):
            buffer += delta
            yield ConversationDelta(content=delta)

        if not buffer.strip():
            logger.warning(f"No LLM response for user={request.user_id} conv={request.conversation_id}")
            yield ConversationDelta(content="(No response)", final=True)
            return

        assistant_msg = self._make_message("assistant", buffer, now)
        await self._persist_assistant_message(request, assistant_msg)

        context.append(assistant_msg)
        self.cache.put(request.user_id, request.conversation_id, context[-CONTEXT_WINDOW_SIZE:])

        yield ConversationDelta(content="", final=True)
        logger.info(f"[Engine] Completed run: user={request.user_id}, conversation={request.conversation_id}")


    async def _llama_stream(self, payload: dict):
        response = await self.llama_client.chat_completion(payload)

        async for line in response.aiter_lines():
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


    async def _load_context(self, user_id: str, conversation_id: str) -> list[dict]:
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
        return {
            "role": role,
            "content": content,
            "timestamp": timestamp,
            **extra
        }

    def _create_payload(self, context: list[dict], temperature: float = 0.7) -> dict:
        return {
            "messages": context,
            "stream": True,
            "temperature": temperature
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

    def _on_cache_evict(self, user_id: str, conversation_id: str, messages: list[dict]):
        logger.info(f"[Cache] Evicted: user_id={user_id}, conversation_id={conversation_id}, messages={len(messages)}")
        logger.debug(f"[Cache] Last messages before eviction: {messages[-3:]}")
