"""Tool that makes HTTP requests (GET/POST) to external REST APIs."""

import ipaddress
import socket
from urllib.parse import urlparse

import requests


PRIVATE_RANGES = [
    "127.0.0.0/8",
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16",
    "169.254.0.0/16",
    "::1/128",
    "fc00::/7",
    "fe80::/10",
]


def _is_private_url(url: str) -> bool:
    """Check if the URL resolves to a private/reserved IP address (SSRF protection)."""
    try:
        hostname = urlparse(url).hostname
        if hostname is None:
            return True
        if hostname in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
            return True
        ip = socket.getaddrinfo(hostname, 80, family=socket.AF_INET)[0][4][0]
        addr = ipaddress.ip_address(ip)
        for block in PRIVATE_RANGES:
            if addr in ipaddress.ip_network(block):
                return True
        return False
    except Exception:
        return True


def call_api(url: str, method: str = "GET", headers: dict = {}, body: dict = {}) -> dict:
    """Make an HTTP request to an external API. Supports GET and POST only."""
    try:
        if not url.startswith(("http://", "https://")):
            return {"success": False, "result": f"Invalid URL scheme: {url}"}

        method = method.upper()
        if method not in ("GET", "POST"):
            return {"success": False, "result": f"Unsupported HTTP method: {method}"}

        if _is_private_url(url):
            return {"success": False, "result": "Access to private/internal IP addresses is not allowed"}

        if method == "POST":
            resp = requests.post(url, headers=headers, json=body, timeout=10)
        else:
            resp = requests.get(url, headers=headers, timeout=10)

        text = resp.text
        if len(text) > 2000:
            text = text[:2000] + "\n\n[... response truncated to 2000 characters ...]"

        return {
            "success": True,
            "result": f"Status: {resp.status_code}\nBody: {text}",
        }

    except requests.RequestException as e:
        return {"success": False, "result": f"Request failed: {e}"}
    except Exception as e:
        return {"success": False, "result": f"Unexpected error: {e}"}
