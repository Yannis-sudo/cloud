"""Security utilities for authentication and authorization."""

import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.config import get_settings

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """Token data model for JWT validation."""
    email: Optional[str] = None
    user_id: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt.
    
    Args:
        password: The plain text password
        
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token.
    
    Args:
        data: The data to encode in the token
        
    Returns:
        str: The encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT token.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        TokenData: The decoded token data, or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if email is None:
            return None
            
        token_data = TokenData(email=email, user_id=user_id)
        return token_data
    except JWTError:
        return None


def verify_refresh_token(token: str) -> Optional[TokenData]:
    """Verify and decode a refresh token.
    
    Args:
        token: The refresh token to verify
        
    Returns:
        TokenData: The decoded token data, or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_type: str = payload.get("type")
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if token_type != "refresh" or email is None:
            return None
            
        token_data = TokenData(email=email, user_id=user_id)
        return token_data
    except JWTError:
        return None


def generate_password_reset_token(email: str) -> str:
    """Generate a password reset token.
    
    Args:
        email: The user's email
        
    Returns:
        str: The password reset token
    """
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode = {"exp": expire, "sub": email, "type": "password_reset"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify a password reset token.
    
    Args:
        token: The password reset token
        
    Returns:
        str: The user's email if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_type: str = payload.get("type")
        email: str = payload.get("sub")
        
        if token_type != "password_reset" or email is None:
            return None
            
        return email
    except JWTError:
        return None
