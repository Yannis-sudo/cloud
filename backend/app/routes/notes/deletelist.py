"""List deletion endpoints."""

from fastapi import APIRouter, HTTPException, status
import logging

from app.database import init_db
from app.auth import verify_user
from app.schemas import DeleteListRequest, DeleteListResponse
from app.modules.notes.deletelist import delete_list
from app.constants import ERROR_INVALID_CREDENTIALS

logger = logging.getLogger(__name__)

router = APIRouter(tags=["notes"])

@router.post("/deletelist", response_model=DeleteListResponse, status_code=status.HTTP_200_OK)
def delete_list_endpoint(request: DeleteListRequest) -> DeleteListResponse:
    """Delete a list that the user has admin permissions for."""
    try:
        init_db()
        # Authorize the user by verifying email and password
        valid_user = verify_user(request.email, request.password)
        if not valid_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_INVALID_CREDENTIALS,
            )

        # Call the delete_list function
        result = delete_list(
            email=request.email,
            password=request.password,
            list_id=request.list_id
        )

        return DeleteListResponse(
            message=result["message"],
            list_id=result["list_id"]
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (authentication, etc.)
        raise
    except ValueError as e:
        # Handle validation errors
        logger.warning(f"Validation error in delete_list_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in delete_list_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the list."
        )
