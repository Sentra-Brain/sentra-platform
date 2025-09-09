# packages/sentra-domain/src/sentra/domain/enums/role.py
import enum

class Role(enum.Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"
