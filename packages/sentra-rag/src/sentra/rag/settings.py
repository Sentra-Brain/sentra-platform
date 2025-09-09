# packages/sentra-rag/src/sentra/rag/settings.py
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class RAGSettings(BaseSettings):
    # Chroma v2 settings
    chroma_url: str = Field(default="http://chroma:8000", json_schema_extra={"env": "CHROMA_URL"})
    chroma_tenant: str = Field(default="default_tenant", json_schema_extra={"env": "CHROMA_TENANT"})
    chroma_database: str = Field(default="default", json_schema_extra={"env": "CHROMA_DATABASE"})
    collection_name: str = Field(default="document_chunks", json_schema_extra={"env": "CHROMA_COLLECTION_NAME"})
    vector_store_mode: str = Field(default="http", json_schema_extra={"env": "VECTOR_STORE_MODE"})

    # Embedding settings
    embedding_model: str = Field(default="BAAI/bge-base-en-v1.5", json_schema_extra={"env": "EMBEDDING_MODEL"})
    
    # Chunking settings
    chunk_size: int = Field(default=1000, json_schema_extra={"env": "CHUNK_SIZE"})
    chunk_overlap: int = Field(default=200, json_schema_extra={"env": "CHUNK_OVERLAP"})
    
    # RAG query settings
    max_context_tokens: int = Field(default=4000, json_schema_extra={"env": "MAX_CONTEXT_TOKENS"})
    default_search_limit: int = Field(default=10, json_schema_extra={"env": "DEFAULT_SEARCH_LIMIT"})

    # Characters per token approximation
    tokens_per_character: int = Field(default=4, json_schema_extra={"env": "CHARACTERS_PER_TOKEN_APPROX"})

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )


try:  # Validate settings on import
    rag_settings = RAGSettings()
except ValidationError as e:
    error_details = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
    raise RuntimeError(f"RAG configuration error: {error_details}")
