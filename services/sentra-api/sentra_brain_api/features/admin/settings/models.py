# features/admin/models.py
from pydantic import BaseModel

class SystemSettingsModel(BaseModel):
    id: int
    workspace_name: str
    license_type: str
    maintenance_mode: bool
    default_language: str
    log_retention_days: int
    max_users: int

    model_config = {
        "from_attributes": True
    }

    