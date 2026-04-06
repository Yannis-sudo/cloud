"""User authentication endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.database import init_db
from app.auth import verify_user, get_user_by_email
from app.schemas import LoginRequest, LoginResponse
from app.constants import ERROR_INVALID_CREDENTIALS, SUCCESS_LOGIN

router = APIRouter(tags=["auth"])

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(request: LoginRequest) -> LoginResponse:
    """Authenticate a user."""
    init_db()
    if not verify_user(request.email, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_INVALID_CREDENTIALS,
        )

    # Get user details to return username and email
    user = get_user_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_INVALID_CREDENTIALS,
        )

    return LoginResponse(
        message=SUCCESS_LOGIN,
        username=user["username"],
        email=user["email"]
    )
    