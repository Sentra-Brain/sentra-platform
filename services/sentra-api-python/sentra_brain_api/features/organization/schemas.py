from pydantic import BaseModel
from typing import Optional


class OrganizationResponse(BaseModel):
    name: str
    slug: str
    description: Optional[str]
    location: Optional[str]
    contact_email: Optional[str]

    model_config = {
        "from_attributes": True
    }


class OrganizationUpdateRequest(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    contact_email: Optional[str] = None