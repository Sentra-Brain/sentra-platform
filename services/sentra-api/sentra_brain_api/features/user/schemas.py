from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

from sentra_core.domain.entities.user_entity import UserEntity

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    
class UserModel(BaseModel):
    id: str | None = None  # UUID as string for frontend compatibility
    username: str
    email: EmailStr | None = None
    full_name: str | None = None
    disabled: bool | None = None
    roles: list[str] = []

    model_config = {
        "from_attributes": True
    }


class SignupModel(BaseModel):
    username: str
    email: EmailStr 
    full_name: str
    password: str 

    model_config = {
        "from_attributes": True
    }

class SignupResponse(BaseModel):
    user: UserModel
    message: str
    
    model_config = {
        "from_attributes": True
    }

class UserUpdate(BaseModel):
    password: str | None = None


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    job_title: Optional[str] = None
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    preferred_language: Optional[str] = None
    timezone: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: UUID
    username: str
    email: str
    full_name: Optional[str]
    job_title: Optional[str]
    avatar_url: Optional[str]
    phone_number: Optional[str]
    bio: Optional[str]
    preferred_language: str
    timezone: str
    roles: list[str]

    model_config = {
        "from_attributes": True
    }
