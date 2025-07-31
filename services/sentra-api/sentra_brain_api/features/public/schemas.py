# features/public/models.py
from pydantic import BaseModel

class PublicSettingsResponse(BaseModel):
    workspace_name: str
    max_users: int
    available_slots: int
