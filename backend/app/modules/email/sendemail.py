"""Send email module"""

import smtplib
import logging
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.application import MIMEApplication
from email import encoders
from typing import List, Dict, Any, Union
from fastapi import UploadFile

from app.database import get_user_emails

logger = logging.getLogger(__name__)

async def send_email(to: str, subject: str, body: str, email: str, files: List[UploadFile] = None) -> bool:
    """Send an email using SMTP with optional file attachments."""
    # Get the email config data
    config = get_user_emails(email)
    if not config or config == "Email not found":
        logger.error(f"No email configuration found for {email}")
        return False
    
    # Handle case where config is a list (multiple email accounts)
    if isinstance(config, list):
        if not config:
            logger.error(f"Empty email configuration list for {email}")
            return False
        # Use the first email account configuration
        config = config[0]
    
    try:
        # Extract SMTP configuration
        smtp_server = config.get("server_outgoing", "mail.gmx.net")
        smtp_port = config.get("server_outgoing_port", 465)
        email_address = config.get("email", email)
        email_password = config.get("password")
        
        if not email_password:
            logger.error(f"No password found in email configuration for {email}")
            return False
        
        # Create email message
        msg = MIMEMultipart()
        msg["From"] = email_address
        msg["To"] = to
        msg["Subject"] = subject
        
        # Attach body as plain text (remove HTML for now to avoid encoding issues)
        msg.attach(MIMEText(body, "plain"))
        
        # Attach files if provided
        if files:
            for file in files:
                try:
                    # Read file content
                    file_content = await file.read()
                    filename = file.filename or "attachment"
                    
                    # Detect MIME type
                    mime_type, _ = mimetypes.guess_type(filename)
                    if not mime_type:
                        mime_type = "application/octet-stream"
                    
                    main_type, sub_type = mime_type.split("/", 1)
                    
                    # Create appropriate MIME part based on file type
                    if main_type == "text":
                        part = MIMEText(file_content.decode('utf-8'), _subtype=sub_type)
                    elif main_type == "image":
                        part = MIMEImage(file_content, _subtype=sub_type)
                    elif main_type == "audio":
                        part = MIMEAudio(file_content, _subtype=sub_type)
                    elif main_type == "application":
                        part = MIMEApplication(file_content, _subtype=sub_type)
                    else:
                        # Fallback to generic base attachment
                        part = MIMEBase(main_type, sub_type)
                        part.set_payload(file_content)
                        encoders.encode_base64(part)
                    
                    # Add header with filename
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={filename}",
                    )
                    
                    msg.attach(part)
                    logger.info(f"Attached file: {filename} (type: {mime_type})")
                    
                except Exception as e:
                    logger.error(f"Error attaching file {file.filename}: {e}")
                    # Continue with other files even if one fails
                    continue
        
        # Send email using SMTP SSL (Port 465)
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(email_address, email_password)
            server.sendmail(email_address, to, msg.as_string())
        
        logger.info(f"Email successfully sent from {email_address} to {to} with {len(files) if files else 0} attachments")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication error for {email}: {e}")
        return False
    except smtplib.SMTPConnectError as e:
        logger.error(f"SMTP connection error for {smtp_server}:{smtp_port}: {e}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error for {email}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email from {email}: {e}")
        return False