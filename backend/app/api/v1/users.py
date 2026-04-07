"""Users API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.core.security import TokenData
from app.schemas.common import SuccessResponse
from app.dependencies import get_current_user

router = APIRouter()
security = HTTPBearer()


@router.get(
    "/search",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Search users",
    description="Search for users by username or email"
)
async def search_users(
    query: str = "",
    current_user: TokenData = Depends(get_current_user)
) -> SuccessResponse:
    """Search users."""
    return SuccessResponse(
        message="Users search completed",
        data={"query": query, "results": []}
    )
