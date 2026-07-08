"""Tool that executes shell commands restricted to an allowed list from CONFIG."""

import shlex
import subprocess

from config import CONFIG


def run_command(command: str) -> dict:
    """Run a shell command if the base command is in ALLOWED_COMMANDS.

    Uses shell=False to prevent shell injection — commands are split
    safely via shlex.split() and executed as a list.
    """
    try:
        cmd_parts = shlex.split(command)
        if not cmd_parts:
            return {"success": False, "result": "No command provided."}

        base_cmd = cmd_parts[0]
        allowed = CONFIG["ALLOWED_COMMANDS"]

        if base_cmd not in allowed:
            return {
                "success": False,
                "result": f"Command '{base_cmd}' is not in the allowed list: {allowed}",
            }

        result = subprocess.run(
            cmd_parts,
            shell=False,
            capture_output=True,
            text=True,
            timeout=15,
        )

        output = result.stdout + result.stderr
        if len(output) > 3000:
            output = output[:3000] + "\n\n[... output truncated to 3000 characters ...]"

        return {"success": True, "result": output}

    except subprocess.TimeoutExpired:
        return {"success": False, "result": "Command timed out after 15 seconds."}
    except Exception as e:
        return {"success": False, "result": f"Command failed: {e}"}
