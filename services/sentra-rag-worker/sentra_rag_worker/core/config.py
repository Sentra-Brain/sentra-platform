from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from sentra_core import logging

logger = logging.get_logger(__name__)

load_dotenv()


class Settings(BaseSettings):
    # PostgreSQL (same as sentra-api)
    database_url: str = Field(..., json_schema_extra={"env": "DATABASE_URL"})

    # RabbitMQ
    rabbitmq_host: str = Field(default="rabbitmq", json_schema_extra={"env": "RABBITMQ_HOST"})
    rabbitmq_port: int = Field(default=5672, json_schema_extra={"env": "RABBITMQ_PORT"})
    rabbitmq_user: str = Field(default="sentra", json_schema_extra={"env": "RABBITMQ_USER"})
    rabbitmq_password: str = Field(default="sentra", json_schema_extra={"env": "RABBITMQ_PASSWORD"})
    rabbitmq_queue: str = Field(default="indexation_queue", json_schema_extra={"env": "RABBITMQ_QUEUE"})

    # ChromaDB
    chroma_url: str = Field(default="http://chroma:8000", json_schema_extra={"env": "CHROMA_URL"})

    # Knowledge processing
    knowledge_root: str = Field(default="/mnt/sentra_knowledge", json_schema_extra={"env": "KNOWLEDGE_ROOT"})
    folder_scan_interval: int = Field(default=60, json_schema_extra={"env": "FOLDER_SCAN_INTERVAL"})
    
    # Embedding model
    embedding_model: str = Field(default="BAAI/bge-base-en-v1.5", json_schema_extra={"env": "EMBEDDING_MODEL"})
    
    # Chunking settings
    chunk_size: int = Field(default=1000, json_schema_extra={"env": "CHUNK_SIZE"})
    chunk_overlap: int = Field(default=200, json_schema_extra={"env": "CHUNK_OVERLAP"})

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )

settings = Settings()