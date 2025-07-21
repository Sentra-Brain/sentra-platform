from enum import Enum

class Role(Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"