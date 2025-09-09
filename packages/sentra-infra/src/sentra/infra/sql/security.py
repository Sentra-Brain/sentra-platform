# packages/sentra-infra/src/sentra/infra/sql/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
