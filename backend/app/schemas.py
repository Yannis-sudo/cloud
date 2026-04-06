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

class LoginResponse(BaseModel):
    """Response model for successful user login."""

    message: str
    username: str
    email: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Login successful",
                "username": "john_doe",
                "email": "user@example.com"
            }
        }


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

# Notes requests
class AddNoteRequest(BaseModel):
    """Request model for adding a new note."""

    email: str  # The email for authentication
    password: str  # The auth password for the account
    title: str
    description: str
    priority: str = Field(..., pattern="^(low|medium|high)$")
    author_name: str
    author_email: EmailStr
    list_id: str  # Use list_id instead of list array
    column: str = Field(default="todo", pattern="^(backlog|todo|in-progress|done)$")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "securepassword123",
                "title": "Meeting Notes",
                "description": "Important points from the team meeting",
                "priority": "high",
                "author_name": "John Doe",
                "author_email": "john@example.com",
                "list_id": "507f1f77bcf86cd799439011",
                "column": "todo"
            }
        }

class AddListRequest(BaseModel):
    """Request model for adding a new list."""

    email: str  # The email for authentication
    password: str  # The auth password for the account
    list_name: str
    creator_email: EmailStr
    description: str = ""

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "securepassword123",
                "list_name": "Project Tasks",
                "creator_email": "john@example.com",
                "description": "Tasks related to the current project"
            }
        }

class AddListResponse(BaseModel):
    """Response model for adding a new list."""

    list_id: str
    list_name: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "list_id": "507f1f77bcf86cd799439011",
                "list_name": "Project Tasks",
                "message": "List added successfully"
            }
        }

class GetListsRequest(BaseModel):
    """Request model for retrieving user's lists."""

    email: str  # The email for authentication
    password: str  # The auth password for the account
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "securepassword123",
                "page": 1,
                "page_size": 20
            }
        }

class ListInfo(BaseModel):
    """Model for individual list information."""

    list_id: str
    list_name: str
    description: str = ""
    created_by: str
    admins: list[str]
    created_at: str | None = None
    updated_at: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "list_id": "507f1f77bcf86cd799439011",
                "list_name": "Project Tasks",
                "description": "Tasks related to the current project",
                "created_by": "john@example.com",
                "admins": ["john@example.com", "admin@example.com"],
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
        }

class GetListsResponse(BaseModel):
    """Response model for retrieving user's lists."""

    lists: list[ListInfo]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "lists": [
                    {
                        "list_id": "507f1f77bcf86cd799439011",
                        "list_name": "Project Tasks",
                        "description": "Tasks related to the current project",
                        "created_by": "john@example.com",
                        "admins": ["john@example.com"],
                        "created_at": "2023-01-01T00:00:00Z",
                        "updated_at": "2023-01-01T00:00:00Z"
                    }
                ],
                "total_count": 1,
                "page": 1,
                "page_size": 20,
                "total_pages": 1,
                "message": "Lists retrieved successfully"
            }
        }

class GetNotesRequest(BaseModel):
    """Request model for retrieving notes from a specific list."""

    email: str  # The email for authentication
    password: str  # The auth password for the account
    list_id: str  # The ID of the list to retrieve notes from
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "securepassword123",
                "list_id": "507f1f77bcf86cd799439011",
                "page": 1,
                "page_size": 20
            }
        }

class NoteInfo(BaseModel):
    """Model for individual note information."""

    note_id: str
    title: str
    description: str
    priority: str = Field(..., pattern="^(low|medium|high)$")
    author_name: str
    author_email: str
    list_id: str
    column: str = Field(..., pattern="^(backlog|todo|in-progress|done)$")
    created_at: str | None = None
    updated_at: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "note_id": "507f1f77bcf86cd799439012",
                "title": "Meeting Notes",
                "description": "Important points from the team meeting",
                "priority": "high",
                "author_name": "John Doe",
                "author_email": "john@example.com",
                "list_id": "507f1f77bcf86cd799439011",
                "column": "todo",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
        }

class GetNotesResponse(BaseModel):
    """Response model for retrieving notes from a specific list."""

    notes: list[NoteInfo]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "notes": [
                    {
                        "note_id": "507f1f77bcf86cd799439012",
                        "title": "Meeting Notes",
                        "description": "Important points from the team meeting",
                        "priority": "high",
                        "author_name": "John Doe",
                        "author_email": "john@example.com",
                        "list_id": "507f1f77bcf86cd799439011",
                        "created_at": "2023-01-01T00:00:00Z",
                        "updated_at": "2023-01-01T00:00:00Z"
                    }
                ],
                "total_count": 1,
                "page": 1,
                "page_size": 20,
                "total_pages": 1,
                "message": "Notes retrieved successfully"
            }
        }