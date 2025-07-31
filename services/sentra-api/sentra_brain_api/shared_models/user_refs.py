# sentra_brain_api/shared_models/user_refs.py

from uuid import UUID
from pydantic import BaseModel, Field

class UserRef(BaseModel):
    id: UUID = Field(..., description="User ID")
    full_name: str = Field(..., description="User's display name")

    model_config = {
        "from_attributes": True
    }
