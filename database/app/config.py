"""Application configuration."""

import os
from functools import lru_cache


class Settings:
    """Application settings."""

    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",  # React dev server
    ]


@lru_cache
def get_settings() -> Settings:
    """Get application settings.
    
    Returns:
        Settings: Application configuration.
    """
    return Settings()
