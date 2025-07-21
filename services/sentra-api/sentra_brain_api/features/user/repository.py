from sqlalchemy.orm import Session
from sentra_brain_api.core.base_repository import BaseRepository
from sentra_brain_api.domain.user_entity import UserEntity
from sentra_brain_api.infra import postgres_service

class UserRepository(BaseRepository[UserEntity]):
    def __init__(self, db: Session):
        super().__init__(UserEntity, db)

    
    def get_by_username(self, username: str) -> UserEntity:
        return self.db.query(UserEntity).filter(UserEntity.username == username).first()

    def get_by_email(self, email: str) -> UserEntity:
        return self.db.query(UserEntity).filter(UserEntity.email == email).first()
