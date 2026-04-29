"""
Google Workspace tools
======================
Provides read/write access to Gmail, Google Sheets, Docs, Slides, and Drive
using a single OAuth2 credential (credentials.json from Google Cloud Console).

One-time setup:
  1. Go to console.cloud.google.com → New Project
  2. Enable: Gmail API, Google Sheets API, Google Docs API, Google Slides API, Google Drive API
  3. Create OAuth 2.0 Client ID (Desktop app) → Download → save as credentials.json
     in the project root (same folder as agent.py)
  4. Run: python tools/google_tools.py --auth
     A browser window will open — sign in and approve. token.json is saved for future use.

NOTE: If you add new scopes, delete token.json and re-run --auth to reauthorize.
"""

import os
import sys
import json
from pathlib import Path

# ── OAuth scopes (request all at once so one token covers everything) ──────────
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive",
]

PROJECT_ROOT = Path(__file__).parent.parent
CREDENTIALS_FILE = PROJECT_ROOT / "credentials.json"
TOKEN_FILE = PROJECT_ROOT / "token.json"


def get_credentials():
    """Load saved OAuth creds or run the browser auth flow."""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        raise ImportError(
            "Google client libraries not installed.\n"
            "Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        )

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"credentials.json not found at {CREDENTIALS_FILE}\n"
                    "Download it from Google Cloud Console → APIs & Services → Credentials"
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return creds


def get_google_service(api: str, version: str):
    """Return an authorized Google API service client."""
    from googleapiclient.discovery import build
    creds = get_credentials()
    return build(api, version, credentials=creds)


# ── Sheets ─────────────────────────────────────────────────────────────────────

def sheets_create(title: str) -> dict:
    """Create a new Google Sheet and return its ID and URL."""
    service = get_google_service("sheets", "v4")
    spreadsheet = service.spreadsheets().create(
        body={"properties": {"title": title}}
    ).execute()
    sheet_id = spreadsheet["spreadsheetId"]
    return {
        "spreadsheet_id": sheet_id,
        "title": title,
        "url": f"https://docs.google.com/spreadsheets/d/{sheet_id}"
    }


def sheets_read(spreadsheet_id: str, range_name: str = "Sheet1") -> dict:
    """Read rows from a Google Sheet range (e.g. 'Sheet1!A1:E10')."""
    service = get_google_service("sheets", "v4")
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    return {
        "spreadsheet_id": spreadsheet_id,
        "range": result.get("range", range_name),
        "rows": result.get("values", [])
    }


def sheets_write(spreadsheet_id: str, range_name: str, values: list) -> dict:
    """
    Write rows to a Google Sheet.
    values: list of rows, each row is a list of cell values.
    Example: [["Job Title", "Company", "Salary"], ["AI Engineer", "Acme", "$120k"]]
    """
    service = get_google_service("sheets", "v4")
    body = {"values": values}
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",
        body=body
    ).execute()
    return {
        "updated_cells": result.get("updatedCells", 0),
        "updated_range": result.get("updatedRange", range_name),
        "url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
    }


def sheets_append(spreadsheet_id: str, range_name: str, values: list) -> dict:
    """Append rows to the end of a Google Sheet."""
    service = get_google_service("sheets", "v4")
    body = {"values": values}
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()
    return {
        "appended_rows": len(values),
        "url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
    }


# ── Docs ───────────────────────────────────────────────────────────────────────

def docs_create(title: str, content: str) -> dict:
    """
    Create a new Google Doc with a title and plain-text body.
    Returns the doc ID and URL.
    """
    service = get_google_service("docs", "v1")

    # Create empty doc
    doc = service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    # Insert content
    service.documents().batchUpdate(
        documentId=doc_id,
        body={
            "requests": [{
                "insertText": {
                    "location": {"index": 1},
                    "text": content
                }
            }]
        }
    ).execute()

    return {
        "document_id": doc_id,
        "title": title,
        "url": f"https://docs.google.com/document/d/{doc_id}"
    }


def docs_read(document_id: str) -> dict:
    """Read the plain text content of a Google Doc."""
    service = get_google_service("docs", "v1")
    doc = service.documents().get(documentId=document_id).execute()

    # Extract plain text from the body
    text_parts = []
    for element in doc.get("body", {}).get("content", []):
        paragraph = element.get("paragraph")
        if paragraph:
            for run in paragraph.get("elements", []):
                text_run = run.get("textRun")
                if text_run:
                    text_parts.append(text_run.get("content", ""))

    return {
        "document_id": document_id,
        "title": doc.get("title", ""),
        "content": "".join(text_parts),
        "url": f"https://docs.google.com/document/d/{document_id}"
    }


