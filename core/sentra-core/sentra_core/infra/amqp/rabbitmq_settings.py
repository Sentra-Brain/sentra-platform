from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, ValidationError
from sentra_core.logging import get_logger

logger = get_logger(__name__)

class RabbitMQSettings(BaseSettings):
    rabbitmq_host: str = Field(default="rabbitmq", json_schema_extra={"env": "RABBITMQ_HOST"})
    rabbitmq_port: int = Field(default=5672, json_schema_extra={"env": "RABBITMQ_PORT"})
    rabbitmq_user: str = Field(default="sentra", json_schema_extra={"env": "RABBITMQ_USER"})
    rabbitmq_password: str = Field(default="sentra", json_schema_extra={"env": "RABBITMQ_PASSWORD"})
    rabbitmq_queue: str = Field(default="indexation_queue", json_schema_extra={"env": "RABBITMQ_QUEUE"})

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )

try: # Validate settings on import
    settings = RabbitMQSettings()  
except ValidationError as e:
    error_details = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
    logger.error(f"Configuration error: {error_details}")
    raise
