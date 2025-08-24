# sentra_brain_api/features/llm_proxy/controller.py

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sentra_core.core import logging
from sentra_engine.core.models import PromptContext
from sentra_brain_api.features.llm_proxy.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatCompletionUsage,
    ChatMessage
)
from sentra_engine.adapters.llm_adapter_factory import LlmAdapterFactory
import json
from datetime import datetime, timezone
from uuid import uuid4

logger = logging.get_logger("llm_proxy")


class LLMProxyController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _convert_to_prompt_context(self, request: ChatCompletionRequest) -> PromptContext:
        return PromptContext(messages=request.messages)

    def _add_routes(self):
        @self.router.post(
            "/chat/completions",
            response_model=ChatCompletionResponse,
            description="Create a chat completion, optionally streamed"
        )
        async def create_chat_completion(
            request: ChatCompletionRequest,
        ):
            try:
                logger.info(f"Received chat completion request: model={request.model}, stream={request.stream}, messages={len(request.messages)}")

                if not request.model:
                    raise HTTPException(status_code=400, detail="Model is required")

                llm_adapter = LlmAdapterFactory.create_adapter(request.model)
                prompt_context = self._convert_to_prompt_context(request)

                if request.stream:
                    # Return streaming response
                    async def generate_stream():
                        async for chunk in llm_adapter.chat_stream(prompt_context):
                            if chunk.type == "message_delta" and chunk.content:
                                yield chunk.content

                    return StreamingResponse(
                        generate_stream(),
                        media_type="text/plain",
                        headers={
                            "Cache-Control": "no-cache",
                            "Connection": "keep-alive",
                            "Content-Type": "text/plain; charset=utf-8"
                        }
                    )
                else:
                    chunks = []
                    async for chunk in llm_adapter.chat_stream(prompt_context):
                        if chunk.type == "message_delta" and chunk.content:
                            chunks.append(chunk.content)

                    return ChatCompletionResponse(
                        id=str(uuid4()),
                        object="chat.completion",
                        created=int(datetime.now(timezone.utc).timestamp()),
                        model=request.model,
                        choices=[
                            ChatCompletionChoice(
                                index=0,
                                message=ChatMessage(
                                    role="assistant",
                                    content="".join(chunks)
                                ),
                                finish_reason="stop"
                            )
                        ],
                        usage=ChatCompletionUsage(
                            prompt_tokens=0,  # Replace with actual token count if available
                            completion_tokens=len(chunks),
                            total_tokens=len(chunks)
                        )
                    )

            except Exception as e:
                logger.error(f"Error in chat completion: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to complete chat: {str(e)}"
                )