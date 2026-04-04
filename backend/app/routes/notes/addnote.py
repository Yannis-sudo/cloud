"""Note management endpoints."""

from fastapi import APIRouter, HTTPException, status
import logging

from app.database import init_db
from app.auth import verify_user
from app.schemas import AddNoteRequest, SuccessResponse
from app.modules.notes.addnote import add_note
from app.constants import ERROR_INVALID_CREDENTIALS

logger = logging.getLogger(__name__)

router = APIRouter(tags=["notes"])

@router.post("/addnote", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
def add_note_endpoint(request: AddNoteRequest) -> SuccessResponse:
    """Add a new note."""
    try:
        init_db()
        # Authorize the user by verifying username and password
        valid_user = verify_user(request.username, request.password)
        if not valid_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_INVALID_CREDENTIALS,
            )

        # Call the add_note function with all parameters from the request
        add_note(
            username=request.username,
            password=request.password,
            title=request.title,
            description=request.description,
            priority=request.priority,
            author_name=request.author_name,
            author_email=request.author_email,
            list=request.list
        )

        return SuccessResponse(message="Note added successfully")
        
    except HTTPException:
        # Re-raise HTTP exceptions (authentication, etc.)
        raise
    except ValueError as e:
        # Handle permission and validation errors
        logger.warning(f"Permission/validation error in add_note_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in add_note_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding the note."
        )