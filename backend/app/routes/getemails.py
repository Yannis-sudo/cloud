"""Account creation endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.database import init_db, get_user_emails
from app.auth import get_user_by_email, verify_user
from app.schemas import EmailsResponse, GetEmailsRequest
from app.modules.loademails import load_emails
from constants import ERROR_INVALID_CREDENTIALS, EMAIL_NOT_FOUND

router = APIRouter(tags=["accounts"])


@router.post("/getemails", response_model=EmailsResponse, status_code=status.HTTP_201_CREATED)
def get_emails(request: GetEmailsRequest) -> EmailsResponse:
    """Retrieve emails."""
    init_db()
    valid_user = verify_user(request.email, request.password)
    if not valid_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_INVALID_CREDENTIALS,
        )

    user = get_user_by_email(request.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EMAIL_NOT_FOUND,
        )

    email_records = get_user_emails(request.email)
    # load_emails can optionally process external mailbox retrieval workflow
    load_emails(request.email)

    return EmailsResponse(
        emails=[
            {
                "id": str(record.get("_id")),
                "email": record.get("email"),
                "server": record.get("server"),
                "password": record.get("password"),
            }
            for record in email_records
        ],
        message="Emails retrieved successfully",
    )