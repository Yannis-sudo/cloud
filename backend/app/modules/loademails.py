from app.database import get_user_emails


def load_emails(email: str):
    """Load emails from the email server. Currently empty, to be implemented later."""
    # TODO: Implement fetching emails from the email server using the email credentials
    # Get the email records from DB to get server, email, password
    email_records = get_user_emails(email)
    if email_records == "Email not found":
        return []
    
    # For now, return empty list as placeholder
    return []