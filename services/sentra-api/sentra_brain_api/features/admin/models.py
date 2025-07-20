# features/admin/models.py

from pydantic import BaseModel

class SystemSettingsModel(BaseModel):
    max_users: int

    model_config = {
        "from_attributes": True
    }