# ── Drive ──────────────────────────────────────────────────────────────────────

def drive_list(folder_id: str = None, max_results: int = 20) -> dict:
    """List files in Google Drive or a specific folder."""
    service = get_google_service("drive", "v3")
    query = f"'{folder_id}' in parents" if folder_id else "trashed=false"
    results = service.files().list(
        q=query,
        pageSize=max_results,
        fields="files(id, name, mimeType, modifiedTime, webViewLink)"
    ).execute()
    files = results.get("files", [])
    return {
        "count": len(files),
        "files": [
            {
                "id": f["id"],
                "name": f["name"],
                "type": f.get("mimeType", ""),
                "modified": f.get("modifiedTime", ""),
                "url": f.get("webViewLink", "")
            }
            for f in files
        ]
    }


def drive_upload(filename: str, content: str, mimetype: str = "text/plain") -> dict:
    """Upload a text file to Google Drive and return its ID and URL."""
    import io
    from googleapiclient.http import MediaIoBaseUpload

    service = get_google_service("drive", "v3")
    file_metadata = {"name": filename}
    media = MediaIoBaseUpload(
        io.BytesIO(content.encode("utf-8")),
        mimetype=mimetype,
        resumable=False
    )
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name, webViewLink"
    ).execute()

    return {
        "file_id": file["id"],
        "name": file["name"],
        "url": file.get("webViewLink", "")
    }


# ── Slides ─────────────────────────────────────────────────────────────────────

def slides_create(title: str) -> dict:
    """Create a new Google Slides presentation and return its ID and URL."""
    service = get_google_service("slides", "v1")
    presentation = service.presentations().create(
        body={"title": title}
    ).execute()
    pres_id = presentation["presentationId"]
    return {
        "presentation_id": pres_id,
        "title": title,
        "url": f"https://docs.google.com/presentation/d/{pres_id}",
        "slides": len(presentation.get("slides", [])),
    }


def slides_read(presentation_id: str) -> dict:
    """
    Read the structure of a Google Slides presentation.
    Returns slide count, speaker notes, and text content per slide.
    """
    service = get_google_service("slides", "v1")
    pres = service.presentations().get(presentationId=presentation_id).execute()

    slides_summary = []
    for i, slide in enumerate(pres.get("slides", []), start=1):
        texts = []
        notes_text = ""
        for element in slide.get("pageElements", []):
            shape = element.get("shape", {})
            text_content = shape.get("text", {})
            for run in text_content.get("textElements", []):
                t = run.get("textRun", {}).get("content", "").strip()
                if t:
                    texts.append(t)
        # Speaker notes
        notes_page = slide.get("slideProperties", {}).get("notesPage", {})
        for element in notes_page.get("pageElements", []):
            shape = element.get("shape", {})
            if shape.get("shapeType") == "TEXT_BOX":
                for run in shape.get("text", {}).get("textElements", []):
                    t = run.get("textRun", {}).get("content", "").strip()
                    if t:
                        notes_text += t + " "
        slides_summary.append({
            "slide": i,
            "text": " | ".join(texts),
            "notes": notes_text.strip(),
        })

    return {
        "presentation_id": presentation_id,
        "title": pres.get("title", ""),
        "slide_count": len(slides_summary),
        "slides": slides_summary,
        "url": f"https://docs.google.com/presentation/d/{presentation_id}",
    }


def slides_add_slide(presentation_id: str, title: str, body: str, notes: str = "") -> dict:
    """
    Append a new slide with a title and body text to an existing presentation.
    Optionally add speaker notes.
    """
    service = get_google_service("slides", "v1")

    # Get current slide count to determine insertion index
    pres = service.presentations().get(presentationId=presentation_id).execute()
    slide_count = len(pres.get("slides", []))

    requests = [
        # Insert a new slide at the end using TITLE_AND_BODY layout
        {"insertSlide": {"insertionIndex": slide_count, "slideLayoutReference": {"predefinedLayout": "TITLE_AND_BODY"}}},
    ]

    result = service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": requests}
    ).execute()

    # Get the new slide's object ID
    new_slide_id = result["replies"][0]["insertSlide"]["objectId"]

    # Fetch the slide to find placeholder IDs
    pres = service.presentations().get(presentationId=presentation_id).execute()
    new_slide = next(s for s in pres["slides"] if s["objectId"] == new_slide_id)

    text_requests = []
    for element in new_slide.get("pageElements", []):
        placeholder = element.get("shape", {}).get("placeholder", {})
        p_type = placeholder.get("type", "")
        obj_id = element["objectId"]
        if p_type == "CENTERED_TITLE" or p_type == "TITLE":
            text_requests.append({"insertText": {"objectId": obj_id, "text": title, "insertionIndex": 0}})
        elif p_type == "BODY":
            text_requests.append({"insertText": {"objectId": obj_id, "text": body, "insertionIndex": 0}})

    if notes:
        notes_page = new_slide.get("slideProperties", {}).get("notesPage", {})
        for element in notes_page.get("pageElements", []):
            shape = element.get("shape", {})
            if shape.get("shapeType") == "TEXT_BOX":
                text_requests.append({
                    "insertText": {"objectId": element["objectId"], "text": notes, "insertionIndex": 0}
                })

    if text_requests:
        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": text_requests}
        ).execute()

    return {
        "presentation_id": presentation_id,
        "new_slide_index": slide_count + 1,
        "title": title,
        "url": f"https://docs.google.com/presentation/d/{presentation_id}",
    }


