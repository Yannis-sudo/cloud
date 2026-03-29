"""Module for handling email folder retrieval."""

import imaplib
import re
from typing import List
from app.database import get_user_emails    

def get_folders(email: str) -> List[str]:
    """Get folders from the email server (GMX compatible)."""
    configs = get_user_emails(email)
    
    if not configs or not isinstance(configs, list) or len(configs) == 0:
        return []
    
    config = configs[0]
    imap_server = config.get("server_incoming")
    imap_port = config.get("server_incoming_port", 993)
    password = config.get("password")

    if not imap_server or not password:
        return []

    folder_names = []

    try:
        imap = imaplib.IMAP4_SSL(imap_server, imap_port)
        imap.login(email, password)

        status, folders = imap.list()
        if status != "OK" or not folders:
            return []

        for folder in folders:
            folder_decoded = folder.decode()
            print(f"Debug: Raw folder: {folder_decoded}")

            # Match the last part after the separator (robust for GMX)
            # This handles: (\HasNoChildren) "/" INBOX
            # And: (\HasChildren) "/" "test folder"
            # And: (\HasNoChildren) "/" "test folder/test"
            
            match = re.search(r'"/"?\s*"?(.+?)"?$', folder_decoded)
            if match:
                name = match.group(1)
                print(f"Debug: Extracted name before decode: {name}")
                
                # Decode IMAP UTF-7 special characters using imaplib
                try:
                    name = imaplib.IMAP4._decode_utf7(name)
                except:
                    # Fallback: handle common GMX encodings manually
                    name = name.replace('&APw-', 'ü').replace('&AP-', 'ä').replace('&AOQ-', 'ß').replace('&APg-', 'ö')
                
                # Skip empty separators only
                if name and name != '/' and name.strip():
                    folder_names.append(name)
                    print(f"Debug: Added folder: {name}")
                continue
            else:
                print(f"Debug: No match for: {folder_decoded}")

        # Remove duplicates and sort
        folder_names = sorted(list(set(folder_names)))
        print(f"Debug: All extracted folders: {folder_names}")
        return folder_names

    except Exception as e:
        print(f"Error retrieving folders: {str(e)}")
        return []

    finally:
        try:
            imap.logout()
        except:
            pass