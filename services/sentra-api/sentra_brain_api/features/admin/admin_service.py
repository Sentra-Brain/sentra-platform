from sentra_brain_api.features.user.repository import UserRepository
from sentra_brain_api.crosscutting.logging import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__name__)

class AdminService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def delete_user(self, user_id: int, db: Session) -> None:
        logger.info(f"Deleting user with id: {user_id}")
        user_repo = self.user_repository(db)
        try:
            user_repo.delete(user_id)
        except Exception as e:
            raise ValueError(f"Error deleting user: {str(e)}")

    def enable_user(self, user_id: int, db: Session):
        user_repo = self.user_repository(db)
        user = user_repo.get(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        if not user.disabled:
            raise ValueError(f"User with id {user_id} is already enabled")
        user.disabled = False
        user_repo.update(user)
        logger.info(f"User {user.username} has been enabled.")
        return user

    def get_all_users(self, db: Session):
        user_repo = self.user_repository(db)
        users = user_repo.get_all()
        if not users:
            raise ValueError("No users found")
        return users
