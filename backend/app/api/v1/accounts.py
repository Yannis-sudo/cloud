"""Accounts API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.core.security import TokenData
from app.schemas.common import SuccessResponse
from app.dependencies import get_current_user

router = APIRouter()
security = HTTPBearer()


@router.get(
    "/profile",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user profile",
    description="Get the current user's profile information"
)
async def get_profile(
    current_user: TokenData = Depends(get_current_user)
) -> SuccessResponse:
    """Get user profile."""
    return SuccessResponse(
        message="Profile retrieved successfully",
        data={"user_id": current_user.user_id, "email": current_user.email}
    )
