from app.database import get_user_emails
import imaplib
import email
from email.header import decode_header
import quopri
import base64
import re
import logging

logger = logging.getLogger(__name__)


# Load the config from the database
def load_config(email: str):
    return get_user_emails(email)

def decode_mime_header(header_value):
    """Dekodiert Header (Subject, From, Date) korrekt inkl. Umlaute"""
    if not header_value:
        return ""
    result = ""
    for part, encoding in decode_header(header_value):
        if isinstance(part, bytes):
            if encoding:
                try:
                    result += part.decode(encoding, errors='replace')
                except:
                    result += part.decode('utf-8', errors='replace')
            else:
                # Fallback
                try:
                    result += part.decode('utf-8')
                except:
                    result += part.decode('iso-8859-1', errors='replace')
        else:
            result += part
    return result


def get_body(msg):
    """Dekodiert E-Mail Body robust inkl. Umlaute"""
    body = ""
    html_body = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get("Content-Disposition"))
            
            # Nur Text-Teile verarbeiten, keine Anhänge
            if "attachment" not in disp:
                try:
                    # Email library's built-in decoding
                    payload = part.get_payload(decode=True)
                    if payload is None:
                        payload = b''
                    
                    # Charset aus dem Part holen
                    charset = part.get_content_charset()
                    
                    # Text dekodieren mit Email-Library Methode
                    if isinstance(payload, bytes):
                        if charset:
                            try:
                                decoded_text = payload.decode(charset, errors='replace')
                            except (UnicodeDecodeError, LookupError):
                                try:
                                    decoded_text = payload.decode('utf-8', errors='replace')
                                except (UnicodeDecodeError, LookupError):
                                    decoded_text = payload.decode('latin-1', errors='replace')
                        else:
                            # Kein Charset - versuchen wir UTF-8
                            try:
                                decoded_text = payload.decode('utf-8', errors='replace')
                            except (UnicodeDecodeError, LookupError):
                                decoded_text = payload.decode('latin-1', errors='replace')
                    else:
                        # Payload ist bereits String
                        decoded_text = str(payload)
                    
                    # HTML und Plain Text getrennt sammeln
                    if ctype == "text/html":
                        html_body = decoded_text
                    elif ctype == "text/plain":
                        body = decoded_text
                        
                except Exception as e:
                    # Bei Fehlern weitermachen
                    logger.error(f"Error decoding email part: {e}")
                    continue
        
        # Wenn wir HTML haben aber keinen Plain Text, extrahieren wir Text aus HTML
        if not body and html_body:
            # Einfache HTML-Entfernung (für bessere Lesbarkeit)
            try:
                import re
                body = re.sub(r'<[^>]+>', '', html_body)
                body = re.sub(r'&nbsp;', ' ', body)
                body = re.sub(r'\s+', ' ', body).strip()
            except:
                body = html_body  # Fallback bei Regex-Fehlern
    else:
        # Single-part E-Mail
        try:
            # Email library's built-in decoding
            payload = msg.get_payload(decode=True)
            if payload is None:
                payload = b''
            
            # Charset aus der Message holen
            charset = msg.get_content_charset()
            
            # Text dekodieren
            if isinstance(payload, bytes):
                if charset:
                    try:
                        body = payload.decode(charset, errors='replace')
                    except (UnicodeDecodeError, LookupError):
                        try:
                            body = payload.decode('utf-8', errors='replace')
                        except (UnicodeDecodeError, LookupError):
                            body = payload.decode('latin-1', errors='replace')
                else:
                    # Kein Charset - versuchen wir UTF-8
                    try:
                        body = payload.decode('utf-8', errors='replace')
                    except (UnicodeDecodeError, LookupError):
                        body = payload.decode('latin-1', errors='replace')
            else:
                # Payload ist bereits String
                body = str(payload)
                
        except Exception as e:
            logger.error(f"Error decoding single-part email: {e}")
            body = "Error decoding email content"
    
    return body


def extract_attachments(msg):
    """Extrahiert Anhänge aus einer E-Mail und gibt sie als Liste zurück"""
    attachments = []
    
    if msg.is_multipart():
        for part in msg.walk():
            disp = str(part.get("Content-Disposition"))
            
            # Prüfen ob es ein Anhang ist
            if "attachment" in disp:
                filename = part.get_filename()
                if filename:
                    # Dateiname dekodieren
                    decoded_filename = decode_mime_header(filename)
                    
                    # Inhalt dekodieren
                    content = part.get_payload(decode=True)
                    if content:
                        # Transfer-Encoding behandeln
                        transfer_encoding = part.get('Content-Transfer-Encoding', '').lower()
                        if transfer_encoding == 'quoted-printable':
                            content = quopri.decodestring(content)
                        elif transfer_encoding == 'base64':
                            # Base64 Content ist bereits dekodiert durch get_payload(decode=True)
                            pass
                        
                        # In Base64 für Frontend umwandeln
                        content_b64 = base64.b64encode(content).decode('utf-8')
                        
                        attachments.append({
                            'filename': decoded_filename,
                            'content_type': part.get_content_type(),
                            'size': len(content),
                            'content': content_b64
                        })
    
    return attachments


