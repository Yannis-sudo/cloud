"""Account creation endpoints."""

from fastapi import APIRouter, HTTPException, status
from pymongo import errors

from app.database import add_email_server_config
from app.schemas import CreateEmailServerRequest, SuccessResponse
from app.constants import ERROR_EMAIL_EXISTS, SUCCESS_ACCOUNT_CREATED


# Router endpoint
router = APIRouter()
@router.post("/addemailserver", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
def create_account(request: CreateEmailServerRequest) -> SuccessResponse:
    """Create a new email server configuration."""
    success = add_email_server_config(
        imap_server=request.server_incoming,
        smtp_server=request.server_outgoing,
        imap_port=request.server_incoming_port,
        smtp_port=request.server_outgoing_port,
        email=request.email,
        password=request.password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_EMAIL_EXISTS
        )
    
    return SuccessResponse(message=SUCCESS_ACCOUNT_CREATED)
    
