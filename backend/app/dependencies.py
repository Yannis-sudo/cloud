"""Dependency injection for FastAPI."""

from functools import lru_cache
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo import MongoClient
from pymongo.database import Database
from bson import ObjectId

from app.config import get_settings
from app.core.security import verify_token, TokenData
from app.core.exceptions import AuthenticationError, DatabaseError
from app.database.connection import get_database, get_mongo_client

settings = get_settings()
security = HTTPBearer()


def get_db() -> Generator[Database, None, None]:
    """Get database dependency.
    
    Yields:
        Database: MongoDB database instance
    """
    try:
        db = get_database()
        yield db
    except Exception as e:
        raise DatabaseError(f"Database connection failed: {str(e)}")


def get_mongo_client_dep() -> Generator[MongoClient, None, None]:
    """Get MongoDB client dependency.
    
    Yields:
        MongoClient: MongoDB client instance
    """
    try:
        client = get_mongo_client()
        yield client
    except Exception as e:
        raise DatabaseError(f"MongoDB client connection failed: {str(e)}")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        TokenData: Current user token data
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token_data = verify_token(credentials.credentials)
        if token_data is None:
            raise credentials_exception
        return token_data
    except Exception:
        raise credentials_exception


def get_current_active_user(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """Get current active user (for future use with user status).
    
    Args:
        current_user: Current user token data
        
    Returns:
        TokenData: Current active user token data
    """
    # Future: Add user status check here
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[TokenData]:
    """Get current user if authenticated, otherwise return None.
    
    Args:
        credentials: Optional HTTP authorization credentials
        
    Returns:
        Optional[TokenData]: Current user token data or None
    """
    if credentials is None:
        return None
    
    try:
        return verify_token(credentials.credentials)
    except Exception:
        return None


def validate_object_id(id: str) -> ObjectId:
    """Validate and convert string to ObjectId.
    
    Args:
        id: String ID to validate
        
    Returns:
        ObjectId: Valid ObjectId
        
    Raises:
        HTTPException: If ID is invalid
    """
    try:
        return ObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ID format: {id}"
        )


@lru_cache()
def get_user_repository():
    """Get cached user repository instance.
    
    Returns:
        UserRepository: User repository instance
    """
    from app.database.repositories.users import UserRepository
    return UserRepository()


@lru_cache()
def get_email_repository():
    """Get cached email repository instance.
    
    Returns:
        EmailRepository: Email repository instance
    """
    from app.database.repositories.emails import EmailRepository
    return EmailRepository()


@lru_cache()
def get_notes_repository():
    """Get cached notes repository instance.
    
    Returns:
        NotesRepository: Notes repository instance
    """
    from app.database.repositories.notes import NotesRepository
    return NotesRepository()


@lru_cache()
def get_files_repository():
    """Get cached files repository instance.
    
    Returns:
        FilesRepository: Files repository instance
    """
    from app.database.repositories.files import FilesRepository
    return FilesRepository()


def get_user_service():
    """Get user service instance.
    
    Returns:
        UserService: User service instance
    """
    from app.modules.users.service import UserService
    return UserService()


def get_email_service():
    """Get email service instance.
    
    Returns:
        EmailService: Email service instance
    """
    from app.modules.emails.service import EmailService
    return EmailService()


def get_notes_service():
    """Get notes service instance.
    
    Returns:
        NotesService: Notes service instance
    """
    from app.modules.notes.service import NotesService
    return NotesService()


def get_files_service():
    """Get files service instance.
    
    Returns:
        FilesService: Files service instance
    """
    from app.modules.files.service import FilesService
    return FilesService()
