from enum import Enum
from typing import Optional
from .base import LLMClient
from .vllm_client import VLLMClient
from .llama_server_client import LlamaServerClient
from sentra_core.core.settings import LLMEngine
from sentra_core.core.logging import get_logger

logger = get_logger(__name__)

def build_llm_client(
    *,
    engine: LLMEngine,
    vllm_url: str,
    llama_url: str,
    request_timeout: Optional[float] = None,
) -> LLMClient:
    """
    Creates an LLM client based on the specified engine type.
    """
    if engine == LLMEngine.VLLM:
        logger.info(f"Using VLLM client with URL: {vllm_url}")
        return VLLMClient(base_url=vllm_url, request_timeout=request_timeout)
    if engine == LLMEngine.LLAMA:
        logger.info(f"Using LLAMA client with URL: {llama_url}")
        return LlamaServerClient(base_url=llama_url, request_timeout=request_timeout)
    raise ValueError(f"Unknown LLM engine: {engine}")
