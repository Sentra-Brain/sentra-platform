from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from sentra_shared.infra.sql.postgres_settings import settings
from sentra_brain_api.core.exceptions import SentraHTTPException
from sentra_shared.domain.entities.user_entity import UserEntity
from sentra_shared.domain.repository.user_repository  import UserRepository
from sentra_shared.core import logging

logger = logging.get_logger("sentra_brain_api")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:   
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate_user(self, username: str, password: str) -> UserEntity | None:
        user = self.user_repo.get_by_username(username)
        if not user:
            user = self.user_repo.get_by_email(username.lower())
        if not user or not self._verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)  # 7 days default
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    def validate_refresh_token(self, refresh_token: str) -> UserEntity | None:
        try:
            payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
            username: str = payload.get("sub")
            token_type: str = payload.get("type")
            
            if not username or token_type != "refresh":
                logger.warning("Invalid refresh token: missing subject or wrong type")
                return None
                
            user = self.user_repo.get_by_username(username)
            if not user:
                user = self.user_repo.get_by_email(username.lower())
            
            if not user or user.disabled:
                logger.warning(f"Refresh token refers to invalid or disabled user: '{username}'")
                return None
                
            return user
        except ExpiredSignatureError:
            logger.warning("Refresh token has expired")
            return None
        except JWTError as e:
            logger.warning(f"Invalid refresh token: {str(e)}")
            return None
    
    def create_verification_token(self, user_id: int, expires_delta: timedelta | None = None):
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=24))
        to_encode = {"user_id": user_id, "exp": expire}
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    
    def decode_verification_token(self, token: str):
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except ExpiredSignatureError:
            logger.error(f"Token has expired: {token}")
            raise SentraHTTPException(
                status_code=400,
                code="TOKEN_EXPIRED",
                message="Token has expired",
                path="/users/validate",
                suggestion="Request a new verification email"
            )
        except JWTError:
            logger.error(f"Invalid token: {token}")
            raise SentraHTTPException(
                status_code=400,
                code="INVALID_TOKEN",
                message="Invalid token",
                path="/users/validate",
                suggestion="Request a new verification email"
            )


    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
