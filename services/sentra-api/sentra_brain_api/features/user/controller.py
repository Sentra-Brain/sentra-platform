from fastapi import APIRouter, Depends
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sqlalchemy.orm import Session
from sentra_brain_api.domain.user_entity import UserEntity
from sentra_brain_api.features.user.models import SignupResponse, UserModel, SignupModel, UserUpdate
from sentra_brain_api.infra.postgres_service import get_db
from sentra_brain_api.features.user.constants import (
    SIGNUP_DESCRIPTION,
    ME_DESCRIPTION,
    UPDATE_USER_DESCRIPTION,
    VALIDATE_USER_DESCRIPTION
)
from sentra_brain_api.features.user.repository import UserRepository
from sentra_brain_api.features.user.user_service import UserService
from sentra_brain_api.crosscutting import logging

logger = logging.get_logger("sentra_brain_api")

class UserController:
    def __init__(self):
        self.router = APIRouter()
        self.user_service = UserService(UserRepository)
        self._add_routes()

    def _add_routes(self):
        @self.router.post("/signup", response_model=SignupResponse, description=SIGNUP_DESCRIPTION)
        def signup(user: SignupModel, db: Session = Depends(get_db)):
            logger.info(f"Signup attempt for user: {user.username}")
            return self.user_service.signup(user, db)
        
        @self.router.get("/me", response_model=UserModel, description=ME_DESCRIPTION)
        def me(current_user: UserEntity = Depends(get_authenticated_user)):
            return UserModel.from_entity(current_user)
    
        @self.router.put("/{user_to_update_id}", response_model=UserModel, description=UPDATE_USER_DESCRIPTION)
        def update_user(user_to_update_id: str, user_update: UserUpdate, current_user: UserEntity = Depends(get_authenticated_user), db: Session = Depends(get_db)):
            logger.info(f"Updating user {user_to_update_id} by {current_user.id}")
            return self.user_service.update_user(current_user.id, user_to_update_id, user_update, db)

        @self.router.get("/validate", response_model=UserModel, description=VALIDATE_USER_DESCRIPTION)
        def validate_user(token: str, db: Session = Depends(get_db)):
            logger.info(f"Validating user with token: {token}")
            return self.user_service.validate_user(token, db)