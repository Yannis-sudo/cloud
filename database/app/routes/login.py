"""User authentication endpoints."""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, SuccessResponse
from app.constants import ERROR_INVALID_CREDENTIALS, SUCCESS_LOGIN

router = APIRouter(tags=["auth"])

@router.post("/login", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """Authenticate a user.
    
    Args:
        request: Login credentials.
        db: Database session.
        
    Returns:
        SuccessResponse: Success message.
        
    Raises:
        HTTPException: If credentials are invalid.
    """
    user = db.query(User).filter(User.email == request.email).first()

    if not user or user.password != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_INVALID_CREDENTIALS,
        )

    return SuccessResponse(message=SUCCESS_LOGIN)
    