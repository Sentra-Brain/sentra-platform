# sentra_brain_api/infra/postgres_service.py

import time
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError

from sentra_core.logging import get_logger
from sentra_core.infra.sql.postgres_settings import settings
from sentra_core.infra.sql.security import pwd_context
from sentra_core.infra.sql.migrations_check import check_schema_consistency

from sentra_core.domain.enums.role import Role
from sentra_core.domain.repository.user_repository import UserRepository
from sentra_core.domain.entities.system_settings import SystemSettingsEntity
from sentra_core.domain.entities.chat_settings import ChatSettingsEntity
from sentra_core.domain.entities.user_entity import UserEntity

logger = get_logger(__name__)

# Create database engine
engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Ensures the DB is ready and that the schema is up to date with Alembic.

    - Retries connection for up to 30 attempts
    - Fails fast if the migration version is out of sync
    - Creates initial admin user and system settings if needed
    """
    MAX_RETRIES = 30
    RETRY_DELAY_SECONDS = 2

    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            # ✅ Verify that the database is migrated before continuing
            check_schema_consistency(engine)
            logger.info("Database schema is up to date.")
            break
        except OperationalError as e:
            attempt += 1
            logger.warning(f"[init_db] Database not ready, attempt {attempt}/{MAX_RETRIES}: {e}")
            time.sleep(RETRY_DELAY_SECONDS)
        except RuntimeError as e:
            logger.error(f"[init_db] Migration check failed: {e}")
            raise
        except Exception as e:
            logger.exception("[init_db] Unexpected error checking DB readiness.")
            raise

    if attempt == MAX_RETRIES:
        logger.error("[init_db] Database could not be initialized after maximum retries.")
        raise RuntimeError("Database initialization failed after retries.")

    # Create initial admin user if none exists
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)

        if not user_repo.get_by_username(settings.initial_admin_username):
            admin_user = UserEntity(
                username=settings.initial_admin_username,
                email=settings.initial_admin_email,
                full_name="API Admin",
                hashed_password=pwd_context.hash(settings.initial_admin_password),
                disabled=False
            )
            admin_user.set_roles([Role.SUPERADMIN, Role.ADMIN, Role.USER])
            user_repo.create(admin_user)
            logger.info("[init_db] Initial Super Admin user created.")

        if not db.query(SystemSettingsEntity).first():
            db.add(SystemSettingsEntity(max_users=3))
            db.commit()
            logger.info("[init_db] Default system settings created.")

        if not db.query(ChatSettingsEntity).first():
            db.add(ChatSettingsEntity())
            db.commit()
            logger.info("[init_db] Default chat settings created.")

    finally:
        db.close()


def create_db_session() -> Session:
    """Create a new database session."""
    return SessionLocal()
