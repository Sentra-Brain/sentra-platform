# packages/sentra-infra/src/sentra/infra/sql/postgres_service.py

import time
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError

from sentra.infra.sql.postgres_settings import settings
from sentra.shared.logging import get_logger

logger = get_logger(__name__)

engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_pre_ping=True,
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
    This service becomes a pure consumer of tables already created.
    How this works:
      • Only ensures the DB is reachable.
      • No schema creation.
      • No migrations.
      • No seed data.
      • API owns schema + migrations + seeding.
    """

    MAX_RETRIES = 30
    RETRY_DELAY_SECONDS = 2

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("[init_db] Database connection OK.")
            return
        except OperationalError as e:
            logger.warning(
                f"[init_db] Database not ready, attempt {attempt}/{MAX_RETRIES}: {e}"
            )
            time.sleep(RETRY_DELAY_SECONDS)
        except Exception as e:
            logger.exception("[init_db] Unexpected error while checking DB readiness.")
            raise

    logger.error("[init_db] Database could not be reached after maximum retries.")
    raise RuntimeError("Database connection failed after retries.")

def create_db_session() -> Session:
    return SessionLocal()
