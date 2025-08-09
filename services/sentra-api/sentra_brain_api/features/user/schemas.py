
from pydantic import BaseModel, EmailStr
from uuid import UUID

from sentra_core.domain.entities.user_entity import UserEntity

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    
class UserModel(BaseModel):
    id: UUID | None = None
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
