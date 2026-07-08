"""FastAPI entrypoint: starts the server, registers routes, and initialises the app."""

import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from agent import Agent, SESSIONS, LOCAL_TOOLS_DEFS
from config import CONFIG
from schemas import ChatRequest, ToolEvent, TextEvent, ErrorEvent, DoneEvent


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

AVAILABLE_TOOLS = [
    {"name": "web_search", "description": "Search the web using DuckDuckGo", "parameters": ["query", "max_results"]},
    {"name": "send_email", "description": "Send an email via SMTP", "parameters": ["to", "subject", "body"]},
    {"name": "call_api", "description": "Make an HTTP request to an external API", "parameters": ["url", "method", "headers", "body"]},
]

if CONFIG["ENABLE_LOCAL_TOOLS"]:
    for td in LOCAL_TOOLS_DEFS:
        fn = td["function"]
        AVAILABLE_TOOLS.append({
            "name": fn["name"],
            "description": fn["description"],
            "parameters": list(fn["parameters"]["properties"].keys()),
        })

app = FastAPI(title="AutoAgent API", version="1.0.0")

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
