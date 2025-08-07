# sentra_brain_api/features/settings/schemas.py

from pydantic import BaseModel
from typing import Optional


class SystemSettingsResponse(BaseModel):
    id: str
    workspace_name: str
    license_type: str
    maintenance_mode: bool
    default_language: str
    log_retention_days: int
    max_users: int
    enable_web_search: bool
    web_search_region: str
    max_web_results: int
    cache_results: bool
    cache_expiration_hours: int
    context_limit_chars: int
    default_timezone: str

    model_config = {
        "from_attributes": True
    }


class SystemSettingsUpdateRequest(BaseModel):
    workspace_name: Optional[str] = None
    license_type: Optional[str] = None
    maintenance_mode: Optional[bool] = None
    default_language: Optional[str] = None
    log_retention_days: Optional[int] = None
    max_users: Optional[int] = None
    enable_web_search: Optional[bool] = None
    web_search_region: Optional[str] = None
    max_web_results: Optional[int] = None
    cache_results: Optional[bool] = None
    cache_expiration_hours: Optional[int] = None
    context_limit_chars: Optional[int] = None
    default_timezone: Optional[str] = None


class ChatSettingsResponse(BaseModel):
    id: str
    max_tokens: int
    temperature: float
    top_p: float
    top_k: int
    system_prompt: str
    stop_sequences: str

    model_config = {
        "from_attributes": True
    }


class ChatSettingsUpdateRequest(BaseModel):
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    system_prompt: Optional[str] = None
    stop_sequences: Optional[str] = None