def load_emails(email: str):
    # Load config
    config = load_config(email)
    
    # Check if config was found and is a list
    if config == "Email not found" or not isinstance(config, list) or len(config) == 0:
        return None
    
    # Get the first email configuration (assuming one config per user for simplicity)
    email_config = config[0]
    
    # Save every parameter in a variable
    user_email = email_config.get('user_email')
    email_address = email_config.get('email')
    server_incoming = email_config.get('server_incoming')
    server_outgoing = email_config.get('server_outgoing')
    server_incoming_port = email_config.get('server_incoming_port')
    server_outgoing_port = email_config.get('server_outgoing_port')
    password = email_config.get('password')
    
    # Load emails using new function
    return load_emails_from_folders(email_address, password, server_incoming, server_incoming_port)


def load_emails_from_folders(email_address, password, server_incoming, server_incoming_port=993):
    """Hauptfunktion: Alle Ordner durchsuchen, E-Mails laden mit imaplib und Standard-Email-Bibliothek"""
    emails_result = []
    folder_list = []
    
    try:
        # Verbindung mit imaplib (same as getfolders.py)
        imap = imaplib.IMAP4_SSL(server_incoming, server_incoming_port)
        imap.login(email_address, password)

        # Ordner abrufen mit der gleichen Logik wie getfolders.py
        status, folders = imap.list()
        if status != "OK" or not folders:
            return {"folders": [], "emails": []}

        for folder in folders:
            folder_decoded = folder.decode()

            # Match the last part after the separator (robust for GMX)
            # This handles: (\HasNoChildren) "/" INBOX
            # And: (\HasChildren) "/" "test folder"
            # And: (\HasNoChildren) "/" "test folder/test"
            
            match = re.search(r'"/"?\s*"?(.+?)"?$', folder_decoded)
            if match:
                name = match.group(1)
                
                # Decode IMAP UTF-7 special characters using imaplib
                try:
                    # Try proper UTF-7 decoding first
                    if isinstance(name, str):
                        name_bytes = name.encode('ascii')
                        name = imaplib._decode_utf7(name_bytes)
                    else:
                        name = imaplib._decode_utf7(name)
                except Exception as e:
                    # Fallback: handle common encodings manually
                    name = name.replace('&APw-', 'ü').replace('&AP-', 'ä').replace('&AOQ-', 'ß').replace('&APg-', 'ö').replace('&Aw-', 'Ä').replace('&Ow-', 'Ö').replace('&Uw-', 'Ü')
                
                # Skip empty separators only
                if name and name != '/' and name.strip():
                    folder_list.append(name)

        # Remove duplicates and sort
        folder_list = sorted(list(set(folder_list)))

        # E-Mails aus jedem Ordner laden
        for folder_name in folder_list:
            try:
                # Properly encode folder name for IMAP select command
                if isinstance(folder_name, str):
                    # Try to encode as UTF-7, fallback to modified UTF-7 for IMAP
                    try:
                        encoded_folder = imaplib._encode_utf7(folder_name)
                        select_arg = f'"{encoded_folder.decode()}"'
                    except:
                        # Manual encoding fallback for problematic characters
                        encoded_name = folder_name.replace('ü', '&APw-').replace('ä', '&AP-').replace('ö', '&APg-').replace('ß', '&AOQ-')
                        select_arg = f'"{encoded_name}"'
                else:
                    select_arg = f'"{folder_name}"'
                
                imap.select(select_arg, readonly=True)
                status, uids = imap.search(None, 'ALL')
                
                if status == "OK" and uids:
                    uid_list = uids[0].split()
                    # Nur die letzten 5 E-Mails pro Ordner
                    for uid in uid_list[-5:]:
                        status, msg_data = imap.fetch(uid, '(BODY.PEEK[])')
                        if status == "OK":
                            raw_message = msg_data[0][1]
                            msg = email.message_from_bytes(raw_message)
                            
                            # Body mit manueller Dekodierung
                            body = get_body(msg)
                            
                            # Anhänge extrahieren
                            attachments = extract_attachments(msg)
                            
                            # Header mit manueller Dekodierung
                            from_str = decode_mime_header(msg["from"])
                            subject = decode_mime_header(msg["subject"])
                            date = decode_mime_header(msg["date"])
                            
                            emails_result.append({
                                'folder': folder_name,
                                'from': from_str,
                                'subject': subject or '',
                                'date': date or '',
                                'message_id': uid.decode(),
                                'body': body,
                                'attachments': attachments,
                                'has_attachments': len(attachments) > 0
                            })
                    
            except Exception as e:
                # Ordner überspringen, falls Fehler
                print(f"Error processing folder {folder_name}: {e}")
                continue

        imap.logout()
        return {
            "folders": folder_list,
            "emails": emails_result
        }
        
    except Exception as e:
        print(f"Error in load_emails_from_folders: {e}")
        return {"folders": [], "emails": []}