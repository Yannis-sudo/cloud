from app.database import get_user_emails
import imapclient
import email
from email.header import decode_header
import quopri
import base64


# Load the config from the database
def load_config(email: str):
    return get_user_emails(email)

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
    
    # Load emails using the new function
    return load_emails_from_folders(email_address, password, server_incoming)


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
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get("Content-Disposition"))
            if ctype == "text/plain" and "attachment" not in disp:
                payload = part.get_payload(decode=True) or b''
                charset = part.get_content_charset() or 'utf-8'
                # Transfer-Encoding
                transfer_encoding = part.get('Content-Transfer-Encoding', '').lower()
                if transfer_encoding == 'quoted-printable':
                    payload = quopri.decodestring(payload)
                elif transfer_encoding == 'base64':
                    payload = base64.b64decode(payload)
                for enc in [charset, 'utf-8', 'iso-8859-1']:
                    try:
                        body += payload.decode(enc, errors='replace')
                        break
                    except:
                        continue
    else:
        payload = msg.get_payload(decode=True) or b''
        charset = msg.get_content_charset() or 'utf-8'
        transfer_encoding = msg.get('Content-Transfer-Encoding', '').lower()
        if transfer_encoding == 'quoted-printable':
            payload = quopri.decodestring(payload)
        elif transfer_encoding == 'base64':
            payload = base64.b64decode(payload)
        for enc in [charset, 'utf-8', 'iso-8859-1']:
            try:
                body += payload.decode(enc, errors='replace')
                break
            except:
                continue
    return body


def load_emails_from_folders(email_address, password, server_incoming):
    """Hauptfunktion: Alle Ordner durchsuchen, E-Mails laden mit imapclient und Standard-Email-Bibliothek"""
    emails_result = []
    folder_list = []
    
    try:
        # Verbindung mit imapclient
        client = imapclient.IMAPClient(server_incoming, ssl=True)
        client.login(email_address, password)

        # Alle Ordner abrufen (UTF-8 automatisch)
        folders = client.list_folders()
        folder_dict = {f[2]: f[2] for f in folders}  # UTF-8 Namen
        folder_list = list(folder_dict.keys())

        for folder_utf8 in folder_dict.keys():
            try:
                client.select_folder(folder_utf8, readonly=True)
                uids = client.search(['ALL'])
                
                # Nur die letzten 5 E-Mails pro Ordner
                for uid in uids[-5:]:
                    raw_message = client.fetch([uid], ['BODY[]', 'FLAGS'])
                    msg = email.message_from_bytes(raw_message[uid][b'BODY[]'])
                    
                    # Body mit manueller Dekodierung
                    body = get_body(msg)
                    
                    # Header mit manueller Dekodierung
                    from_str = decode_mime_header(msg["from"])
                    subject = decode_mime_header(msg["subject"])
                    date = decode_mime_header(msg["date"])
                    
                    emails_result.append({
                        'folder': folder_utf8,
                        'from': from_str,
                        'subject': subject or '',
                        'date': date or '',
                        'message_id': str(uid),
                        'body': body
                    })
                    
            except Exception as e:
                # Ordner überspringen, falls Fehler
                continue

        client.logout()
        return {
            "folders": folder_list,
            "emails": emails_result
        }
        
    except Exception as e:
        return {"folders": [], "emails": []}