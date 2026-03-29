"""In this module, we will implement the logic to add a new folder to the email server."""

import imaplib
from app.database import get_user_emails


def add_new_folder(email: str, folder_name: str) -> bool:
    """Add a new folder to the email server."""
    # get email configuration
    config = get_user_emails(email)
    
    if not config or config == "Email not found":
        return False
    
    try:
        # Extract server details from config
        imap_server = config.get("imap_server")
        imap_port = config.get("imap_port", 993)
        password = config.get("password")
        
        if not imap_server or not password:
            return False
        
        # Connect to IMAP server
        imap = imaplib.IMAP4_SSL(imap_server, imap_port)
        
        # Login
        imap.login(email, password)
        
        # Create folder
        status, response = imap.create(folder_name)
        
        # Close connection
        imap.logout()
        
        # Return True if folder was created successfully
        return status == "OK"
        
    except Exception as e:
        print(f"Error creating folder: {e}")
        return False
    

