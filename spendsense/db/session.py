"""Database session management."""
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from spendsense.config import settings
from spendsense.models import Base


# Create engine
engine = create_engine(settings.database_url, echo=False)

# Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db() -> None:
    """
    Initialize database tables.
    
    For production, use Alembic migrations instead.
    This is useful for development/testing.
    """
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session():
    """
    Context manager for database sessions.
    
    Usage:
        with get_session() as session:
            session.query(Transaction).all()
    
    Automatically commits on success, rolls back on error.
    """
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
