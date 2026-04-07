"""Notes API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.core.security import TokenData
from app.schemas.common import SuccessResponse
from app.dependencies import get_current_user

router = APIRouter()
security = HTTPBearer()


@router.get(
    "/lists",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Get notes lists",
    description="Get user's notes lists"
)
async def get_notes_lists(
    current_user: TokenData = Depends(get_current_user)
) -> SuccessResponse:
    """Get notes lists."""
    return SuccessResponse(
        message="Notes lists retrieved successfully",
        data={"lists": []}
    )
