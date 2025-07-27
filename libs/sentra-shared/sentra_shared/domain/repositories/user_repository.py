from sqlalchemy.orm import Session
from sentra_shared.domain.repositories.base_repository import BaseRepository
from sentra_shared.domain.entities.user_entity import UserEntity

class UserRepository(BaseRepository[UserEntity]):
    def __init__(self, db: Session):
        super().__init__(UserEntity, db)

    
    def get_by_username(self, username: str) -> UserEntity:
        return self.db.query(UserEntity).filter(UserEntity.username == username).first()

    def get_by_email(self, email: str) -> UserEntity:
        return self.db.query(UserEntity).filter(UserEntity.email == email).first()
