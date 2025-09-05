from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sentra.infra.sql.postgres_settings import settings
from sentra_brain_api.core.exceptions import SentraHTTPException
from sentra.shared.logging import get_logger
from sentra_brain_api.features.auth.auth_service import AuthService
from sentra_brain_api.features.auth.models import Token, RefreshTokenRequest, AccessToken
from sentra.domain.repository.user_repository  import UserRepository
from sentra.infra.sql.postgres_service import get_db

logger = get_logger(__name__)

class AuthController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()
        
    def _add_routes(self):
        @self.router.post("/token", response_model=Token)
        async def authenticate(
            form_data: OAuth2PasswordRequestForm = Depends(),
            db: Session = Depends(get_db)
            ):
            user_repo = UserRepository(db)
            auth_service = AuthService(user_repo)
            logger.info(f"Logging in user: {form_data.username}")
            user = auth_service.authenticate_user(form_data.username, form_data.password)
            if not user:
                raise SentraHTTPException(
                        status_code=401,
                        code="AUTH_FAILED",
                        message="Incorrect username or password",
                        path="/auth/token",
                        suggestion="Check your credentials",
                    )
            access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
            access_token = auth_service.create_access_token(
                data={"sub": user.username, "roles": user.roles},
                expires_delta=access_token_expires
            )
            refresh_token = auth_service.create_refresh_token(
                data={"sub": user.username, "roles": user.roles}
            )
            return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

        @self.router.post("/refresh", response_model=AccessToken)
        async def refresh_access_token(
            request: RefreshTokenRequest,
            db: Session = Depends(get_db)
        ):
            user_repo = UserRepository(db)
            auth_service = AuthService(user_repo)
            logger.info("Refreshing access token")
            
            user = auth_service.validate_refresh_token(request.refresh_token)
            if not user:
                raise SentraHTTPException(
                    status_code=401,
                    code="INVALID_REFRESH_TOKEN",
                    message="Invalid or expired refresh token",
                    path="/auth/refresh",
                    suggestion="Please log in again",
                )
            
            access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
            access_token = auth_service.create_access_token(
                data={"sub": user.username, "roles": user.roles},
                expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}
