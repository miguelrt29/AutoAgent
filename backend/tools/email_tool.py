"""Tool that sends emails via SendGrid API (preferred) or SMTP as fallback."""

import re
import smtplib
from email.mime.text import MIMEText

import requests

from config import CONFIG


def _send_via_sendgrid(to: str, subject: str, body: str) -> dict:
    api_key = CONFIG["SENDGRID_API_KEY"]
    from_email = CONFIG["SMTP_USER"]

    resp = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "personalizations": [{"to": [{"email": to}]}],
            "from": {"email": from_email},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}],
        },
        timeout=15,
    )

    if resp.status_code in (200, 201, 202):
        return {
            "success": True,
            "result": f"Email sent to {to} with subject '{subject}'",
        }

    return {
        "success": False,
        "result": f"SendGrid API error {resp.status_code}: {resp.text}",
    }


def _send_via_smtp(to: str, subject: str, body: str) -> dict:
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


def send_email(to: str, subject: str, body: str) -> dict:
    try:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", to):
            return {"success": False, "result": f"Invalid email address: {to}"}

        if CONFIG.get("SENDGRID_API_KEY"):
            return _send_via_sendgrid(to, subject, body)

        return _send_via_smtp(to, subject, body)

    except Exception as e:
        return {"success": False, "result": f"Failed to send email: {e}"}
