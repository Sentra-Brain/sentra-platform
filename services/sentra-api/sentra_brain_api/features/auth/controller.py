from fastapi import APIRouter, Depends, HTTPException, status
from .models import UserLoginRequest, UserRegisterRequest, AuthResponse, UserInfo
from pydantic import EmailStr
import logging

router = APIRouter()
logger = logging.getLogger("auth")

@router.post("/login", response_model=AuthResponse)
def login(request: UserLoginRequest):
    # Dummy logic for illustration
    if request.email == "admin@sentra.com" and request.password == "password":
        logger.info(f"User {request.email} logged in.")
        return AuthResponse(access_token="dummy-token")
    logger.warning(f"Failed login for {request.email}")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@router.post("/register", response_model=UserInfo)
def register(request: UserRegisterRequest):
    # Dummy logic for illustration
    logger.info(f"Registering user {request.email}")
    return UserInfo(id=1, email=request.email, full_name=request.full_name, is_active=True)
