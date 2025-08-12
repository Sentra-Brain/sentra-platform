# sentra_brain_api/core/settings.py
from enum import Enum
from typing import Any
from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sentra_core.core.logging import get_logger

logger = get_logger(__name__)

class LLMEngine(str, Enum):
    VLLM = "vllm"
    LLAMA = "llama"  # llama-server

class SentraSettings(BaseSettings):
    # ---- LLM backend selection ----
    llm_engine: LLMEngine = Field(default=LLMEngine.VLLM, json_schema_extra={"env": "LLM_ENGINE"})
    vllm_server_url: str = Field(default="http://vllm:8000", json_schema_extra={"env": "VLLM_SERVER_URL"})
    llama_server_url: str = Field(default="http://llama_server:8080", json_schema_extra={"env": "LLAMA_SERVER_URL"})
    llm_request_timeout: float | None = Field(default=None, json_schema_extra={"env": "LLM_REQUEST_TIMEOUT"})  # seconds, None = unlimited

    # ---- Other settings you already had ----
    knowledge_mount_path: str = Field(default="/mnt/sentra_knowledge", json_schema_extra={"env": "KNOWLEDGE_MOUNT_PATH"})

    # Pydantic Settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )

    @field_validator("llm_engine", mode="before")
    @classmethod
    def _normalize_llm_engine(cls, v: Any) -> Any:
        # Permite LLM_ENGINE=vLlM / LLAMA / etc. (case-insensitive)
        if isinstance(v, str):
            v = v.strip().lower()
            if v == "vllm":
                return LLMEngine.VLLM
            if v in ("llama", "llama_server", "llama-server"):
                return LLMEngine.LLAMA
        return v

try:  # Validate settings on import
    settings = SentraSettings()
except ValidationError as e:
    error_details = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
    logger.error(f"Configuration error: {error_details}")
    raise
