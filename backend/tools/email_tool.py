"""Tool that sends emails via SMTP with STARTTLS using credentials from CONFIG."""

import re
import smtplib
from email.mime.text import MIMEText

from config import CONFIG

# For Gmail, SMTP_PASS must be an App Password (not your regular password).


def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email via SMTP using credentials from the CONFIG dict."""
    try:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", to):
            return {"success": False, "result": f"Invalid email address: {to}"}

        host = CONFIG["SMTP_HOST"]
        port = int(CONFIG["SMTP_PORT"])
        user = CONFIG["SMTP_USER"]
        password = CONFIG["SMTP_PASS"]

        msg = MIMEText(body, "plain")
        msg["Subject"] = subject
        msg["From"] = user
        msg["To"] = to

        with smtplib.SMTP(host, port, timeout=15) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(user, [to], msg.as_string())

        return {
            "success": True,
            "result": f"Email sent to {to} with subject '{subject}'",
        }

    except Exception as e:
        return {"success": False, "result": f"Failed to send email: {e}"}
