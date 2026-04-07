"""Get permissions endpoints."""

from fastapi import APIRouter, HTTPException, status
import logging

from app.database import init_db
from app.auth import verify_user
from app.schemas import GetPermissionsRequest, GetPermissionsResponse, UserPermission
from app.modules.notes.getpermissions import get_permissions
from app.constants import ERROR_INVALID_CREDENTIALS

logger = logging.getLogger(__name__)

router = APIRouter(tags=["notes"])

@router.post("/getpermissions", response_model=GetPermissionsResponse, status_code=status.HTTP_200_OK)
def get_permissions_endpoint(request: GetPermissionsRequest) -> GetPermissionsResponse:
    """Get all users with permissions for a list."""
    try:
        init_db()
        
        # Authorize the user by verifying email and password
        valid_user = verify_user(request.email, request.password)
        if not valid_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_INVALID_CREDENTIALS,
            )

        # Call the get_permissions function with all parameters from the request
        result = get_permissions(
            requesting_email=request.email,
            requesting_password=request.password,
            list_id=request.list_id
        )

        # Convert the result to match the response schema
        users = []
        for user_data in result["users"]:
            users.append(UserPermission(
                email=user_data["email"],
                username=user_data["username"],
                permissions=user_data["permissions"]
            ))

        return GetPermissionsResponse(
            message="Permissions retrieved successfully",
            list_id=result["list_id"],
            users=users
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (authentication, etc.)
        raise
    except ValueError as e:
        # Handle validation errors
        logger.warning(f"Validation error in get_permissions_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_permissions_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving permissions."
        )
