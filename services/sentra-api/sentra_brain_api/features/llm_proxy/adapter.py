# sentra_brain_api/features/llm_proxy/adapter.py

import json
import time
import uuid
from typing import AsyncGenerator, Dict, Any, Optional
import httpx
from sentra_brain_api.crosscutting import logging
from sentra_brain_api.core.config import settings
from sentra_brain_api.features.llm_proxy.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChunk
)

logger = logging.get_logger("llm_proxy")


class LlamaServerClient:
    def __init__(self, base_url: str = None):
        self.base_url = (base_url or settings.llama_server_url).rstrip("/")
        self.client = httpx.AsyncClient(timeout=300.0)  # 5 minute timeout
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def complete_chat(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Complete a chat request without streaming - forwards directly to llama-server"""
        
        # Forward the request directly as JSON to the llama-server /v1/chat/completions endpoint
        request_data = request.model_dump(exclude_none=True)
        
        try:
            logger.info(f"Forwarding request to llama-server at {self.base_url}/v1/chat/completions")
            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            # Return the response directly from llama-server as it should be OpenAI-compatible
            response_data = response.json()
            return ChatCompletionResponse(**response_data)
            
        except httpx.RequestError as e:
            logger.error(f"Request error calling llama-server: {e}")
            raise Exception(f"Failed to connect to llama-server: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from llama-server: {e.response.status_code} - {e.response.text}")
            raise Exception(f"llama-server returned error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error calling llama-server: {e}")
            raise Exception(f"Unexpected error: {e}")
    
    async def stream_chat(self, request: ChatCompletionRequest) -> AsyncGenerator[ChatCompletionChunk, None]:
        """Stream a chat completion response - forwards directly to llama-server"""
        
        # Forward the request directly as JSON to the llama-server /v1/chat/completions endpoint
        request_data = request.model_dump(exclude_none=True)
        
        try:
            logger.info(f"Streaming request to llama-server at {self.base_url}/v1/chat/completions")
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.strip():
                        # Skip the "data: " prefix if present (SSE format)
                        line_content = line.strip()
                        if line_content.startswith("data: "):
                            line_content = line_content[6:]  # Remove "data: " prefix
                        
                        # Handle special SSE messages
                        if line_content == "[DONE]":
                            break
                        
                        try:
                            chunk_data = json.loads(line_content)
                            chunk = ChatCompletionChunk(**chunk_data)
                            yield chunk
                                
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse JSON from llama-server: {line}")
                            continue
            
        except httpx.RequestError as e:
            logger.error(f"Request error during streaming from llama-server: {e}")
            raise Exception(f"Failed to connect to llama-server: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during streaming from llama-server: {e.response.status_code}")
            raise Exception(f"llama-server returned error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error during streaming from llama-server: {e}")
            raise Exception(f"Unexpected error: {e}")