# sentra_brain_api/features/llm_proxy/controller.py

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sentra_core.core import logging
from sentra_brain_api.features.llm_proxy.models import (
    ChatCompletionRequest,
    ChatCompletionResponse
)
from sentra_brain_api.features.llm_proxy.adapter import VLLMServerClient
import json

logger = logging.get_logger("llm_proxy")


def get_vllm_client() -> VLLMServerClient:
    """Dependency function to get VLLMServerClient instance"""
    return VLLMServerClient()


class LLMProxyController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()
    
    def _add_routes(self):
        @self.router.post(
            "/chat/completions",
            response_model=ChatCompletionResponse,
            description="Create a chat completion, optionally streamed"
        )
        async def create_chat_completion(
            request: ChatCompletionRequest,
            vllm_client: VLLMServerClient = Depends(get_vllm_client)
        ):
            try:
                logger.info(f"Received chat completion request: model={request.model}, stream={request.stream}, messages={len(request.messages)}")
                
                if request.stream:
                    # Return streaming response
                    async def generate_stream():
                        try:
                            async for chunk in vllm_client.stream_chat(request):
                                chunk_json = chunk.model_dump_json()
                                yield f"data: {chunk_json}\n\n"
                            yield "data: [DONE]\n\n"
                        except Exception as e:
                            logger.error(f"Error during streaming: {e}")
                            error_data = {
                                "error": {
                                    "message": str(e),
                                    "type": "server_error"
                                }
                            }
                            yield f"data: {json.dumps(error_data)}\n\n"
                        finally:
                            await vllm_client.close()
                    
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
                    # Return regular response
                    try:
                        response = await vllm_client.complete_chat(request)
                        logger.info(f"Chat completion successful: {response.id}")
                        return response
                    finally:
                        await vllm_client.close()
                        
            except Exception as e:
                logger.error(f"Error in chat completion: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to complete chat: {str(e)}"
                )