from fastapi import APIRouter, Depends, HTTPException, status
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sqlalchemy.orm import Session
from sentra_brain_api.features.user.models import SignupResponse, User, SignupModel, UserUpdate
from sentra_brain_api.infra.postgres_service import get_db
from sentra_brain_api.features.user.constants import (
    SIGNUP_DESCRIPTION,
    ME_DESCRIPTION,
    UPDATE_USER_DESCRIPTION,
    VALIDATE_USER_DESCRIPTION
)
from sentra_brain_api.features.user.repository import UserRepository
from sentra_brain_api.features.user.user_service import UserService

class UserController:
    def __init__(self):
        self.router = APIRouter()
        self.user_service = UserService(UserRepository)
        self._add_routes()

    def _add_routes(self):
        @self.router.post("/signup", response_model=SignupResponse, description=SIGNUP_DESCRIPTION)
        def signup(user: SignupModel, db: Session = Depends(get_db)):
            try:
                return self.user_service.signup(user, db)
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        @self.router.get("/me", response_model=User, description=ME_DESCRIPTION)
        def me(current_user: User = Depends(get_authenticated_user)):
            return User.model_validate(current_user)
    
        @self.router.put("/{user_to_update_id}", response_model=User, description=UPDATE_USER_DESCRIPTION)
        def update_user(user_to_update_id: int, user_update: UserUpdate, current_user: User = Depends(get_authenticated_user), db: Session = Depends(get_db)):
            try:
                return self.user_service.update_user(current_user.id, user_to_update_id, user_update, db)
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        @self.router.get("/validate", response_model=User, description=VALIDATE_USER_DESCRIPTION)
        def validate_user(token: str, db: Session = Depends(get_db)):
            try:
                return self.user_service.validate_user(token, db)
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))