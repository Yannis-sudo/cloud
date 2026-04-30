"""Application configuration."""

import os
from functools import lru_cache
from typing import List


class Settings:
    """Application settings."""

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "cloud")
    
    # FastAPI Users & JWT settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", os.getenv("SECRET_KEY", "your-secret-key-change-in-production"))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_SECONDS: int = int(os.getenv("JWT_EXPIRATION_SECONDS", "1800"))  # 30 minutes
    
    # Email verification settings
    EMAIL_VERIFICATION_ENABLED: bool = os.getenv("EMAIL_VERIFICATION_ENABLED", "false").lower() == "true"
    ALLOW_UNVERIFIED_EMAIL_LOGIN: bool = os.getenv("ALLOW_UNVERIFIED_EMAIL_LOGIN", "true").lower() == "true"
    
    # OAuth settings (placeholder for future providers)
    OAUTH_GOOGLE_CLIENT_ID: str = os.getenv("OAUTH_GOOGLE_CLIENT_ID", "")
    OAUTH_GITHUB_CLIENT_ID: str = os.getenv("OAUTH_GITHUB_CLIENT_ID", "")
    
    # Legacy security settings (kept for backward compatibility)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # React dev
        "http://10.168.6.136:5173",
        "http://10.168.5.137:5173",
        "http://10.168.5.137:8081",  # Expo web
        "http://localhost:3000",  # Alternative React port
        "http://127.0.0.1:5173",
        "http://10.168.5.137:19000",  # Expo dev server
    ]
    allow_all_origins: bool = os.getenv("ALLOW_ALL_ORIGINS", "false").lower() == "true"
    
    # File upload settings
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif", "application/pdf",
        "text/plain", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    
    # Rate limiting settings
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
    
    # Email settings
    IMAP_TIMEOUT: int = int(os.getenv("IMAP_TIMEOUT", "30"))
    SMTP_TIMEOUT: int = int(os.getenv("SMTP_TIMEOUT", "30"))
    
    # AI API settings
    OPENROUTER_COPILOT_AI_CHAT_KEY_FREE: str = os.getenv("OPENROUTER_COPILOT_AI_CHAT_KEY_FREE", "")
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Development settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"


@lru_cache
def get_settings() -> Settings:
    """Get application settings.
    
    Returns:
        Settings: Application configuration.
    """
    return Settings()
