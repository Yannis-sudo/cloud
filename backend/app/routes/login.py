"""User authentication endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.database import init_db
from app.auth import verify_user
from app.schemas import LoginRequest, SuccessResponse
from app.constants import ERROR_INVALID_CREDENTIALS, SUCCESS_LOGIN

router = APIRouter(tags=["auth"])

@router.post("/login", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
def login(request: LoginRequest) -> SuccessResponse:
    """Authenticate a user."""
    init_db()
    if not verify_user(request.email, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_INVALID_CREDENTIALS,
        )

    return SuccessResponse(message=SUCCESS_LOGIN)
    