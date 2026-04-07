"""Permission management endpoints."""

from fastapi import APIRouter, HTTPException, status
import logging

from app.database import init_db
from app.auth import verify_user
from app.schemas import UpdatePermissionsRequest, UpdatePermissionsResponse
from app.modules.notes.updatepermissions import update_permissions
from app.constants import ERROR_INVALID_CREDENTIALS

logger = logging.getLogger(__name__)

router = APIRouter(tags=["notes"])

@router.post("/updatepermissions", response_model=UpdatePermissionsResponse, status_code=status.HTTP_200_OK)
def update_permissions_endpoint(request: UpdatePermissionsRequest) -> UpdatePermissionsResponse:
    """Update user permissions for a list."""
    try:
        init_db()
        
        # Authorize the user by verifying email and password
        valid_user = verify_user(request.email, request.password)
        if not valid_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_INVALID_CREDENTIALS,
            )

        # Call the update_permissions function with all parameters from the request
        result = update_permissions(
            requesting_email=request.email,
            requesting_password=request.password,
            list_id=request.list_id,
            target_user_email=request.target_user_email,
            permissions=request.permissions
        )

        return UpdatePermissionsResponse(
            message="Permissions updated successfully",
            target_user_email=result["target_user_email"],
            list_id=result["list_id"],
            updated_permissions=result["updated_permissions"]
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (authentication, etc.)
        raise
    except ValueError as e:
        # Handle validation errors
        logger.warning(f"Validation error in update_permissions_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in update_permissions_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating permissions."
        )
