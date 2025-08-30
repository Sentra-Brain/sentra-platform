from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from sentra_core.infra.sql.postgres_settings import settings
from sentra_brain_api.core.exceptions import SentraHTTPException
from sentra_core.logging import get_logger
from sentra_core.domain.entities.user_entity import UserEntity
from sentra_brain_api.features.auth.models import TokenData
from sentra_core.domain.repository.user_repository import UserRepository
from sentra_core.infra.sql.postgres_service import get_db

logger = get_logger("sentra.auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_authenticated_user(token: str = Depends(oauth2_scheme),
                            db: Session = Depends(get_db)) -> UserEntity:
    user_repo = UserRepository(db)

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")
        if not username:
            logger.warning("Token received with no subject (sub)")
            raise SentraHTTPException(
                status_code=400,
                code="INVALID_TOKEN",
                message="Missing subject in token",
                path="/auth/validate",
                suggestion="Request a new token"
            )
        token_data = TokenData(username=username, roles=payload.get("roles"))
        logger.debug(f"Token decoded successfully for user '{username}'")
    except JWTError as e:
        logger.warning(f"Invalid JWT token: {str(e)}")
        raise SentraHTTPException(
            status_code=401,
            code="INVALID_TOKEN",
            message="Invalid token",
            path="/auth/validate",
            suggestion="Request a new token"
        )

    user = user_repo.get_by_username(username)
    if user is None:
        logger.warning(f"Token refers to nonexistent user: '{username}'")
        raise SentraHTTPException(
            status_code=401,
            code="USER_NOT_FOUND",
            message="User not found for token",
            path="/auth/validate",
            suggestion="Ensure the account exists or re-authenticate"
        )
    if user.disabled:
        logger.warning(f"User '{user.username}' is disabled and tried to authenticate")
        raise SentraHTTPException(
            status_code=403,
            code="ACCOUNT_DISABLED",
            message="Your account is disabled",
            path="/auth/validate",
            suggestion="Contact support to reactivate your account"
        )

    logger.info(f"Authenticated user '{user.username}' with roles: {user.roles}")
    return user


def get_admin_user(token: str = Depends(oauth2_scheme),
                   db: Session = Depends(get_db)):
    user = get_authenticated_user(token=token, db=db)
    if 'admin' not in user.roles:
        logger.warning(f"User '{user.username}' attempted admin access without sufficient permissions")
        raise SentraHTTPException(
            status_code=403,
            code="INSUFFICIENT_PERMISSIONS",
            message="Admin privileges required",
            path="/admin",
            suggestion="Contact a system administrator"
        )
    logger.info(f"Admin user '{user.username}' authenticated")
    return user


def get_superadmin_user(token: str = Depends(oauth2_scheme),
                        db: Session = Depends(get_db)):
    user = get_authenticated_user(token=token, db=db)
    if 'superadmin' not in user.roles:
        logger.warning(f"User '{user.username}' attempted superadmin access without permissions")
        raise SentraHTTPException(
            status_code=403,
            code="INSUFFICIENT_PERMISSIONS",
            message="Superadmin privileges required",
            path="/admin",
            suggestion="Operation restricted to superadmins"
        )
    logger.info(f"Superadmin user '{user.username}' authenticated")
    return user
