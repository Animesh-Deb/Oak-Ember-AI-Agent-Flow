import os 
import base64 
from email.mime.text import MIMEText 
from email.mime.multipart import MIMEMultipart 
from google.oauth2.credentials import Credentials 
from google.auth.transport.requests import Request 
from google_auth_oauthlib.flow import InstalledAppFlow 
from googleapiclient.discovery import build 
# ============================================================ 
# GMAIL CONFIGURATION 
# ============================================================ 
SCOPES = [ 
"https://www.googleapis.com/auth/gmail.modify", 
"https://www.googleapis.com/auth/gmail.send" 
] 
BASE_DIR = os.path.dirname( 
os.path.abspath(__file__) 
) 
 
CREDENTIALS_FILE = os.path.join( 
    BASE_DIR, 
    "gmail_credentials.json" 
) 
 
TOKEN_FILE = os.path.join( 
    BASE_DIR, 
    "gmail_token.json" 
) 
 
 
# ============================================================ 
# AUTHENTICATION 
# ============================================================ 
 
def get_gmail_service(): 
 
    credentials = None 
 
    # Existing token 
    if os.path.exists(TOKEN_FILE): 
 
        credentials = Credentials.from_authorized_user_file( 
            TOKEN_FILE, 
            SCOPES 
        ) 
 
    # Refresh expired token 
    if credentials and credentials.expired and credentials.refresh_token: 
 
        credentials.refresh( 
            Request() 
        ) 
 
    # First-time authentication 
    if not credentials or not credentials.valid: 
 
        flow = InstalledAppFlow.from_client_secrets_file( 
            CREDENTIALS_FILE, 
            SCOPES 
        ) 
 
        credentials = flow.run_local_server( 
            port=0 
        ) 
 
        with open( 
            TOKEN_FILE, 
            "w" 
        ) as token: 
 
            token.write( 
                credentials.to_json() 
            ) 
 
    return build( 
        "gmail", 
        "v1", 
        credentials=credentials 
    ) 
 
 
# ============================================================ 
# GET UNREAD EMAILS 
# ============================================================ 
 
def get_unread_emails( 
    service, 
    max_results=10 
): 
 
    response = service.users().messages().list( 
        userId="me", 
        q="is:unread", 
        maxResults=max_results 
    ).execute() 
 
    messages = response.get( 
        "messages", 
        [] 
    ) 
 
    return messages 
 
 
# ============================================================ 
# GET FULL EMAIL 
# ============================================================ 
 
def get_email( 
    service, 
    message_id 
): 
 
    return service.users().messages().get( 
        userId="me", 
        id=message_id, 
        format="full" 
    ).execute() 
 
 
# ============================================================ 
# EXTRACT EMAIL BODY 
# ============================================================ 
 
def extract_email_body( 
    payload 
): 
 
    # Simple email 
    if payload.get("body", {}).get("data"): 
 
        data = payload["body"]["data"] 
 
        return base64.urlsafe_b64decode( 
            data 
        ).decode( 
            "utf-8", 
            errors="ignore" 
        ) 
 
    # Multipart email 
    parts = payload.get( 
        "parts", 
        [] 
    ) 
 
    for part in parts: 
 
        mime_type = part.get( 
            "mimeType", 
            "" 
        ) 
 
        if mime_type == "text/plain": 
 
            data = part.get( 
                "body", 
                {} 
            ).get( 
                "data" 
            ) 
 
            if data: 
 
                return base64.urlsafe_b64decode( 
                    data 
                ).decode( 
                    "utf-8", 
                    errors="ignore" 
                ) 
 
    # Recursive multipart search 
    for part in parts: 
 
        if part.get("parts"): 
 
            body = extract_email_body( 
                part 
            ) 
 
            if body: 
                return body 
 
    return "" 
 
 
# ============================================================ 
# GET EMAIL HEADER 
# ============================================================ 
 
def get_header( 
    headers, 
    name 
): 
 
    for header in headers: 
 
        if header["name"].lower() == name.lower(): 
 
            return header["value"] 
 
    return "" 
 
 
# ============================================================ 
# EXTRACT EMAIL INFORMATION 
# ============================================================ 
 
def extract_email_information( 
    email 
): 
 
    payload = email.get( 
        "payload", 
        {} 
    ) 
 
    headers = payload.get( 
        "headers", 
        [] 
    ) 
 
    sender = get_header( 
        headers, 
        "From" 
    ) 
 
    subject = get_header( 
        headers, 
        "Subject" 
    ) 
 
    message_id = email.get( 
        "id" 
    ) 
 
    thread_id = email.get( 
        "threadId" 
    ) 
 
    body = extract_email_body( 
        payload 
    ) 
 
    return { 
        "sender": sender, 
        "subject": subject, 
        "body": body, 
        "message_id": message_id, 
        "thread_id": thread_id 
    } 
 
 
# ============================================================ 
# SEND EMAIL REPLY 
# ============================================================ 
 
def send_email_reply( 
    service, 
    recipient, 
    subject, 
    body, 
    thread_id 
): 
 
    message = MIMEText( 
        body, 
        "plain", 
        "utf-8" 
    ) 
 
    message["To"] = recipient 
    message["Subject"] = subject 
 
    raw_message = base64.urlsafe_b64encode( 
        message.as_bytes() 
    ).decode() 
 
    gmail_message = { 
        "raw": raw_message, 
        "threadId": thread_id 
    } 
 
    result = service.users().messages().send( 
        userId="me", 
        body=gmail_message 
    ).execute() 
 
    return result 
 
 
# ============================================================ 
# MARK EMAIL AS READ 
# ============================================================ 
 
def mark_as_read( 
    service, 
    message_id 
): 
 
    service.users().messages().modify( 
        userId="me", 
        id=message_id, 
        body={ 
            "removeLabelIds": ["UNREAD"] 
        } 
    ).execute()