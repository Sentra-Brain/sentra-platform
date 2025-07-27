from pydantic import BaseModel, EmailStr

from sentra_shared.domain.entities.user_entity import UserEntity

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

    @classmethod
    def from_entity(cls, user: UserEntity) -> "UserModel":
        return cls(
            id=str(user.id) if user.id else None,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            disabled=user.disabled,
            roles=user.get_roles() if hasattr(user, "get_roles") else []
        )


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

class UserUpdate(UserModel):
    password: str | None = None
