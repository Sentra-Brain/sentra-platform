from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    id: int | None = None
    username: str
    email: EmailStr | None = None
    full_name: str | None = None
    disabled: bool | None = None
    roles: list[str] = []

    model_config = {
        "from_attributes": True
    }
        
    @classmethod
    def model_validate(cls, obj, **kwargs):
        data = obj.__dict__.copy()
        data["roles"] = obj.get_roles() if hasattr(obj, "get_roles") else []
        return super().model_validate(data, **kwargs)


class SignupModel(BaseModel):
    username: str
    email: EmailStr 
    full_name: str
    password: str 

    model_config = {
        "from_attributes": True
    }

class SignupResponse(BaseModel):
    user: User
    message: str
    
    model_config = {
        "from_attributes": True
    }

class UserUpdate(User):
    password: str | None = None
