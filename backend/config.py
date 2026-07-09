import os
from dotenv import load_dotenv

load_dotenv()

REQUIRED_KEYS = [
    "GROQ_API_KEY",
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USER",
    "SMTP_PASS",
    "ALLOWED_COMMANDS",
]

missing = [key for key in REQUIRED_KEYS if key not in os.environ]
if missing:
    raise ValueError(f"Missing required environment variable(s): {', '.join(missing)}")

groq_key = os.environ["GROQ_API_KEY"].strip()
if not groq_key:
    raise ValueError("GROQ_API_KEY is set but empty")

raw_allowed = os.environ["ALLOWED_COMMANDS"]
ALLOWED_COMMANDS = [cmd.strip() for cmd in raw_allowed.split(",") if cmd.strip()]

CONFIG = {
    "GROQ_API_KEY": groq_key,
    "SMTP_HOST": os.environ["SMTP_HOST"],
    "SMTP_PORT": os.environ["SMTP_PORT"],
    "SMTP_USER": os.environ["SMTP_USER"],
    "SMTP_PASS": os.environ["SMTP_PASS"],
    "ALLOWED_COMMANDS": ALLOWED_COMMANDS,
    "SENDGRID_API_KEY": os.environ.get("SENDGRID_API_KEY", ""),
    "ENABLE_LOCAL_TOOLS": os.environ.get("ENABLE_LOCAL_TOOLS", "false").lower() == "true",
    "DATABASE_URL": os.environ.get("DATABASE_URL", ""),
}
