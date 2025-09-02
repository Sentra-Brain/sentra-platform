"""Service-level settings for Sentra API."""

from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EngineMode(str, Enum):
    """Selectable conversation engine backends."""

    LEGACY = "legacy"
    ADK = "adk"


class Settings(BaseSettings):
    """Runtime configuration for the API service."""

    engine_mode: EngineMode = Field(
        default=EngineMode.LEGACY, json_schema_extra={"env": "ENGINE_MODE"}
    )

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()

