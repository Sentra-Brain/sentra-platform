from typing import List
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from sentra_brain_api.domain.base_entity import BaseEntity
from sentra_brain_api.domain.role import Role

class UserEntity(BaseEntity):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
    roles = Column(String)  # Roles stored as comma-separated string

    # questions = relationship("QuestionEntity", back_populates="user")
    # answers = relationship("AnswerEntity", back_populates="user")

    def get_roles(self) -> List[Role]:
        return [Role(role) for role in self.roles.split(",")]

    def set_roles(self, roles: List[Role]) -> None:
        self.roles = ",".join([role.value for role in roles])
