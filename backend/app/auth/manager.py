"""User manager for FastAPI Users with custom actions."""

import logging
from typing import Optional
from beanie import PydanticObjectId
from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.exceptions import UserAlreadyExists, InvalidPasswordException
from app.auth.models import User
from app.config import get_settings
from app.auth.database import get_user_db

logger = logging.getLogger(__name__)
settings = get_settings()


class UserManager(BaseUserManager[User, PydanticObjectId]):
    """Custom user manager for FastAPI Users."""
    
    reset_password_token_secret = settings.JWT_SECRET
    verification_token_secret = settings.JWT_SECRET
    
    async def validate_password(self, password: str, user: User | None = None) -> None:
        """Override password validation to be more permissive.
        
        Only requires minimum 8 characters.
        """
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )
    
    async def on_after_register(
        self, user: User, request: Optional[object] = None
    ) -> None:
        """Hook called after user registration.
        
        Args:
            user: The newly registered user
            request: Optional request object
        """
        logger.info(f"User {user.email} registered successfully")
    
    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[object] = None
    ) -> None:
        """Hook called after password reset is requested.
        
        Args:
            user: User requesting password reset
            token: Reset token
            request: Optional request object
        """
        logger.info(f"Password reset requested for user {user.email}")
    
    async def on_after_reset_password(
        self, user: User, request: Optional[object] = None
    ) -> None:
        """Hook called after password is reset.
        
        Args:
            user: User who reset password
            request: Optional request object
        """
        logger.info(f"Password reset completed for user {user.email}")
    
    async def on_after_verification_request(
        self, user: User, token: str, request: Optional[object] = None
    ) -> None:
        """Hook called after email verification is requested.
        
        Args:
            user: User requesting verification
            token: Verification token
            request: Optional request object
        """
        logger.info(f"Email verification requested for user {user.email}")
    
    async def on_after_verify(
        self, user: User, request: Optional[object] = None
    ) -> None:
        """Hook called after email is verified.
        
        Args:
            user: User whose email was verified
            request: Optional request object
        """
        logger.info(f"Email verified for user {user.email}")


async def get_user_manager(user_db=Depends(get_user_db)):
    """Dependency to get user manager.
    
    Args:
        user_db: User database dependency
        
    Yields:
        UserManager: User manager instance
    """
    yield UserManager(user_db)
