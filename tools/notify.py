"""
Notification tool
=================
Sends desktop notifications, Gmail (via Google API OAuth), Telegram messages,
and logs all alerts to a file.

One-time setup:
  1. Run `python tools/google_tools.py --auth` to authorize Google access.
  2. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env for Telegram.
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent.parent / "output" / "notifications.log"


def _log(entry: str):
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)


def send_notification(title: str, message: str, priority: str = "normal") -> dict:
    """Send a desktop notification and log it."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _log(f"[{timestamp}] [{priority.upper()}] {title}: {message}\n")

    sent_desktop = False
    try:
        if sys.platform == "darwin":
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
            sent_desktop = True
        elif sys.platform.startswith("linux"):
            urgency = "critical" if priority == "urgent" else "normal"
            subprocess.run(["notify-send", "-u", urgency, title, message],
                           check=True, capture_output=True)
            sent_desktop = True
        elif sys.platform == "win32":
            ps_script = (
                f'[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; '
                f'$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); '
                f'$template.SelectSingleNode("//text[@id=1]").InnerText = "{title}"; '
                f'$template.SelectSingleNode("//text[@id=2]").InnerText = "{message}"; '
                f'$toast = [Windows.UI.Notifications.ToastNotification]::new($template); '
                f'[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Agent").Show($toast);'
            )
            subprocess.run(["powershell", "-Command", ps_script], check=True, capture_output=True)
            sent_desktop = True
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    prefix = "🚨" if priority == "urgent" else "🔔"
    print(f"\n{prefix} NOTIFICATION: {title}\n   {message}\n")

    return {"sent": True, "desktop": sent_desktop, "logged_to": str(LOG_FILE), "timestamp": timestamp}


def send_email(subject: str, body: str, to_email: str = None) -> dict:
    """
    Send an email via Gmail using Google OAuth2 credentials.

    Requires tools/google_tools.py to be authorized first
    (`python tools/google_tools.py --auth`).

    to_email defaults to NOTIFY_EMAIL env var, then the authorized Gmail account.
    """
    try:
        import base64
        from email.mime.text import MIMEText
        from tools.google_tools import get_google_service

        service = get_google_service("gmail", "v1")
        recipient = to_email or os.getenv("NOTIFY_EMAIL", "")

        if not recipient:
            # Fall back to the authenticated account's address
            profile = service.users().getProfile(userId="me").execute()
            recipient = profile.get("emailAddress", "")

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["To"] = recipient

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
        service.users().messages().send(userId="me", body={"raw": raw}).execute()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _log(f"[{timestamp}] [EMAIL] To:{recipient} Subject:{subject}\n")
        print(f"\n📧 EMAIL SENT: {subject}\n   To: {recipient}\n")
        return {"sent": True, "to": recipient, "subject": subject, "timestamp": timestamp}

    except ImportError:
        return {"sent": False, "error": "google-api-python-client not installed. Run: pip install google-api-python-client google-auth-oauthlib"}
    except Exception as e:
        return {"sent": False, "error": str(e)}


def send_telegram(message: str, chat_id: str = None) -> dict:
    """
    Send a message via a Telegram bot.

    Required .env vars:
      TELEGRAM_BOT_TOKEN — token from @BotFather
      TELEGRAM_CHAT_ID   — your chat ID from @userinfobot
    """
    import urllib.request
    import urllib.parse
    import json

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    target_chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")

    if not bot_token or not target_chat_id:
        return {
            "sent": False,
            "error": "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env"
        }

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({
        "chat_id": target_chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        if result.get("ok"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _log(f"[{timestamp}] [TELEGRAM] {message[:80]}\n")
            print(f"\n📱 TELEGRAM SENT: {message[:60]}\n")
            return {"sent": True, "chat_id": target_chat_id, "timestamp": timestamp}
        else:
            return {"sent": False, "error": result.get("description", "Unknown Telegram error")}

    except Exception as e:
        return {"sent": False, "error": str(e)}
