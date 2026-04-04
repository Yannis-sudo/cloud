"""List retrieval endpoints."""

from fastapi import APIRouter, HTTPException, status
import logging

from app.database import init_db
from app.auth import verify_user
from app.schemas import GetListsRequest, GetListsResponse
from app.modules.notes.getlists import get_lists
from app.constants import ERROR_INVALID_CREDENTIALS

logger = logging.getLogger(__name__)

router = APIRouter(tags=["notes"])

@router.post("/getlists", response_model=GetListsResponse, status_code=status.HTTP_200_OK)
def get_lists_endpoint(request: GetListsRequest) -> GetListsResponse:
    """Get all lists that the user has permission to view."""
    try:
        init_db()
        # Authorize the user by verifying email and password
        valid_user = verify_user(request.email, request.password)
        if not valid_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_INVALID_CREDENTIALS,
            )

        # Call the get_lists function with pagination parameters
        lists_result = get_lists(
            email=request.email,
            password=request.password,
            page=request.page,
            page_size=request.page_size
        )

        return GetListsResponse(
            lists=lists_result["lists"],
            total_count=lists_result["total_count"],
            page=lists_result["page"],
            page_size=lists_result["page_size"],
            total_pages=lists_result["total_pages"],
            message="Lists retrieved successfully"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (authentication, etc.)
        raise
    except ValueError as e:
        # Handle validation errors
        logger.warning(f"Validation error in get_lists_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_lists_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the lists."
        )