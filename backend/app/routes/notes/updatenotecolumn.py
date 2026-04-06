"""Note column update endpoints."""

from fastapi import APIRouter, HTTPException, status
import logging

from app.database import init_db
from app.auth import verify_user
from app.schemas import UpdateNoteColumnRequest, SuccessResponse
from app.modules.notes.updatenotecolumn import update_note_column
from app.constants import ERROR_INVALID_CREDENTIALS

logger = logging.getLogger(__name__)

router = APIRouter(tags=["notes"])

@router.put("/updatenotecolumn", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
def update_note_column_endpoint(request: UpdateNoteColumnRequest) -> SuccessResponse:
    """Update the column of an existing note."""
    try:
        init_db()
        # Authorize the user by verifying email and password
        valid_user = verify_user(request.email, request.password)
        if not valid_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_INVALID_CREDENTIALS,
            )

        # Call the update_note_column function with all parameters from the request
        update_note_column(
            username=request.email,  # Use email as username for consistency
            password=request.password,
            note_id=request.note_id,
            new_column=request.new_column
        )

        return SuccessResponse(message="Note column updated successfully")
        
    except HTTPException:
        # Re-raise HTTP exceptions (authentication, etc.)
        raise
    except ValueError as e:
        # Handle permission and validation errors
        logger.warning(f"Permission/validation error in update_note_column_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in update_note_column_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the note column."
        )
