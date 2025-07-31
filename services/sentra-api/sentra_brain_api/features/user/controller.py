# sentra_brain_api/features/user/controller.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_brain_api.features.user.schemas import SignupResponse, UserModel, SignupModel, UserUpdate
from sentra_core.domain.entities.user_entity import UserEntity
from sentra_core.infra.sql.postgres_service import get_db
from sentra_brain_api.features.user.mappers import to_user_model
from sentra_brain_api.features.user.constants import (
    SIGNUP_DESCRIPTION,
    ME_DESCRIPTION,
    UPDATE_USER_DESCRIPTION,
    VALIDATE_USER_DESCRIPTION
)
from sentra_brain_api.features.user.api_service import UserApiService
from sentra_core.core import logging

logger = logging.get_logger("sentra_brain_api")


class UserController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()
    
    def _add_routes(self):
        @self.router.post("/signup", response_model=SignupResponse, description=SIGNUP_DESCRIPTION)
        def signup(user: SignupModel, db: Session = Depends(get_db)):
            logger.info(f"Signup attempt for user: {user.username}")
            return UserApiService(db).signup(user)

        @self.router.get("/me", response_model=UserModel, description=ME_DESCRIPTION)
        def me(current_user: UserEntity = Depends(get_authenticated_user)):
            return to_user_model(current_user)

        @self.router.put("/{user_to_update_id}", response_model=UserModel, description=UPDATE_USER_DESCRIPTION)
        def update_user(
            user_to_update_id: UUID,
            user_update: UserUpdate,
            current_user: UserEntity = Depends(get_authenticated_user),
            db: Session = Depends(get_db)
        ):
            logger.info(f"Updating user {user_to_update_id} by {current_user.id}")
            return UserApiService(db).update_user(current_user.id, user_to_update_id, user_update)

        @self.router.get("/validate", response_model=UserModel, description=VALIDATE_USER_DESCRIPTION)
        def validate_user(token: str, db: Session = Depends(get_db)):
            logger.info(f"Validating user with token: {token}")
            return UserApiService(db).validate_user(token)

        @self.router.get("/{user_id}/display-name", response_model=str, description="Get a user's display name by ID.")
        def get_user_display_name(user_id: UUID, db: Session = Depends(get_db)):
            logger.info(f"Fetching display name for user: {user_id}")
            return UserApiService(db).get_user_display_name(user_id)
