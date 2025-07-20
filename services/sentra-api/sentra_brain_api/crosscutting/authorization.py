
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import JWTError, jwt

from sqlalchemy.orm import Session
from sentra_brain_api.features.auth.models import TokenData
from sentra_brain_api.core.config import settings
from sentra_brain_api.features.user.repository import UserRepository
from sentra_brain_api.infra.postgres_service import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_authenticated_user(token: str = Depends(oauth2_scheme), 
                            db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )    
    token_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    account_disabled_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Your account is disabled. Please contact support.",
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if not username:
            raise token_exception
        token_data = TokenData(username=username, roles=payload.get("roles"))
    except JWTError:
        raise token_exception

    user = user_repo.get_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    if user.disabled:
        raise account_disabled_exception
    return user

def get_admin_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user = get_authenticated_user(token=token, db=db)
    if 'admin' not in user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the necessary permissions",
        )
    return user

def get_superadmin_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user = get_authenticated_user(token=token, db=db)
    if 'superadmin' not in user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the necessary permissions",
        )
    return user