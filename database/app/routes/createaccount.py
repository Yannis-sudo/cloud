"""Account creation endpoints."""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import User
from app.schemas import CreateAccountRequest, SuccessResponse
from app.constants import ERROR_EMAIL_EXISTS, SUCCESS_ACCOUNT_CREATED

router = APIRouter(tags=["accounts"])


@router.post("/create-account", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    request: CreateAccountRequest,
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """Create a new user account.
    
    Args:
        request: Account creation request data.
        db: Database session.
        
    Returns:
        SuccessResponse: Success message.
        
    Raises:
        HTTPException: If email already exists or database error occurs.
    """
    new_user = User(
        username=request.username,
        email=request.email,
        password=request.password,
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return SuccessResponse(message=SUCCESS_ACCOUNT_CREATED)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_EMAIL_EXISTS,
        )