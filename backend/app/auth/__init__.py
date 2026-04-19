"""Authentication module for FastAPI Users with MongoDB/Beanie."""

from app.auth.models import User
from app.auth.schemas import UserRead, UserCreate, UserUpdate
from app.auth.manager import UserManager
from app.auth.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_superuser,
    get_optional_current_user,
)
from app.auth.routes import fastapi_users, get_auth_router

__all__ = [
    "User",
    "UserRead",
    "UserCreate",
    "UserUpdate",
    "UserManager",
    "fastapi_users",
    "get_auth_router",
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    "get_optional_current_user",
]
