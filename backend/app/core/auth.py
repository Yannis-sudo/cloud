"""Core authentication logic."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.modules.users.service import UserService
from app.core.security import (
    create_access_token, create_refresh_token, verify_token,
    verify_refresh_token, generate_password_reset_token,
    verify_password_reset_token
)
from app.core.exceptions import (
    AuthenticationError, ValidationError, NotFoundError
)

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self):
        """Initialize auth service."""
        self.user_service = UserService()
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return tokens.
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Dict[str, Any]: Login response with tokens and user data
            
        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If input is invalid
        """
        if not email or not password:
            raise ValidationError("Email and password are required")
        
        # Authenticate user
        user = await self.user_service.authenticate_user(email, password)
        
        if not user:
            raise AuthenticationError("Invalid email or password")
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": user["email"], "user_id": user["_id"]},
            expires_delta=timedelta(minutes=30)  # 30 minutes
        )
        
        refresh_token = create_refresh_token(
            data={"sub": user["email"], "user_id": user["_id"]}
        )
        
        return {
            "user": user,
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": 1800  # 30 minutes in seconds
            }
        }
    
    async def register(
        self,
        username: str,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Register a new user and return tokens.
        
        Args:
            username: User's username
            email: User's email
            password: User's password
            first_name: Optional first name
            last_name: Optional last name
            
        Returns:
            Dict[str, Any]: Registration response with tokens and user data
            
        Raises:
            ValidationError: If input is invalid
            ConflictError: If user already exists
        """
        # Create user
        user = await self.user_service.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": user["email"], "user_id": user["_id"]},
            expires_delta=timedelta(minutes=30)
        )
        
        refresh_token = create_refresh_token(
            data={"sub": user["email"], "user_id": user["_id"]}
        )
        
        return {
            "user": user,
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": 1800
            }
        }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Dict[str, Any]: New tokens
            
        Raises:
            AuthenticationError: If refresh token is invalid
        """
        if not refresh_token:
            raise AuthenticationError("Refresh token is required")
        
        # Verify refresh token
        token_data = verify_refresh_token(refresh_token)
        
        if not token_data:
            raise AuthenticationError("Invalid refresh token")
        
        # Get user to ensure they still exist and are active
        user = await self.user_service.get_user_by_email(token_data.email)
        
        if not user or not user.get("is_active", True):
            raise AuthenticationError("User not found or inactive")
        
        # Create new access token
        access_token = create_access_token(
            data={"sub": user["email"], "user_id": user["_id"]},
            expires_delta=timedelta(minutes=30)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 1800
        }
    
    async def logout(self, refresh_token: str) -> bool:
        """Logout user by invalidating refresh token.
        
        Args:
            refresh_token: Refresh token to invalidate
            
        Returns:
            bool: True if logout successful
            
        Raises:
            AuthenticationError: If refresh token is invalid
        """
        # In a real implementation, you would add the refresh token
        # to a blacklist or revoked tokens list in Redis/database
        # For now, we just verify the token is valid
        
        if not refresh_token:
            raise AuthenticationError("Refresh token is required")
        
        token_data = verify_refresh_token(refresh_token)
        
        if not token_data:
            raise AuthenticationError("Invalid refresh token")
        
        # TODO: Add token to blacklist
        # await self.token_blacklist_service.add_token(refresh_token)
        
        logger.info(f"User logged out: {token_data.email}")
        return True
    
    async def request_password_reset(self, email: str) -> str:
        """Request password reset token.
        
        Args:
            email: User's email
            
        Returns:
            str: Password reset token
            
        Raises:
            ValidationError: If email is invalid
            NotFoundError: If user not found
        """
        if not email:
            raise ValidationError("Email is required")
        
        # Check if user exists
        user = await self.user_service.get_user_by_email(email)
        
        if not user:
            # Don't reveal if user exists or not for security
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return ""
        
        # Generate reset token
        reset_token = generate_password_reset_token(email)
        
        # TODO: Send email with reset token
        # await self.email_service.send_password_reset_email(email, reset_token)
        
        logger.info(f"Password reset requested for: {email}")
        return reset_token
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using reset token.
        
        Args:
            token: Password reset token
            new_password: New password
            
        Returns:
            bool: True if password reset successful
            
        Raises:
            ValidationError: If input is invalid
            AuthenticationError: If token is invalid
            NotFoundError: If user not found
        """
        if not token or not new_password:
            raise ValidationError("Token and new password are required")
        
        if len(new_password) < 6:
            raise ValidationError("Password must be at least 6 characters long")
        
        # Verify token
        email = verify_password_reset_token(token)
        
        if not email:
            raise AuthenticationError("Invalid or expired reset token")
        
        # Get user
        user = await self.user_service.get_user_by_email(email)
        
        if not user:
            raise NotFoundError("User not found")
        
        # Update password
        success = await self.user_service.change_password(
            user_id=user["_id"],
            current_password="",  # Not needed for password reset
            new_password=new_password
        )
        
        if success:
            logger.info(f"Password reset completed for: {email}")
        
        return success
    
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
            ValidationError: If input is invalid
            AuthenticationError: If current password is incorrect
            NotFoundError: If user not found
        """
        return await self.user_service.change_password(
            user_id=user_id,
            current_password=current_password,
            new_password=new_password
        )
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify access token and return user data.
        
        Args:
            token: Access token
            
        Returns:
            Optional[Dict[str, Any]]: User data if token is valid, None otherwise
        """
        token_data = verify_token(token)
        
        if not token_data:
            return None
        
        # Get user to ensure they still exist and are active
        user = await self.user_service.get_user_by_email(token_data.email)
        
        if not user or not user.get("is_active", True):
            return None
        
        return user
