"""Request and response data schemas."""

from pydantic import BaseModel, EmailStr, Field

# Requests
# Account requests
class CreateAccountRequest(BaseModel):
    """Request model for account creation."""

    email: str
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

    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
            }
        }


# Email requests
class GetEmailsRequest(BaseModel):
    """Request model for retrieving emails."""

    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }

class CreateEmailServerRequest(BaseModel):
    """Request model for adding email server credentials."""

    email: str
    server_incoming: str
    server_outgoing: str
    server_incoming_port: int
    server_outgoing_port: int
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "server_incoming": "imap.gmail.com",
                "server_outgoing": "smtp.gmail.com",
                "server_incoming_port": 993,
                "server_outgoing_port": 587,
                "password": "securepassword123"
            }
        }

class AddFolderRequest(BaseModel):
    """Request model for adding a new folder."""
    
    email: str
    folder_name: str
    password: str # The auth password for the account of this website
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "folder_name": "Important",
                "password": "securepassword123"
            }
        }


# Responses
class SuccessResponse(BaseModel):
    """Generic success response."""

    message: str

class EmailsResponse(BaseModel):
    """Response model for email retrieval."""

    emails: dict
    message: str

class ErrorResponse(BaseModel):
    """Generic error response."""

    message: str
    detail: str | None = None

