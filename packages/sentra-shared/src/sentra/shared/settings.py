# packages/sentra-shared/src/sentra/shared/settings.py
from enum import Enum
from typing import Any
from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sentra.shared.logging import get_logger

logger = get_logger(__name__)


class LLMEngine(str, Enum):
	VLLM = "vllm"
	LLAMA = "llama"  # llama-server
	DMR = "dmr"  # DMR server

class SentraSettings(BaseSettings):
	# ---- LLM backend selection ----
	llm_engine: LLMEngine = Field(
		default=LLMEngine.VLLM, json_schema_extra={"env": "LLM_ENGINE"}
	)
	
	# ---- LLM server settings ----
	# OpenAI compatible server URL (like DMR)
	openai_api_base: str = Field(
		default="http://localhost:12434/engines/llama.cpp/v1", json_schema_extra={"env": "OPEN_API_BASE"}
	)
	openai_api_key: str = Field(
		default="", json_schema_extra={"env": "OPEN_API_KEY"}
	)
	model_id: str = Field(
		default="ai/gpt-oss:latest", json_schema_extra={"env": "MODEL_ID"}
	)

	# VLLM server settings
	vllm_server_url: str = Field(
		default="http://vllm:8000", json_schema_extra={"env": "VLLM_SERVER_URL"}
	)
	vllm_model: str = Field(
		default="hosted_vllm//models/meta-llama--Llama-3.1-8B-Instruct",
		json_schema_extra={"env": "VLLM_MODEL"},
	)

	# Llama-server settings
	llama_server_url: str = Field(
		default="http://llama_server:8080",
		json_schema_extra={"env": "LLAMA_SERVER_URL"},
	)
	llm_request_timeout: float | None = Field(
		default=None, json_schema_extra={"env": "LLM_REQUEST_TIMEOUT"}
	)

	# ---- Knowledge settings ----
	knowledge_mount_path: str = Field(
		default="/mnt/sentra_knowledge",
		json_schema_extra={"env": "KNOWLEDGE_MOUNT_PATH"},
	)
	persist_markdown: bool = Field(
		default=True, json_schema_extra={"env": "PERSIST_MARKDOWN"}
	)
	max_markdown_bytes: int = Field(
		default=5_000_000, json_schema_extra={"env": "MAX_MARKDOWN_BYTES"}
	)
	derived_dir_name: str = Field(
		default=".derived", json_schema_extra={"env": "DERIVED_DIR_NAME"}
	)

	# ---- Tools / MCP (NEW) ----
	tools_enabled: bool = Field(
		default=False, json_schema_extra={"env": "SENTRA_TOOLS_ENABLED"}
	)
	mcp_base_url: str = Field(
		default="http://sentra-mcp:8200", json_schema_extra={"env": "MCP_BASE_URL"}
	)
	tool_max_output_bytes: int = Field(
		default=8192, json_schema_extra={"env": "TOOL_MAX_OUTPUT_BYTES"}
	)
	mcp_timeout: float | None = Field(
		default=None, json_schema_extra={"env": "MCP_TIMEOUT"}
	)  # ADD

	# ---- ADK-specific config ----
	adk_token_budget: int = Field(
		default=3000, json_schema_extra={"env": "ADK_TOKEN_BUDGET"}
	)
	enable_rag: bool = Field(default=True, json_schema_extra={"env": "ENABLE_RAG"})
	max_tool_rounds: int = Field(
		default=2, json_schema_extra={"env": "MAX_TOOL_ROUNDS"}
	)

	# ---- RAG server ----
	rag_server_url: str = Field(
		default="http://Sentra.Rag.Server:9100",
		json_schema_extra={"env": "RAG_SERVER_URL"},
	)

	# ---- Vertical defaults ----
	default_vertical: str = Field(
		default="legal", json_schema_extra={"env": "DEFAULT_VERTICAL"}
	)

	model_config = SettingsConfigDict(env_file=".env", extra="allow")

	@field_validator("llm_engine", mode="before")
	@classmethod
	def _normalize_llm_engine(cls, v: Any) -> Any:
		if isinstance(v, str):
			v = v.lower()
			if v in ("vllm", "vllm_engine"):
				return LLMEngine.VLLM
			if v in ("llama", "llama-server", "llama_server"):
				return LLMEngine.LLAMA
		return v

try:
    settings = SentraSettings()
except ValidationError as e:
    error_details = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
    logger.error(f"Configuration error: {error_details}")
    raise