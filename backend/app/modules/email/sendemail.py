"""Send email module"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Union

from app.database import get_user_emails

logger = logging.getLogger(__name__)

def send_email(to: str, subject: str, body: str, email: str) -> bool:
    """Send an email using SMTP."""
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
        
        # Attach body
        msg.attach(MIMEText(body, "plain"))
        
        # Send email using SMTP SSL (Port 465)
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(email_address, email_password)
            server.sendmail(email_address, to, msg.as_string())
        
        logger.info(f"Email successfully sent from {email_address} to {to}")
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