"""Authentication schemas for API requests and responses."""

from pydantic import BaseModel, Field, EmailStr, ConfigDict, AliasChoices
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Request model for user login."""
    
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }


class RegisterRequest(BaseModel):
    """Request model for user registration."""

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "john_doe",
                "email": "user@example.com",
                "password": "securepassword123",
                "first_name": "John",
                "last_name": "Doe"
            }
        },
    )

    username: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Username",
        validation_alias=AliasChoices("name", "username"),
    )
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, max_length=128, description="Password")
    first_name: Optional[str] = Field(None, max_length=255, description="First name")
    last_name: Optional[str] = Field(None, max_length=255, description="Last name")


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class PasswordResetRequest(BaseModel):
    """Request model for password reset."""
    
    email: EmailStr = Field(..., description="User's email address")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordResetConfirmRequest(BaseModel):
    """Request model for password reset confirmation."""
    
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=6, max_length=128, description="New password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "new_password": "newsecurepassword123"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Request model for changing password."""
    
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=6, max_length=128, description="New password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newpassword123"
            }
        }


class UserResponse(BaseModel):
    """Response model for user information."""
    
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    is_active: bool = Field(..., description="Whether user is active")
    is_verified: bool = Field(..., description="Whether user is verified")
    created_at: datetime = Field(..., description="Account creation date")
    last_login: Optional[datetime] = Field(None, description="Last login date")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "username": "john_doe",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "is_verified": True,
                "created_at": "2023-01-01T00:00:00Z",
                "last_login": "2023-01-15T12:30:00Z"
            }
        }


class LoginResponse(BaseModel):
    """Response model for successful login."""
    
    message: str = Field(..., description="Success message")
    user: UserResponse = Field(..., description="User information")
    tokens: TokenResponse = Field(..., description="Authentication tokens")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Login successful",
                "user": {
                    "id": "507f1f77bcf86cd799439011",
                    "username": "john_doe",
                    "email": "user@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "is_active": True,
                    "is_verified": True,
                    "created_at": "2023-01-01T00:00:00Z",
                    "last_login": "2023-01-15T12:30:00Z"
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 1800
                }
            }
        }


class LogoutResponse(BaseModel):
    """Response model for logout."""
    
    message: str = Field(..., description="Success message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Logout successful"
            }
        }
