# sentra_brain_api/infra/postgres_service.py

import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sentra_shared.infra.sql.postgres_settings import settings
from sentra_shared.core.logging import get_logger
from sentra_shared.domain.entities.base_entity import BaseEntity
from sentra_shared.domain.entities.role import Role
from sentra_shared.domain.entities.system_settings import SystemSettings
from sentra_shared.infra.sql.security import pwd_context

logger = get_logger(__name__)

# Create database engine
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logger.error(f"Error creating database session: {e}")
        db.close()
        raise

def init_db():
    from sentra_shared.domain.entities.user_entity import UserEntity
    from sentra_shared.domain.entities.conversation_entity import ConversationEntity
    from sentra_shared.domain.entities.knowledge_source_entity import KnowledgeSourceEntity
    from sentra_shared.domain.entities.document_entity import DocumentEntity
    from sentra_shared.domain.repositories.user_repository import UserRepository
    from sqlalchemy.exc import OperationalError

    MAX_RETRIES = 30
    RETRY_DELAY_SECONDS = 2

    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            # Create tables (using BaseEntity to include all inherited models)
            BaseEntity.metadata.create_all(bind=engine)
            logger.info("Database initialized successfully.")
            break
        except OperationalError as e:
            attempt += 1
            logger.warning(f"[init_db] Database not ready, attempt {attempt}/{MAX_RETRIES}: {e}")
            time.sleep(RETRY_DELAY_SECONDS)
        except Exception as e:
            logger.exception("[init_db] Unexpected error initializing database.")
            raise

    if attempt == MAX_RETRIES:
        logger.error("[init_db] Database could not be initialized after maximum retries.")
        raise RuntimeError("Database initialization failed after retries.")

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
        logger.info("[init_db] Initial admin user created.")

    if not db.query(SystemSettings).first():
        db.add(SystemSettings(max_users=3))
        db.commit()
        logger.info("[init_db] Default system settings created.")

    db.close()

def create_db_session() -> Session:
    """Create a new database session."""
    return SessionLocal()