"""Email sending routes."""

from fastapi import APIRouter, Depends
from app.modules.email.sendemail import send_email
from app.schemas import SendEmailRequest, SendEmailResponse
from app.database import init_db
from app.auth import verify_user
from app.constants import ERROR_INVALID_CREDENTIALS
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/send-email", response_model=SendEmailResponse)
async def send_email_endpoint(request: SendEmailRequest):
    """Send an email."""
    try:
        init_db()
        # Authorize the user by verifying email and password
        valid_user = verify_user(request.email, request.password)
        if not valid_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_INVALID_CREDENTIALS,
            )

        success = send_email(
            to=request.to,
            subject=request.subject,
            body=request.body,
            email=request.email
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email. Please check your email configuration and try again."
            )
            
        return SendEmailResponse(success=True)
        
    except HTTPException:
        # Re-raise HTTP exceptions (authentication, etc.)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in send_email_endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while sending the email."
        )
