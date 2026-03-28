"""Account creation endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.database import init_db, get_user_emails
from app.auth import get_user_by_email, verify_user
from app.schemas import EmailsResponse, GetEmailsRequest
from app.modules.loademails import load_emails
from app.constants import ERROR_INVALID_CREDENTIALS, EMAIL_NOT_FOUND

router = APIRouter(tags=["accounts"])


@router.post("/getemails", response_model=EmailsResponse, status_code=status.HTTP_201_CREATED)
def get_emails(request: GetEmailsRequest) -> EmailsResponse:
    """Retrieve emails."""
    # Initialize the database
    init_db()
    # Authorize the user by verifying email and password
    valid_user = verify_user(request.email, request.password)
    if not valid_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_INVALID_CREDENTIALS,
        )

    # Check if the email address is saved in the email_addresses collection
    email_record = get_user_emails(request.email)
    if not email_record or email_record == "Email not found":
        return EmailsResponse(
            emails=[],
            message=EMAIL_NOT_FOUND,
        )

    # If email is found, run the function to load emails from the email server
    email_data = load_emails(request.email)
    
    # Check if email data was successfully retrieved
    if not email_data:
        return EmailsResponse(
            emails=[],
            message="Failed to load emails from server",
        )

    # Return the emails and folders retrieved from the server
    return EmailsResponse(
        emails=email_data,
        message="Emails retrieved successfully",
    )