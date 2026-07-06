"""Tool that makes HTTP requests (GET/POST) to external REST APIs."""

import requests


def call_api(url: str, method: str = "GET", headers: dict = {}, body: dict = {}) -> dict:
    """Make an HTTP request to an external API. Supports GET and POST only."""
    try:
        if not url.startswith(("http://", "https://")):
            return {"success": False, "result": f"Invalid URL scheme: {url}"}

        method = method.upper()
        if method not in ("GET", "POST"):
            return {"success": False, "result": f"Unsupported HTTP method: {method}"}

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
