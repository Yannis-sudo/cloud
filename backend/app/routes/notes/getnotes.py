"""Note retrieval endpoints."""

from fastapi import APIRouter, HTTPException, status
import logging

from app.database import init_db
from app.auth import verify_user
from app.schemas import GetNotesRequest, GetNotesResponse
from app.modules.notes.getnotes import get_notes
from app.constants import ERROR_INVALID_CREDENTIALS

logger = logging.getLogger(__name__)

router = APIRouter(tags=["notes"])

@router.post("/getnotes", response_model=GetNotesResponse, status_code=status.HTTP_200_OK)
def get_notes_endpoint(request: GetNotesRequest) -> GetNotesResponse:
    """Get all notes from a specific list that the user has permission to view."""
    try:
        init_db()
        # Authorize the user by verifying email and password
        valid_user = verify_user(request.email, request.password)
        if not valid_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_INVALID_CREDENTIALS,
            )

        # Call the get_notes function with pagination parameters
        notes_result = get_notes(
            email=request.email,
            password=request.password,
            list_id=request.list_id,
            page=request.page,
            page_size=request.page_size
        )

        return GetNotesResponse(
            notes=notes_result["notes"],
            total_count=notes_result["total_count"],
            page=notes_result["page"],
            page_size=notes_result["page_size"],
            total_pages=notes_result["total_pages"],
            message="Notes retrieved successfully"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (authentication, etc.)
        raise
    except ValueError as e:
        # Handle validation and permission errors
        logger.warning(f"Permission/validation error in get_notes_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_notes_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the notes."
        )
