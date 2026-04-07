"""Emails API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.core.security import TokenData
from app.schemas.common import SuccessResponse
from app.dependencies import get_current_user

router = APIRouter()
security = HTTPBearer()


@router.get(
    "/servers",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Get email servers",
    description="Get user's configured email servers"
)
async def get_email_servers(
    current_user: TokenData = Depends(get_current_user)
) -> SuccessResponse:
    """Get email servers."""
    return SuccessResponse(
        message="Email servers retrieved successfully",
        data={"servers": []}
    )
