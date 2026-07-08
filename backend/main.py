"""FastAPI entrypoint: starts the server, registers routes, and initialises the app."""

import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from agent import Agent, SESSIONS
from schemas import ChatRequest, ToolEvent, TextEvent, ErrorEvent, DoneEvent

AVAILABLE_TOOLS = [
    {"name": "web_search", "description": "Search the web using DuckDuckGo", "parameters": ["query", "max_results"]},
    {"name": "read_file", "description": "Read the contents of a file", "parameters": ["path"]},
    {"name": "write_file", "description": "Write content to a file", "parameters": ["path", "content"]},
    {"name": "send_email", "description": "Send an email via SMTP", "parameters": ["to", "subject", "body"]},
    {"name": "call_api", "description": "Make an HTTP request to an external API", "parameters": ["url", "method", "headers", "body"]},
    {"name": "run_command", "description": "Execute a shell command", "parameters": ["command"]},
]

app = FastAPI(title="AutoAgent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "https://autoagent-ui.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/tools")
async def list_tools():
    return AVAILABLE_TOOLS


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/sessions/{session_id}/history")
async def session_history(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "messages": SESSIONS[session_id]}


@app.post("/chat")
async def chat(req: ChatRequest):
    async def event_stream():
        try:
            agent = Agent(session_id=req.session_id)
            for event in agent.run(req.message):
                if event["type"] == "tool_call":
                    sse = ToolEvent(
                        type="tool_call",
                        tool=event["tool"],
                        input=event["input"],
                    )
                elif event["type"] == "text":
                    sse = TextEvent(type="text", content=event["content"])
                else:
                    continue

                yield f"data: {json.dumps(sse.model_dump())}\n\n"

        except Exception as e:
            err = ErrorEvent(type="error", message=str(e))
            yield f"data: {json.dumps(err.model_dump())}\n\n"

        finally:
            done = DoneEvent(type="done")
            yield f"data: {json.dumps(done.model_dump())}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
