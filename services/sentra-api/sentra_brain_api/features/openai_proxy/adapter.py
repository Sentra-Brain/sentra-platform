# sentra_brain_api/features/openai_proxy/adapter.py

import json
import time
import uuid
from typing import AsyncGenerator, Dict, Any, Optional
import httpx
from sentra_brain_api.crosscutting import logging
from sentra_brain_api.features.openai_proxy.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatCompletionUsage,
    ChatMessage,
    ChatCompletionChunk
)

logger = logging.get_logger("openai_proxy")


class LlamaServerClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=300.0)  # 5 minute timeout
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def _convert_messages_to_prompt(self, messages: list[ChatMessage]) -> str:
        """Convert OpenAI messages format to a simple prompt for llama-server"""
        prompt_parts = []
        
        for message in messages:
            if message.role == "system":
                prompt_parts.append(f"System: {message.content}")
            elif message.role == "user":
                prompt_parts.append(f"User: {message.content}")
            elif message.role == "assistant":
                prompt_parts.append(f"Assistant: {message.content}")
        
        # Add the assistant prompt at the end
        prompt_parts.append("Assistant:")
        
        return "\n".join(prompt_parts)
    
    async def complete_chat(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Complete a chat request without streaming"""
        prompt = self._convert_messages_to_prompt(request.messages)
        
        # Prepare request for llama-server (Ollama API format)
        llama_request = {
            "model": request.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature or 1.0,
                "top_p": request.top_p or 1.0,
            }
        }
        
        if request.max_tokens:
            llama_request["options"]["num_predict"] = request.max_tokens
        
        try:
            logger.info(f"Sending request to llama-server at {self.base_url}/api/generate")
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=llama_request,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            llama_response = response.json()
            
            # Extract response text
            response_text = llama_response.get("response", "")
            
            # Create OpenAI-compatible response
            completion_id = f"chatcmpl-{uuid.uuid4().hex[:29]}"
            created = int(time.time())
            
            # Calculate usage (approximate since llama-server may not provide exact counts)
            prompt_tokens = len(prompt.split()) * 1.3  # Rough estimate
            completion_tokens = len(response_text.split()) * 1.3  # Rough estimate
            
            choice = ChatCompletionChoice(
                index=0,
                message=ChatMessage(role="assistant", content=response_text),
                finish_reason="stop"
            )
            
            usage = ChatCompletionUsage(
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
                total_tokens=int(prompt_tokens + completion_tokens)
            )
            
            return ChatCompletionResponse(
                id=completion_id,
                created=created,
                model=request.model,
                choices=[choice],
                usage=usage
            )
            
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
        """Stream a chat completion response"""
        prompt = self._convert_messages_to_prompt(request.messages)
        
        # Prepare request for llama-server (Ollama API format)
        llama_request = {
            "model": request.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": request.temperature or 1.0,
                "top_p": request.top_p or 1.0,
            }
        }
        
        if request.max_tokens:
            llama_request["options"]["num_predict"] = request.max_tokens
        
        try:
            logger.info(f"Streaming request to llama-server at {self.base_url}/api/generate")
            
            completion_id = f"chatcmpl-{uuid.uuid4().hex[:29]}"
            created = int(time.time())
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=llama_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            chunk_data = json.loads(line)
                            content = chunk_data.get("response", "")
                            done = chunk_data.get("done", False)
                            
                            if content:
                                # Create streaming chunk
                                chunk = ChatCompletionChunk(
                                    id=completion_id,
                                    created=created,
                                    model=request.model,
                                    choices=[{
                                        "index": 0,
                                        "delta": {"content": content},
                                        "finish_reason": None
                                    }]
                                )
                                yield chunk
                            
                            if done:
                                # Send final chunk
                                final_chunk = ChatCompletionChunk(
                                    id=completion_id,
                                    created=created,
                                    model=request.model,
                                    choices=[{
                                        "index": 0,
                                        "delta": {},
                                        "finish_reason": "stop"
                                    }]
                                )
                                yield final_chunk
                                break
                                
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