import json

from groq import Groq
from config import CONFIG

from tools.web_search import web_search
from tools.file_ops import read_file, write_file
from tools.email_tool import send_email
from tools.api_tool import call_api
from tools.shell_tool import run_command

SESSIONS: dict[str, list] = {}

LOCAL_TOOLS_MAP = {
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command,
}

LOCAL_TOOLS_DEFS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to the file"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file (overwrites if it exists).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute path to the file"},
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a shell command (restricted to ALLOWED_COMMANDS).",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to run"},
                },
                "required": ["command"],
            },
        },
    },
]

BASE_TOOLS_MAP = {
    "web_search": web_search,
    "send_email": send_email,
    "call_api": call_api,
}

TOOLS_MAP = {**BASE_TOOLS_MAP}
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                    "max_results": {"type": "integer", "description": "Max results to return (default 5)"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email via SMTP.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body text"},
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "call_api",
            "description": "Make an HTTP request to an external API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {"type": "string", "description": "HTTP method (GET, POST)"},
                    "url": {"type": "string", "description": "Request URL"},
                    "headers": {"type": "object", "description": "Optional request headers"},
                    "body": {"type": "object", "description": "Optional request body"},
                },
                "required": ["method", "url"],
            },
        },
    },
]

if CONFIG["ENABLE_LOCAL_TOOLS"]:
    TOOLS_MAP.update(LOCAL_TOOLS_MAP)
    TOOLS.extend(LOCAL_TOOLS_DEFS)


def _coerce_args(tool_name: str, args: dict) -> dict:
    coercions = {
        "web_search": {"max_results": int},
        "read_file": {},
        "write_file": {},
        "send_email": {},
        "call_api": {},
        "run_command": {},
    }
    expected = coercions.get(tool_name, {})
    result = {}
    for k, v in args.items():
        if k in expected:
            try:
                result[k] = expected[k](v)
            except (ValueError, TypeError):
                result[k] = v
        else:
            result[k] = v
    return result


def _execute_tool(name: str, input_data: dict) -> dict:
    if name not in TOOLS_MAP:
        return {"success": False, "result": f"Unknown tool: {name}"}
    try:
        tool_fn = TOOLS_MAP[name]
        coerced = _coerce_args(name, input_data)
        result = tool_fn(**coerced)
        return result if isinstance(result, dict) else {"success": True, "result": str(result)}
    except Exception as e:
        return {"success": False, "result": f"Tool error: {e}"}


class Agent:
    def __init__(self, session_id: str | None = None):
        self.session_id = session_id
        self.messages = SESSIONS.get(session_id, []) if session_id else []
        self.client = Groq(api_key=CONFIG["GROQ_API_KEY"])

    def _save(self):
        if self.session_id:
            SESSIONS[self.session_id] = self.messages

    def run(self, user_message: str):
        self.messages.append({"role": "user", "content": user_message})

        enable_local = CONFIG["ENABLE_LOCAL_TOOLS"]
        available = "search the web, send emails, call an API"
        if enable_local:
            available += ", read/write files, run commands"

        system_prompt = f"""You are AutoAgent, a helpful AI assistant with access to tools.

IMPORTANT RULES:
- For simple conversation (greetings, questions about yourself, general knowledge you already know): respond directly with text. DO NOT call any tool.
- Only use tools when the user explicitly asks to: {available}.
- When calling a tool, ALWAYS output the arguments as raw valid JSON — never wrap them in parentheses or extra characters.
- max_results must always be an integer (e.g. 5), never a string.
- Respond in the same language the user writes in.
- Be concise and helpful."""

        while True:
            response = self.client.chat.completions.create(
                model="qwen/qwen3-32b",
                messages=[{"role": "system", "content": system_prompt}] + self.messages,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=2048,
            )

            msg = response.choices[0].message

            if msg.tool_calls:
                self.messages.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                        }
                        for tc in msg.tool_calls
                    ],
                })

                for tc in msg.tool_calls:
                    name = tc.function.name
                    tool_input = json.loads(tc.function.arguments)
                    if isinstance(tool_input, str):
                        try:
                            tool_input = json.loads(tool_input)
                        except json.JSONDecodeError:
                            tool_input = {}
                    yield {"type": "tool_call", "tool": name, "input": tool_input}
                    result = _execute_tool(name, tool_input)
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": str(result),
                    })

                continue

            content = msg.content or ""
            if content:
                yield {"type": "text", "content": content}
            yield {"type": "done"}
            self._save()
            return
