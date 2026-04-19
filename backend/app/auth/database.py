"""Database dependency for FastAPI Users."""

from fastapi_users_db_beanie import BeanieUserDatabase
from app.auth.models import User


async def get_user_db() -> BeanieUserDatabase:
    """Dependency to get Beanie user database.
    
    Yields:
        BeanieUserDatabase: User database for FastAPI Users
    """
    yield BeanieUserDatabase(User)
