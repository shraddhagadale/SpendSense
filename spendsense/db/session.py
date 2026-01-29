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
