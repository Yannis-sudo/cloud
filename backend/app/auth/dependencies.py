"""Dependencies for route protection and user injection."""

from typing import Optional, Callable
from fastapi import Depends
from fastapi_users import FastAPIUsers
from app.auth.models import User


# This will be populated by the routes module
_fastapi_users: Optional[FastAPIUsers] = None


def set_fastapi_users(fastapi_users: FastAPIUsers) -> None:
    """Set the FastAPIUsers instance (called from routes module).
    
    Args:
        fastapi_users: FastAPIUsers instance
    """
    global _fastapi_users
    _fastapi_users = fastapi_users


def get_current_user() -> Callable:
    """Get current authenticated user (may be inactive).
    
    Returns:
        Callable: Dependency that returns User object
        
    Raises:
        HTTPException 401: If not authenticated
    """
    if _fastapi_users is None:
        raise RuntimeError("FastAPIUsers not initialized")
    return _fastapi_users.current_user()


def get_current_active_user() -> Callable:
    """Get current active authenticated user.
    
    Returns:
        Callable: Dependency that returns User object
        
    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If user is inactive
    """
    if _fastapi_users is None:
        raise RuntimeError("FastAPIUsers not initialized")
    return _fastapi_users.current_user(active=True)


def get_current_superuser() -> Callable:
    """Get current authenticated superuser.
    
    Returns:
        Callable: Dependency that returns User object
        
    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If user is not a superuser
    """
    if _fastapi_users is None:
        raise RuntimeError("FastAPIUsers not initialized")
    return _fastapi_users.current_user(superuser=True)


def get_optional_current_user() -> Callable:
    """Get current user if authenticated, otherwise None.
    
    Returns:
        Callable: Dependency that returns Optional[User]
    """
    if _fastapi_users is None:
        raise RuntimeError("FastAPIUsers not initialized")
    return _fastapi_users.current_user(optional=True)
