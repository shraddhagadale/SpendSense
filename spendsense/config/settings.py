"""
Centralized application settings.

Loads configuration from environment variables.
In local development, automatically loads from .env file if present.

Usage:
    from spendsense.config import settings
    
    api_key = settings.openai_api_key
    db_url = settings.database_url
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from functools import lru_cache

# Project root (two levels up from this file)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Load .env file in local development (before reading env vars)
_dotenv_path = PROJECT_ROOT / ".env"
if _dotenv_path.exists():
    from dotenv import load_dotenv
    load_dotenv(_dotenv_path)


@dataclass(frozen=True)
class Settings:
    """Immutable application settings."""
    
    # =========================================================================
    # OpenAI / LLM
    # =========================================================================
    OPENAI_API_KEY: str
    OPENAI_MODEL: str  # Default/fallback model
    LOW_COST_MODEL: str  # For simple tasks like categorization
    HIGH_COST_MODEL: str  # For complex tasks (if needed)
    OPENAI_BASE_URL: str
    OPENAI_TIMEOUT: int
    
    # =========================================================================
    # Database
    # =========================================================================
    DATABASE_URL: str
    
    # PostgreSQL individual params (used if DATABASE_URL not set)
    PG_HOST: str
    PG_PORT: str
    PG_USER: str
    PG_PASSWORD: str
    PG_DATABASE: str
    
    # =========================================================================
    # Paths
    # =========================================================================
    PROJECT_ROOT: Path = field(default=PROJECT_ROOT)
    
    @property
    def DATA_DIR(self) -> Path:
        return self.PROJECT_ROOT / "data"
    
    # =========================================================================
    # Computed Properties
    # =========================================================================
    
    @property
    def database_url(self) -> str:
        """Build database connection URL for PostgreSQL."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        password_part = f":{self.PG_PASSWORD}" if self.PG_PASSWORD else ""
        return f"postgresql://{self.PG_USER}{password_part}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DATABASE}"
    
    @property
    def openai_api_key(self) -> str:
        """
        Get OpenAI API key from environment variable.
        """
        if self.OPENAI_API_KEY:
            return self.OPENAI_API_KEY
        
        raise RuntimeError(
            "Missing OpenAI API key. Set OPENAI_API_KEY in .env or environment."
        )


@lru_cache(maxsize=1)
def _load_settings() -> Settings:
    """Load settings from environment. Cached for performance."""
    return Settings(
        # OpenAI
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
        OPENAI_MODEL=os.getenv("OPENAI_MODEL", ""),
        OPENAI_BASE_URL=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions"),
        OPENAI_TIMEOUT=int(os.getenv("OPENAI_TIMEOUT", "60")),
        
        # Database
        DATABASE_URL=os.getenv("DATABASE_URL", ""),
        PG_HOST=os.getenv("PG_HOST", "localhost"),
        PG_PORT=os.getenv("PG_PORT", "5432"),
        PG_USER=os.getenv("PG_USER", "postgres"),
        PG_PASSWORD=os.getenv("PG_PASSWORD", ""),
        PG_DATABASE=os.getenv("PG_DATABASE", "spendsense"),
    )


# Global settings instance
settings = _load_settings()
