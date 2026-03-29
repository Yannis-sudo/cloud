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
    parent_folder: str | None = None  # Optional parent folder for creating subfolders
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "folder_name": "Important",
                "password": "securepassword123",
                "parent_folder": None
            }
        }

class SendEmailRequest(BaseModel):
    """Request model for sending an email."""

    to: EmailStr
    subject: str
    body: str
    email: str # The sender's email address (the account associated with this website)
    password: str # The auth password for the account of this website

    class Config:
        json_schema_extra = {
            "example": {
                "to": "recipient@example.com",
                "subject": "Test Email",
                "body": "This is a test email.",
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }

class GetFoldersRequest(BaseModel):
    """Request model for retrieving email folders."""
    
    email: str
    password: str # The auth password for the account of this website
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
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

class GetFoldersResponse(BaseModel):
    """Response model for retrieving email folders."""
    
    folders: list[str]

class SendEmailResponse(BaseModel):
    """Response model for sending an email."""

    success: bool