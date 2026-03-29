"""Application configuration."""

import os
from functools import lru_cache


class Settings:
    """Application settings."""

    DATABASE_URL: str = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "cloud")
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",  # React dev 
        "http://10.168.6.136:5173",
    ]


@lru_cache
def get_settings() -> Settings:
    """Get application settings.
    
    Returns:
        Settings: Application configuration.
    """
    return Settings()
