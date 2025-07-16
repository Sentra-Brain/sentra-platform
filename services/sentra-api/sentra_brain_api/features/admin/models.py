from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    role: str

class Role(BaseModel):
    name: str
    description: str

class Slot(BaseModel):
    id: int
    name: str
    assigned_to: int | None
