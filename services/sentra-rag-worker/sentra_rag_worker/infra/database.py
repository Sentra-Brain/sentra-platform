from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sentra_rag_worker.core.config import settings
from sentra_rag_worker.core.logging import get_logger

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


def create_db_session() -> Session:
    """Create a new database session."""
    return SessionLocal()