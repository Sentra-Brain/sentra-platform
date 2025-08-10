from sentra_brain_api.core.exceptions import SentraHTTPException
from sentra_core.domain.repository.user_repository import UserRepository
from sentra_core.core.logging import get_logger
from sqlalchemy.orm import Session
from uuid import UUID

logger = get_logger(__name__)

class AdminService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def delete_user(self, user_id: UUID, db: Session) -> None:
        logger.info(f"Deleting user with id: {user_id}")
        self.user_repository = UserRepository(db)
        try:
            self.user_repository.delete(user_id)
        except Exception as e:
            logger.error(f"Error deleting user with id {user_id}: {str(e)}")
            raise SentraHTTPException(
                status_code=400,
                code="DELETE_FAILED",
                message="Could not delete user",
                details=str(e),
                path=f"/admin/users/{user_id}",
                suggestion="Ensure the user exists and is not referenced elsewhere"
            )       
            
    def enable_user(self, user_id: UUID, db: Session):
        self.user_repository = UserRepository(db)
        user = self.user_repository.get(user_id)
        if not user:
            raise SentraHTTPException(
                status_code=404,
                code="USER_NOT_FOUND",
                message=f"User with id {user_id} not found",
                path=f"/admin/users/{user_id}",
                suggestion="Check if the user ID is correct"
            )
        if not user.disabled:
            raise SentraHTTPException(
                status_code=400,
                code="USER_ALREADY_ENABLED",
                message=f"User with id {user_id} is already enabled",
                path=f"/admin/users/{user_id}/enable",
                suggestion="No action needed, user is already active"
            )
        user.disabled = False
        self.user_repository.update(user)
        logger.info(f"User {user.username} has been enabled.")
        return user

    def get_all_users(self, db: Session):
        self.user_repository = UserRepository(db)
        users = self.user_repository.get_all()
        if not users:
            raise SentraHTTPException(
                status_code=404,
                code="NO_USERS_FOUND",
                message="No users found in the system",
                path="/admin/users",
                suggestion="Ensure there are users created in the system"
            )
        return users
