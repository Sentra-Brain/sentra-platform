# sentra_brain_api/domain/role.py
from enum import Enum

class Role(Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"