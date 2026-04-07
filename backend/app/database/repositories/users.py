"""User repository for database operations."""

import logging
from typing import Dict, Any, Optional, List
from bson import ObjectId

from app.database.repositories.base import BaseRepository
from app.core.security import get_password_hash
from app.core.exceptions import ConflictError, DatabaseError

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    """Repository for user operations."""
    
    def __init__(self):
        """Initialize user repository."""
        super().__init__("users")
    
    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        **kwargs
    ) -> str:
        """Create a new user with hashed password.
        
        Args:
            username: User's username
            email: User's email
            password: User's plain password
            **kwargs: Additional user fields
            
        Returns:
            str: ID of the created user
            
        Raises:
            ConflictError: If user already exists
            DatabaseError: If creation fails
        """
        # Check if user already exists
        if await self.exists({"email": email.lower()}):
            raise ConflictError(f"User with email {email} already exists")
        
        # Hash password
        hashed_password = get_password_hash(password)
        
        # Create user document
        user_data = {
            "username": username,
            "email": email.lower(),
            "password": hashed_password,
            "is_active": True,
            "is_verified": False,
            **kwargs
        }
        
        return await self.create(user_data)
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email.
        
        Args:
            email: User's email
            
        Returns:
            Optional[Dict[str, Any]]: User data or None if not found
        """
        return await self.get_one({"email": email.lower()})
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username.
        
        Args:
            username: User's username
            
        Returns:
            Optional[Dict[str, Any]]: User data or None if not found
        """
        return await self.get_one({"username": username})
    
    async def verify_password(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify user password.
        
        Args:
            email: User's email
            password: Plain password to verify
            
        Returns:
            Optional[Dict[str, Any]]: User data if password matches, None otherwise
        """
        from app.core.security import verify_password
        
        user = await self.get_user_by_email(email)
        if user and verify_password(password, user["password"]):
            return user
        
        return None
    
    async def update_password(self, user_id: str, new_password: str) -> bool:
        """Update user password.
        
        Args:
            user_id: User's ID
            new_password: New plain password
            
        Returns:
            bool: True if updated successfully
            
        Raises:
            DatabaseError: If operation fails
        """
        hashed_password = get_password_hash(new_password)
        return await self.update(user_id, {"password": hashed_password})
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp.
        
        Args:
            user_id: User's ID
            
        Returns:
            bool: True if updated successfully
        """
        from datetime import datetime
        
        return await self.update(user_id, {"last_login": datetime.utcnow()})
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account.
        
        Args:
            user_id: User's ID
            
        Returns:
            bool: True if deactivated successfully
        """
        return await self.update(user_id, {"is_active": False})
    
    async def activate_user(self, user_id: str) -> bool:
        """Activate a user account.
        
        Args:
            user_id: User's ID
            
        Returns:
            bool: True if activated successfully
        """
        return await self.update(user_id, {"is_active": True})
    
    async def verify_user(self, user_id: str) -> bool:
        """Mark user as verified.
        
        Args:
            user_id: User's ID
            
        Returns:
            bool: True if verified successfully
        """
        return await self.update(user_id, {"is_verified": True})
    
    async def search_users(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search users by username or email.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: List of matching users
        """
        search_query = {
            "$or": [
                {"username": {"$regex": query, "$options": "i"}},
                {"email": {"$regex": query, "$options": "i"}}
            ]
        }
        
        return await self.get_many(search_query, limit=limit)
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dict[str, Any]: User statistics
        """
        try:
            # This could be expanded to include more stats
            user = await self.get_by_id(user_id)
            if not user:
                return {}
            
            return {
                "user_id": user_id,
                "username": user.get("username"),
                "email": user.get("email"),
                "created_at": user.get("created_at"),
                "last_login": user.get("last_login"),
                "is_active": user.get("is_active", True),
                "is_verified": user.get("is_verified", False)
            }
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            return {}
    
    def get_model_schema(self) -> Dict[str, Any]:
        """Get user model schema.
        
        Returns:
            Dict[str, Any]: User model schema
        """
        return {
            "type": "object",
            "properties": {
                "username": {"type": "string", "minLength": 1, "maxLength": 255},
                "email": {"type": "string", "format": "email"},
                "password": {"type": "string", "minLength": 6},
                "is_active": {"type": "boolean", "default": True},
                "is_verified": {"type": "boolean", "default": False},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "profile_picture": {"type": "string"},
                "preferences": {"type": "object"}
            },
            "required": ["username", "email", "password"],
            "additionalProperties": True
        }
