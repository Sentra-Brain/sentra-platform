# sentra_brain_api/features/user/user_service.py

from uuid import UUID
from fastapi import HTTPException, status
from sentra_brain_api.core.exceptions import SentraHTTPException
from sentra_brain_api.features.auth.auth_service import AuthService
from sentra_brain_api.features.user.models import SignupResponse, UserModel
from sentra_shared.core import logging
from sentra_shared.infra.notifications.notification_service import NotificationService
from sentra_shared.domain.services.user_service import UserService
from sqlalchemy.orm import Session
import asyncio
import os

logger = logging.get_logger("sentra_brain_api")


class UserApiService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def signup(self, user_data) -> SignupResponse:
        user_count = self.user_service.count_non_superadmin_users()
        max_users = self.user_service.get_max_user_limit()

        if max_users != -1 and user_count >= max_users:
            raise SentraHTTPException(
                status_code=403,
                code="USER_LIMIT_REACHED",
                message="User limit reached",
                path="/users/signup",
                suggestion="Upgrade your license or contact support"
            )

        auth_service = AuthService(self.user_service.user_repo)
        hashed = auth_service.get_password_hash(user_data.password)

        user = self.user_service.create_user(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed
        )

        try:
            verification_token = auth_service.create_verification_token(user.id)
            base_url = os.getenv("BASE_URL", "http://localhost:8100")
            verification_url = f"{base_url}/user/validate?token={verification_token}"

            smtp_service = NotificationService.from_env_vars()
            email_sent = asyncio.run(smtp_service.send_email_verification(user.email, verification_url))

            message = (
                "A verification email has been sent. Please check your inbox."
                if email_sent else
                "Your account has been created."
            )

            return SignupResponse(
                user=UserModel.model_validate(user, from_attributes=True),
                message=message
            )

        except Exception as e:
            logger.error(f"Error during signup: {str(e)}")
            raise SentraHTTPException(
                status_code=400,
                code="SIGNUP_FAILED",
                message=str(e),
                path="/users/signup",
                suggestion="Try again later or contact support"
            )

    def validate_user(self, token: str) -> UserModel:
        try:
            auth_service = AuthService(self.user_service.user_repo)
            payload = auth_service.decode_verification_token(token)
            user_id = payload.get("user_id")
            if not user_id:
                raise SentraHTTPException(
                    status_code=400,
                    code="INVALID_TOKEN",
                    message="Token missing user ID",
                    path="/users/validate",
                    suggestion="Request new verification email"
                )

            user = self.user_service.enable_user(user_id)
            if not user:
                raise SentraHTTPException(
                    status_code=404,
                    code="USER_NOT_FOUND",
                    message="User not found",
                    path="/users/validate",
                    suggestion="Check your signup link"
                )

            return UserModel.model_validate(user, from_attributes=True)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating user: {str(e)}")
            raise SentraHTTPException(
                status_code=400,
                code="INVALID_TOKEN",
                message=str(e),
                path="/users/validate",
                suggestion="Check token or contact support"
            )

    def update_user(self, current_user_id: UUID, user_id: UUID, user_update) -> UserModel:
        # Add permission checks if needed
        hashed_password = AuthService.get_password_hash(user_update.password) if user_update.password else None
        user = self.user_service.update_user(
            user_id=user_id,
            full_name=user_update.full_name,
            email=user_update.email,
            hashed_password=hashed_password
        )
        if not user:
            raise SentraHTTPException(
                status_code=404,
                code="USER_NOT_FOUND",
                message=f"User {user_id} not found",
                path=f"/users/{user_id}",
                suggestion="Check user ID or contact support"
            )
        return UserModel.model_validate(user, from_attributes=True)

    def get_user_display_name(self, user_id: UUID) -> str:
        return self.user_service.get_user_display_name(user_id)
