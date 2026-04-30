"""Application configuration."""

import os
from functools import lru_cache
from pathlib import Path
from typing import List

try:
    from decouple import Config, RepositoryEnv
except ImportError:  # pragma: no cover - fallback for environments before deps install
    Config = None
    RepositoryEnv = None


ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
env_config = Config(RepositoryEnv(str(ENV_FILE))) if Config and ENV_FILE.exists() else None
file_env = {}

if env_config is None and ENV_FILE.exists():
    for raw_line in ENV_FILE.read_text().splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        if line.startswith("export "):
            line = line.removeprefix("export ").strip()

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")

        if key:
            file_env[key] = value


def get_env(name: str, default: str = "") -> str:
    """Read configuration from process env first, then backend/.env."""
    value = os.environ.get(name)

    if value:
        return value

    if env_config is None:
        return file_env.get(name, default)

    return env_config(name, default=default)


class Settings:
    """Application settings."""

    # Database settings
    DATABASE_URL: str = get_env("DATABASE_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = get_env("DATABASE_NAME", "cloud")
    
    # FastAPI Users & JWT settings
    JWT_SECRET: str = get_env("JWT_SECRET", get_env("SECRET_KEY", "your-secret-key-change-in-production"))
    JWT_ALGORITHM: str = get_env("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_SECONDS: int = int(get_env("JWT_EXPIRATION_SECONDS", "1800"))  # 30 minutes
    
    # Email verification settings
    EMAIL_VERIFICATION_ENABLED: bool = get_env("EMAIL_VERIFICATION_ENABLED", "false").lower() == "true"
    ALLOW_UNVERIFIED_EMAIL_LOGIN: bool = get_env("ALLOW_UNVERIFIED_EMAIL_LOGIN", "true").lower() == "true"
    
    # OAuth settings (placeholder for future providers)
    OAUTH_GOOGLE_CLIENT_ID: str = get_env("OAUTH_GOOGLE_CLIENT_ID", "")
    OAUTH_GITHUB_CLIENT_ID: str = get_env("OAUTH_GITHUB_CLIENT_ID", "")
    
    # Legacy security settings (kept for backward compatibility)
    SECRET_KEY: str = get_env("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(get_env("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(get_env("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
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
    allow_all_origins: bool = get_env("ALLOW_ALL_ORIGINS", "false").lower() == "true"
    
    # File upload settings
    MAX_FILE_SIZE: int = int(get_env("MAX_FILE_SIZE", "10485760"))  # 10MB default
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif", "application/pdf",
        "text/plain", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    
    # Rate limiting settings
    RATE_LIMIT_REQUESTS: int = int(get_env("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(get_env("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
    
    # Email settings
    IMAP_TIMEOUT: int = int(get_env("IMAP_TIMEOUT", "30"))
    SMTP_TIMEOUT: int = int(get_env("SMTP_TIMEOUT", "30"))
    
    # AI API settings
    OPENROUTER_COPILOT_AI_CHAT_KEY_FREE: str = get_env("OPENROUTER_COPILOT_AI_CHAT_KEY_FREE", "")

    # Logging settings
    LOG_LEVEL: str = get_env("LOG_LEVEL", "INFO")
    
    # Development settings
    DEBUG: bool = get_env("DEBUG", "False").lower() == "true"


@lru_cache
def get_settings() -> Settings:
    """Get application settings.
    
    Returns:
        Settings: Application configuration.
    """
    return Settings()
