# sentra_brain_api/infra/postgres_service.py

import time
from sqlalchemy import create_engine, make_url
from sqlalchemy.orm import sessionmaker
from sentra_shared.infra.sql.postgres_settings import settings
from sentra_shared.core.logging import get_logger
import sentra_shared.domain.entities 
from sentra_shared.domain.enums.role import Role
from sentra_shared.domain.entities.system_settings import SystemSettings
from sentra_shared.infra.sql.security import pwd_context

logger = get_logger(__name__)

# 1. Module-level SQLAlchemy objects (engine/session)
engine = create_engine(
    make_url(settings.database_url).set(drivername="postgresql+psycopg2"),
    future=True,
    pool_pre_ping=True
)
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
    import sentra_shared.domain.entities 
    from sentra_shared.domain.entities.user_entity import UserEntity
    from sentra_shared.domain.entities.conversation_entity import ConversationEntity
    from sentra_shared.domain.entities.knowledge_source_entity import KnowledgeSourceEntity
    from sentra_shared.domain.entities.document_entity import DocumentEntity
    from sentra_shared.domain.repository.user_repository import UserRepository
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
