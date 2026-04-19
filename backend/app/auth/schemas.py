"""Pydantic schemas for authentication endpoints."""

from typing import Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr, Field, AliasChoices
from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate


class UserRead(BaseUser[PydanticObjectId]):
    """Schema for reading user data in responses.
    
    Includes:
    - id: ObjectId
    - email: str
    - username: str
    - is_active: bool
    - is_verified: bool
    - is_superuser: bool (not exposed by default)
    """
    username: str = Field(
        ...,
        description="Full name of the user",
        validation_alias=AliasChoices("username", "name"),
        serialization_alias="username",
    )


class UserCreate(BaseUserCreate):
    """Schema for creating a new user (registration request).
    
    Requires:
    - email: str
    - password: str (at least 8 chars)
    - username: str
    """
    email: EmailStr = Field(..., description="Email address (must be unique)")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    username: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Full name of the user",
        validation_alias=AliasChoices("username", "name"),
        serialization_alias="username",
    )


class UserUpdate(BaseUserUpdate):
    """Schema for updating user data.
    
    Optional fields:
    - password: str (if updating password)
    - username: str (if updating name)

    Note: Email update is not allowed through this endpoint for security.
    """
    username: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Full name of the user",
        validation_alias=AliasChoices("username", "name"),
        serialization_alias="username",
    )



# Additional helper schemas

class LoginRequest(BaseModel):
    """Request schema for login endpoint."""
    username: str = Field(..., description="Email address for login")
    password: str = Field(..., description="Password")


class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = True
    message: str
    data: Optional[object] = None


class ErrorResponse(BaseModel):
    """Generic error response."""
    success: bool = False
    message: str
    error_code: Optional[str] = None
