"""Email sending routes."""

from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.modules.email.sendemail import send_email
from app.schemas import SendEmailRequest, SendEmailResponse
from app.database import init_db
from app.auth import verify_user
from app.constants import ERROR_INVALID_CREDENTIALS
from fastapi import HTTPException, status
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/send-email", response_model=SendEmailResponse)
async def send_email_endpoint(
    to: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    files: List[UploadFile] = File(default=[])
):
    """Send an email with optional file attachments."""
    try:
        init_db()
        # Authorize the user by verifying email and password
        valid_user = verify_user(email, password)
        if not valid_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_INVALID_CREDENTIALS,
            )

        success = await send_email(
            to=to,
            subject=subject,
            body=body,
            email=email,
            files=files
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
