"""User service for business logic."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.database.repositories.users import UserRepository
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import (
    ValidationError, NotFoundError, ConflictError, 
    AuthenticationError, DatabaseError
)

logger = logging.getLogger(__name__)


class UserService:
    """Service for user-related business logic."""
    
    def __init__(self):
        """Initialize user service."""
        self.user_repository = UserRepository()
    
    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new user.
        
        Args:
            username: User's username
            email: User's email
            password: User's password
            first_name: Optional first name
            last_name: Optional last name
            **kwargs: Additional user fields
            
        Returns:
            Dict[str, Any]: Created user data
            
        Raises:
            ValidationError: If input is invalid
            ConflictError: If user already exists
            DatabaseError: If creation fails
        """
        # Validate input
        self._validate_user_data(username, email, password)
        
        # Check if user already exists
        existing_user = await self.user_repository.get_user_by_email(email)
        if existing_user:
            raise ConflictError(f"User with email {email} already exists")
        
        existing_username = await self.user_repository.get_user_by_username(username)
        if existing_username:
            raise ConflictError(f"Username {username} already exists")
        
        # Create user
        user_id = await self.user_repository.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            **kwargs
        )
        
        # Return created user data
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise DatabaseError("Failed to retrieve created user")
        
        # Remove password from response
        user.pop("password", None)
        
        logger.info(f"Created user: {email}")
        return user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user.
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Optional[Dict[str, Any]]: User data if authentication succeeds, None otherwise
        """
        try:
            user = await self.user_repository.verify_password(email, password)
            
            if user:
                # Update last login
                await self.user_repository.update_last_login(user["_id"])
                
                # Remove password from response
                user.pop("password", None)
                
                logger.info(f"User authenticated: {email}")
                return user
            
            logger.warning(f"Authentication failed for: {email}")
            return None
            
        except Exception as e:
            logger.error(f"Error authenticating user {email}: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Optional[Dict[str, Any]]: User data or None if not found
        """
        user = await self.user_repository.get_by_id(user_id)
        
        if user:
            # Remove password from response
            user.pop("password", None)
        
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email.
        
        Args:
            email: User's email
            
        Returns:
            Optional[Dict[str, Any]]: User data or None if not found
        """
        user = await self.user_repository.get_user_by_email(email)
        
        if user:
            # Remove password from response
            user.pop("password", None)
        
        return user
    
    async def update_user(
        self,
        user_id: str,
        **update_data
    ) -> Optional[Dict[str, Any]]:
        """Update user information.
        
        Args:
            user_id: User ID
            **update_data: Fields to update
            
        Returns:
            Optional[Dict[str, Any]]: Updated user data or None if not found
        """
        # Validate update data
        self._validate_update_data(update_data)
        
        # Don't allow password updates through this method
        if "password" in update_data:
            del update_data["password"]
        
        # Update user
        success = await self.user_repository.update(user_id, update_data)
        
        if success:
            updated_user = await self.user_repository.get_by_id(user_id)
            if updated_user:
                # Remove password from response
                updated_user.pop("password", None)
                logger.info(f"Updated user: {user_id}")
                return updated_user
        
        return None
    
    async def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> bool:
        """Change user password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            bool: True if password changed successfully
            
        Raises:
            ValidationError: If passwords are invalid
            AuthenticationError: If current password is incorrect
            NotFoundError: If user not found
        """
        # Validate new password
        if len(new_password) < 6:
            raise ValidationError("Password must be at least 6 characters long")
        
        # Get user
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        # Verify current password
        if not verify_password(current_password, user["password"]):
            raise AuthenticationError("Current password is incorrect")
        
        # Update password
        success = await self.user_repository.update_password(user_id, new_password)
        
        if success:
            logger.info(f"Password changed for user: {user_id}")
        
        return success
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if deactivated successfully
        """
        success = await self.user_repository.deactivate_user(user_id)
        
        if success:
            logger.info(f"Deactivated user: {user_id}")
        
        return success
    
    async def activate_user(self, user_id: str) -> bool:
        """Activate a user.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if activated successfully
        """
        success = await self.user_repository.activate_user(user_id)
        
        if success:
            logger.info(f"Activated user: {user_id}")
        
        return success
    
    async def verify_user(self, user_id: str) -> bool:
        """Verify a user's email.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if verified successfully
        """
        success = await self.user_repository.verify_user(user_id)
        
        if success:
            logger.info(f"Verified user: {user_id}")
        
        return success
    
    async def search_users(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search users.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: List of matching users
        """
        users = await self.user_repository.search_users(query, limit)
        
        # Remove passwords from results
        for user in users:
            user.pop("password", None)
        
        return users
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict[str, Any]: User statistics
        """
        return await self.user_repository.get_user_stats(user_id)
    
    def _validate_user_data(self, username: str, email: str, password: str) -> None:
        """Validate user creation data.
        
        Args:
            username: Username to validate
            email: Email to validate
            password: Password to validate
            
        Raises:
            ValidationError: If data is invalid
        """
        errors = []
        
        if not username or len(username) < 1:
            errors.append("Username is required")
        elif len(username) > 255:
            errors.append("Username must be less than 255 characters")
        
        if not email or "@" not in email:
            errors.append("Valid email is required")
        
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long")
        elif len(password) > 128:
            errors.append("Password must be less than 128 characters")
        
        if errors:
            raise ValidationError("Validation failed", details={"errors": errors})
    
    def _validate_update_data(self, update_data: Dict[str, Any]) -> None:
        """Validate user update data.
        
        Args:
            update_data: Data to validate
            
        Raises:
            ValidationError: If data is invalid
        """
        errors = []
        
        if "username" in update_data:
            username = update_data["username"]
            if not username or len(username) < 1:
                errors.append("Username is required")
            elif len(username) > 255:
                errors.append("Username must be less than 255 characters")
        
        if "email" in update_data:
            email = update_data["email"]
            if not email or "@" not in email:
                errors.append("Valid email is required")
        
        if "first_name" in update_data and update_data["first_name"] and len(update_data["first_name"]) > 255:
            errors.append("First name must be less than 255 characters")
        
        if "last_name" in update_data and update_data["last_name"] and len(update_data["last_name"]) > 255:
            errors.append("Last name must be less than 255 characters")
        
        if errors:
            raise ValidationError("Validation failed", details={"errors": errors})
