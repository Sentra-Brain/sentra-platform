from fastapi import APIRouter, HTTPException, status, Depends
from sentra_brain_api.core.exceptions import SentraHTTPException
from sentra_brain_api.crosscutting.authorization import get_admin_user
from sentra_brain_api.features.user.models import UserModel
from sentra_shared.infra.sql.postgres_service import get_db
from sentra_shared.domain.repositories.user_repository  import UserRepository
from sentra_brain_api.features.admin.admin_service import AdminService
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger("admin")

class AdminController:
    def __init__(self):
        self.router = APIRouter(dependencies=[Depends(get_admin_user)])
        self.admin_service = AdminService(UserRepository)
        self._add_routes()

    def _add_routes(self):
        @self.router.get("/users", response_model=list[UserModel])
        def get_all_users(db: Session = Depends(get_db)):
            logger.info("an admin user is retrieving all users")
            try:
                users = self.admin_service.get_all_users(db)
                return [UserModel.model_validate(user, from_attributes=True) for user in users]
            except ValueError as e:
                raise SentraHTTPException(
                        status_code=400,
                        code="INVALID_REQUEST",
                        message=str(e),
                        path=f"/users/",
                        suggestion="Check request payload"
                    )

        @self.router.put("/users/{user_id}/enable", response_model=UserModel)
        def enable_user(user_id: int, db: Session = Depends(get_db)):
            logger.info(f"an admin user is enabling user {user_id}")
            try:
                enabled_user = self.admin_service.enable_user(user_id, db)
                return UserModel.model_validate(enabled_user, from_attributes=True)
            except ValueError as e:
                raise SentraHTTPException(
                    status_code=400,
                    code="INVALID_REQUEST",
                    message=str(e),
                    path=f"/users/{user_id}/enable",
                    suggestion="Check request payload"
                )

        @self.router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
        def delete_user(user_id: int, db: Session = Depends(get_db)):
            logger.info(f"An admin user is deleting user with id {user_id}")
            try:
                self.admin_service.delete_user(user_id, db)
            except ValueError as e:
                raise SentraHTTPException(
                    status_code=400,
                    code="INVALID_REQUEST",
                    message=str(e),
                    path=f"/users/{user_id}",
                    suggestion="Check request payload"
                )
