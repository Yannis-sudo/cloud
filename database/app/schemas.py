"""Request and response data schemas."""

from pydantic import BaseModel, EmailStr, Field


class CreateAccountRequest(BaseModel):
    """Request model for account creation."""

    email: EmailStr
    username: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=6)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "john_doe",
                "password": "securepassword123",
            }
        }


class LoginRequest(BaseModel):
    """Request model for user login."""

    email: EmailStr
    password: str = Field(..., min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
            }
        }


class SuccessResponse(BaseModel):
    """Generic success response."""

    message: str


class ErrorResponse(BaseModel):
    """Generic error response."""

    message: str
    detail: str | None = None
