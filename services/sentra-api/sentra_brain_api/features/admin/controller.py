from fastapi import APIRouter, HTTPException, status
from .models import User, Role, Slot
import logging

router = APIRouter()
logger = logging.getLogger("admin")

@router.get("/users", response_model=list[User])
def list_users():
    # Dummy data
    logger.info("Listing users")
    return [User(id=1, email="admin@sentra.com", full_name="Admin", is_active=True, role="admin")]

@router.get("/roles", response_model=list[Role])
def list_roles():
    logger.info("Listing roles")
    return [Role(name="admin", description="Administrator")]

@router.get("/slots", response_model=list[Slot])
def list_slots():
    logger.info("Listing slots")
    return [Slot(id=1, name="Slot 1", assigned_to=None)]
