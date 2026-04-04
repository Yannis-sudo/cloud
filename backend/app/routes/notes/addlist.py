"""List management endpoints."""

from fastapi import APIRouter, HTTPException, status
import logging

from app.database import init_db
from app.auth import verify_user
from app.schemas import AddListRequest, AddListResponse
from app.modules.notes.addlist import add_list
from app.constants import ERROR_INVALID_CREDENTIALS

logger = logging.getLogger(__name__)

router = APIRouter(tags=["notes"])

@router.post("/addlist", response_model=AddListResponse, status_code=status.HTTP_201_CREATED)
def add_list_endpoint(request: AddListRequest) -> AddListResponse:
    """Add a new list."""
    try:
        init_db()
        # Authorize the user by verifying email and password
        valid_user = verify_user(request.email, request.password)
        if not valid_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_INVALID_CREDENTIALS,
            )

        # Call the add_list function with all parameters from the request
        list_info = add_list(
            email=request.email,
            password=request.password,
            list_name=request.list_name,
            creator_email=request.creator_email,
            description=request.description
        )

        return AddListResponse(
            list_id=list_info["list_id"],
            list_name=list_info["list_name"],
            message="List added successfully"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (authentication, etc.)
        raise
    except ValueError as e:
        # Handle validation errors
        logger.warning(f"Validation error in add_list_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in add_list_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding the list."
        )