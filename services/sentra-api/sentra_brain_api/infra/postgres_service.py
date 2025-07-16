# sentra_brain_api/infra/postgres_service.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sentra_brain_api.core.config import settings
from sentra_brain_api.crosscutting.logging import get_logger
from sentra_brain_api.domain.base_entity import BaseEntity
from sentra_brain_api.domain.role import Role
from sentra_brain_api.infra.security import pwd_context

logger = get_logger(__name__)

# 1. Module-level SQLAlchemy objects (engine/session)
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3. DB initialization for app startup
def init_db():
    from sentra_brain_api.domain.user import UserEntity
    from sentra_brain_api.features.user.repository import UserRepository

    try:
        # Create tables (using BaseEntity to include all inherited models)
        BaseEntity.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.exception(f"Database initialization failed: {e}")
        raise
    # Create initial admin user if none exists
    db = SessionLocal()
    user_repo = UserRepository(db)

    if not user_repo.get_by_username(settings.initial_admin_username):
        admin_user = UserEntity(
            username=settings.initial_admin_username,
            email=settings.initial_admin_email,
            full_name="API Admin",
            hashed_password=pwd_context.hash(settings.initial_admin_password),
            disabled=False
        )
        admin_user.set_roles([Role.ADMIN, Role.USER])
        user_repo.create(admin_user)
    db.close()
