"""Tool for reading and writing files on the local filesystem with path traversal protection."""

from pathlib import Path


def _resolve_safe(path: str) -> Path:
    """Resolve the path and raise ValueError if it escapes the current working directory."""
    resolved = Path(path).resolve()
    cwd = Path.cwd().resolve()
    if not str(resolved).startswith(str(cwd)):
        raise ValueError(f"Path traversal denied: {path} resolves outside the working directory")
    return resolved


def read_file(path: str) -> dict:
    """Read and return the content of a local file, validating path safety."""
    try:
        resolved = _resolve_safe(path)

        resolved.exists()
        resolved.is_file()

        content = resolved.read_text(encoding="utf-8")

        if len(content) > 5000:
            content = content[:5000] + "\n\n[... content truncated to 5000 characters ...]"

        return {"success": True, "result": content}

    except ValueError as e:
        return {"success": False, "result": str(e)}
    except PermissionError:
        return {"success": False, "result": f"Permission denied: {path}"}
    except Exception as e:
        return {"success": False, "result": f"Error reading file: {e}"}


def write_file(path: str, content: str) -> dict:
    """Create or overwrite a local file with the given content, validating path safety."""
    try:
        resolved = _resolve_safe(path)

        if resolved.exists() and not resolved.is_file():
            return {"success": False, "result": f"Path exists and is not a file: {path}"}

        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")

        return {"success": True, "result": str(resolved)}

    except ValueError as e:
        return {"success": False, "result": str(e)}
    except PermissionError:
        return {"success": False, "result": f"Permission denied: {path}"}
    except Exception as e:
        return {"success": False, "result": f"Error writing file: {e}"}
