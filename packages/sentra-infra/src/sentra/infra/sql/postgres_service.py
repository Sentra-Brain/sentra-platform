# packages/sentra-infra/src/sentra/infra/sql/postgres_service.py

import time
from typing import Generator, Optional
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError

from sentra.infra.sql.postgres_settings import settings
from sentra.shared.logging import get_logger

logger = get_logger(__name__)

_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None

def get_engine() -> Engine:
    """Get or create the SQLAlchemy engine (lazy initialization)"""
    global _engine
    if _engine is None:
        logger.info(f"Creating database engine with URL: {settings.database_url[:30]}...")
        _engine = create_engine(
            settings.database_url,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_pre_ping=True,
        )
    return _engine

def get_session_maker() -> sessionmaker:
    """Get or create the session maker (lazy initialization)"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

def get_db() -> Generator[Session, None, None]:
    SessionLocal = get_session_maker()
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

    engine = get_engine()
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
    SessionLocal = get_session_maker()
    return SessionLocal()
