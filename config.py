"""
DEPRECATED: Import from spendsense.config instead.

This shim exists only for alembic backward compatibility.
Will be removed in a future version.
"""
from spendsense.config import settings

DB_TYPE = settings.DB_TYPE
SQLITE_PATH = settings.SQLITE_PATH

def get_database_url() -> str:
    return settings.database_url
