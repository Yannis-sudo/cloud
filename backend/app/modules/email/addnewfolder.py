"""In this module, we will implement the logic to add a new folder to the email server."""

import imaplib
from app.database import get_user_emails


def add_new_folder(email: str, folder_name: str, parent_folder: str = None) -> bool:
    """Add a new folder to the email server."""
    # get email configuration
    configs = get_user_emails(email)
    
    print(f"Debug: configs = {configs}")
    print(f"Debug: type(configs) = {type(configs)}")
    
    if not configs or configs == "Email not found" or not isinstance(configs, list):
        print("Debug: Failed validation check")
        return False
    
    if len(configs) == 0:
        print("Debug: Empty configs list")
        return False
    
    # Use the first email configuration
    config = configs[0]
    print(f"Debug: First config = {config}")
    
    try:
        # Extract server details from config
        imap_server = config.get("server_incoming")
        imap_port = config.get("server_incoming_port", 993)
        password = config.get("password")
        
        print(f"Debug: imap_server = {imap_server}, imap_port = {imap_port}")
        print(f"Debug: password exists = {bool(password)}")
        
        if not imap_server or not password:
            print("Debug: Missing imap_server or password")
            return False
        
        # Sanitize and format folder name for IMAP
        folder_name = folder_name.strip()
        print(f"Debug: Original folder name: '{folder_name}'")
        
        # Build full folder path if parent folder is specified
        if parent_folder and parent_folder.strip():
            parent_folder = parent_folder.strip()
            # Remove quotes from parent folder if they exist
            if parent_folder.startswith('"') and parent_folder.endswith('"'):
                parent_folder = parent_folder[1:-1]
            # Combine parent and child folder
            full_folder_path = f"{parent_folder}/{folder_name}"
            print(f"Debug: Parent folder: '{parent_folder}'")
            print(f"Debug: Full folder path: '{full_folder_path}'")
        else:
            full_folder_path = folder_name
        
        # Quote folder name if it contains spaces
        if " " in full_folder_path:
            full_folder_path = f'"{full_folder_path}"'
        
        print(f"Debug: Formatted folder name: '{full_folder_path}'")
        
        # Connect to IMAP server
        imap = imaplib.IMAP4_SSL(imap_server, imap_port)
        
        # Login
        imap.login(email, password)
        
        # Create folder
        status, response = imap.create(full_folder_path)
        print(f"Debug: IMAP create status = {status}, response = {response}")
        
        # Close connection
        imap.logout()
        
        # Return True if folder was created successfully
        return status == "OK"
        
    except Exception as e:
        print(f"Error creating folder: {e}")
        return False
    

