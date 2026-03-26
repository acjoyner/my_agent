"""
Notification tool
=================
Sends desktop notifications and logs alerts to a file.
Cross-platform: works on Mac, Windows, and Linux.
"""

import sys
import subprocess
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent.parent / "output" / "notifications.log"


def send_notification(title: str, message: str, priority: str = "normal") -> dict:
    """
    Send a desktop notification and log it to file.
    Falls back gracefully if desktop notifications aren't available.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log to file always
    log_entry = f"[{timestamp}] [{priority.upper()}] {title}: {message}\n"
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

    # Try desktop notification
    sent_desktop = False
    try:
        if sys.platform == "darwin":          # macOS
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
            sent_desktop = True
        elif sys.platform.startswith("linux"):  # Linux (notify-send)
            urgency = "critical" if priority == "urgent" else "normal"
            subprocess.run(
                ["notify-send", "-u", urgency, title, message],
                check=True, capture_output=True
            )
            sent_desktop = True
        elif sys.platform == "win32":          # Windows
            # Uses PowerShell toast notification
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
        pass  # Desktop notify failed — logged to file is fine

    # Also print to console so you always see it
    prefix = "🚨" if priority == "urgent" else "🔔"
    print(f"\n{prefix} NOTIFICATION: {title}\n   {message}\n")

    return {
        "sent": True,
        "desktop": sent_desktop,
        "logged_to": str(LOG_FILE),
        "timestamp": timestamp
    }
