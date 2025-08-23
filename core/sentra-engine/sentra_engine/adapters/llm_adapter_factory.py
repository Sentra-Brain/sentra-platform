from sentra_core.core.settings import settings, LLMEngine  # type: ignore
from sentra_engine.adapters.llama_server import LlamaServerAdapter
from sentra_engine.adapters.vllm import VLLMAdapter

class LlmAdapterFactory:
    """Factory for creating LLM adapter instances."""

    @staticmethod
    def create_adapter(model: str):
        """
        Create an LLM adapter instance based on the configured engine.

        Args:
            model: The model to use with the adapter.

        Returns:
            An instance of the appropriate LLM adapter.
        """
        if settings.llm_engine == LLMEngine.LLAMA:
            return LlamaServerAdapter(
                base_url=settings.llama_server_url,
                model=model,
                request_timeout=settings.llm_request_timeout,
            )
        elif settings.llm_engine == LLMEngine.VLLM:
            return VLLMAdapter(
                base_url=settings.vllm_server_url,
                model=model,
                request_timeout=settings.llm_request_timeout,
            )

        # Default to LlamaServerAdapter if engine is unknown
        raise ValueError(f"Unsupported LLM engine: {settings.llm_engine}")
