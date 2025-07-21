# features/public/models.py
from pydantic import BaseModel

class PublicSettingsModel(BaseModel):
    workspace_name: str
    max_users: int
    available_slots: int
