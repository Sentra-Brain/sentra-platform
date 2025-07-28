# sentra_shared/domain/enums/role.py
import enum

class Role(enum.Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"
