# features/admin/models.py
from pydantic import BaseModel

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

    