# ── Gmail Inbox ─────────────────────────────────────────────────────────────────

def _decode_body(payload: dict) -> str:
    """Recursively extract plain text body from a Gmail message payload."""
    import base64
    mime = payload.get("mimeType", "")
    if mime == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
    for part in payload.get("parts", []):
        text = _decode_body(part)
        if text:
            return text
    return ""


def _parse_headers(headers: list) -> dict:
    """Extract common headers from a Gmail message."""
    h = {h["name"].lower(): h["value"] for h in headers}
    return {
        "from":    h.get("from", ""),
        "to":      h.get("to", ""),
        "subject": h.get("subject", "(no subject)"),
        "date":    h.get("date", ""),
    }


def gmail_read_inbox(max_results: int = 10, query: str = "in:inbox") -> dict:
    """
    List recent emails from the inbox.
    Returns sender, subject, date, and snippet for each message.
    query: Gmail search syntax, e.g. 'in:inbox is:unread' or 'from:boss@company.com'
    """
    service = get_google_service("gmail", "v1")
    results = service.users().messages().list(
        userId="me", maxResults=max_results, q=query
    ).execute()

    messages = []
    for msg_ref in results.get("messages", []):
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()
        headers = _parse_headers(msg.get("payload", {}).get("headers", []))
        messages.append({
            "id":      msg["id"],
            "from":    headers["from"],
            "subject": headers["subject"],
            "date":    headers["date"],
            "snippet": msg.get("snippet", ""),
            "unread":  "UNREAD" in msg.get("labelIds", []),
        })

    return {
        "count": len(messages),
        "query": query,
        "messages": messages,
    }


def gmail_get_message(message_id: str) -> dict:
    """
    Get the full content of a specific email by its ID.
    Returns headers, body text, and attachment names.
    """
    service = get_google_service("gmail", "v1")
    msg = service.users().messages().get(
        userId="me", id=message_id, format="full"
    ).execute()

    headers = _parse_headers(msg.get("payload", {}).get("headers", []))
    body = _decode_body(msg.get("payload", {}))

    # List attachment filenames
    attachments = []
    for part in msg.get("payload", {}).get("parts", []):
        filename = part.get("filename", "")
        if filename:
            attachments.append(filename)

    return {
        "id":          message_id,
        "from":        headers["from"],
        "to":          headers["to"],
        "subject":     headers["subject"],
        "date":        headers["date"],
        "body":        body[:4000],   # cap to avoid flooding context
        "attachments": attachments,
        "unread":      "UNREAD" in msg.get("labelIds", []),
    }


def gmail_search(query: str, max_results: int = 10) -> dict:
    """
    Search Gmail using Gmail search syntax.
    Examples: 'from:boss@company.com', 'subject:invoice is:unread', 'after:2024/01/01'
    """
    return gmail_read_inbox(max_results=max_results, query=query)


def gmail_mark_read(message_id: str) -> dict:
    """Mark an email as read."""
    service = get_google_service("gmail", "v1")
    service.users().messages().modify(
        userId="me", id=message_id,
        body={"removeLabelIds": ["UNREAD"]}
    ).execute()
    return {"marked_read": True, "id": message_id}


# ── CLI auth helper ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--auth" in sys.argv:
        print("Opening browser for Google authorization...")
        creds = get_credentials()
        print(f"✅ Authorization complete. token.json saved to {TOKEN_FILE}")
        print("Your agent can now use Gmail, Sheets, Docs, and Drive.")
    else:
        print("Usage: python tools/google_tools.py --auth")
