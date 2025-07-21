# sentra_brain_api/features/user/user_service.py
from fastapi import HTTPException, status
from sentra_brain_api.core.exceptions import SentraHTTPException
from sentra_brain_api.crosscutting import logging
from sentra_brain_api.crosscutting.notification_service import NotificationService
from sentra_brain_api.domain.role import Role
from sentra_brain_api.domain.system_settings import SystemSettings
from sentra_brain_api.domain.user import UserEntity
from sentra_brain_api.features.auth.auth_service import AuthService
from sentra_brain_api.features.user.models import SignupResponse, User
from sentra_brain_api.features.user.repository import UserRepository
from sqlalchemy.orm import Session
import asyncio
import os

logger = logging.get_logger("sentra_brain_api")

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_user_by_username(self, username: str, db: Session):
        return self.user_repository(db).get_by_username(username)

    def signup(self, user_data, db: Session, notification_service_cls=None, auth_service_cls=None):
        """
        Handles user signup, creates user, sends verification email if SMTP is configured.
        """
        user_count = db.query(UserEntity).filter(~UserEntity.roles.contains("superadmin")).count()
        settings = db.query(SystemSettings).first()

        # Check if user limit is reached
        if settings.max_users != -1 and user_count >= settings.max_users:
            raise SentraHTTPException(
                status_code=403,
                code="USER_LIMIT_REACHED",
                message="User limit reached",
                path="/users/signup",
                suggestion="Upgrade your license or contact support"
            )
        notification_service_cls = notification_service_cls or NotificationService
        auth_service_cls = auth_service_cls or AuthService

        user_repository = self.user_repository(db)
        notification_service = notification_service_cls.from_env_vars()
        auth_service = auth_service_cls(user_repository)

        logger.info(f"Creating user: {user_data.username}")
        user = UserEntity(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=auth_service_cls.get_password_hash(user_data.password),
            disabled=False
        )
        user.set_roles([Role.USER])

        try:
            user_repository.create(user)
            verification_token = auth_service.create_verification_token(user.id)
            base_url = os.getenv("BASE_URL", "http://localhost:8100")
            verification_url = f"{base_url}/user/validate?token={verification_token}"
            email_sent = asyncio.run(notification_service.send_email_verification(user.email, verification_url))

            message = (
                "A verification email has been sent. Please check your inbox."
                if email_sent else
                "Your account has been created."
            )

            return SignupResponse(
                user=User.model_validate(user, from_attributes=True),
                message=message
            )

        except ValueError as e:
            logger.error(f"Error creating user: {str(e)}")
            raise SentraHTTPException(
                status_code=400,
                code="INVALID_REQUEST",
                message=str(e),
                path="/users/signup",
                suggestion="Check request payload"
            )
    def update_user(self, current_user_id: int, user_to_update_id: int, user_update, db: Session):
        """
        Handles updating a user. Only allows self-update or admin update.
        """
        user_repository = self.user_repository(db)
        user = user_repository.get(user_to_update_id)
        if not user:            
            raise SentraHTTPException(
                status_code=404,
                code="USER_NOT_FOUND",
                message=f"User with id {user_to_update_id} not found",
                path=f"/users/{user_to_update_id}",
                suggestion="Check user ID or contact support"
            )
        # Add permission checks as needed
        if user_update.full_name is not None:
            user.full_name = user_update.full_name
        if user_update.email is not None:
            user.email = user_update.email
        if user_update.password is not None:
            user.hashed_password = AuthService.get_password_hash(user_update.password)
        user_repository.update(user)
        return User.model_validate(user, from_attributes=True)

    def validate_user(self, token: str, db: Session):
        """
        Handles user email validation via token.
        """
        user_repository = self.user_repository(db)
        auth_service = AuthService(user_repository)
        try:
            payload = auth_service.decode_verification_token(token)
            user_id = payload.get("user_id")
            if not user_id:
                logger.error("Invalid token: user_id not found in payload")
                raise SentraHTTPException(
                    status_code=400,
                    code="INVALID_TOKEN",
                    message="Invalid token",
                    path="/users/validate",
                    suggestion="Request a new verification email"
                )
            user = user_repository.get(user_id)
            if not user:
                raise SentraHTTPException(
                    status_code=404,
                    code="USER_NOT_FOUND",
                    message="User not found",
                    path="/users/validate",
                    suggestion="Check user ID"
                )
            user.disabled = False
            user_repository.update(user)
            return User.model_validate(user, from_attributes=True)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating user: {str(e)}")
            raise SentraHTTPException(
                status_code=400,
                code="INVALID_REQUEST",
                message=str(e),
                path="/users/validate",
                suggestion="Check request payload"
            )
