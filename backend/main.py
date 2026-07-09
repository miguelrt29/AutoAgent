"""FastAPI entrypoint: starts the server, registers routes, and initialises the app."""

import json

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session as DBSession
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from agent import Agent, SESSIONS, LOCAL_TOOLS_DEFS
from config import CONFIG
from schemas import ChatRequest, ToolEvent, TextEvent, ErrorEvent, DoneEvent
from database import get_db, get_db_sync, create_session, get_session, get_all_sessions, delete_session, update_session_title, touch_session, toggle_pin_session, add_message, get_messages, PINNED_SESSIONS
from db_schemas import SessionOut, SessionDetailOut, MessageOut, UpdateTitleRequest


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


# ─── Session endpoints ───


@app.get("/sessions", response_model=list[SessionOut])
async def list_sessions(db: DBSession = Depends(get_db)):
    sessions = get_all_sessions(db)
    result = []
    for s in sessions:
        out = SessionOut.model_validate(s)
        out.pinned = s.id in PINNED_SESSIONS
        result.append(out)
    return result


@app.get("/sessions/{session_id}", response_model=SessionDetailOut)
async def get_session_detail(session_id: str, db: DBSession = Depends(get_db)):
    session = get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = get_messages(db, session_id)
    return SessionDetailOut(
        id=session.id,
        title=session.title,
        pinned=session.id in PINNED_SESSIONS,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=[MessageOut.model_validate(m) for m in messages],
    )


@app.put("/sessions/{session_id}/title")
async def update_title(session_id: str, req: UpdateTitleRequest, db: DBSession = Depends(get_db)):
    session = update_session_title(db, session_id, req.title)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    out = SessionOut.model_validate(session)
    out.pinned = session.id in PINNED_SESSIONS
    return out


@app.put("/sessions/{session_id}/pin")
async def pin_session(session_id: str, db: DBSession = Depends(get_db)):
    session = toggle_pin_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    out = SessionOut.model_validate(session)
    out.pinned = session.id in PINNED_SESSIONS
    return out


@app.delete("/sessions/{session_id}")
async def delete_session_endpoint(session_id: str, db: DBSession = Depends(get_db)):
    if not delete_session(db, session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"ok": True}


# ─── Chat endpoint ───


@app.post("/chat")
async def chat(req: ChatRequest):
    db = get_db_sync()
    session_id = req.session_id

    if session_id:
        sess = get_session(db, session_id)
        if not sess:
            create_session(db, session_id)
            touch_session(db, session_id)
    else:
        import uuid
        session_id = str(uuid.uuid4())
        create_session(db, session_id)

    async def event_stream():
        nonlocal session_id
        try:
            agent = Agent(session_id=session_id, db=db)
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
            db.close()
            done = DoneEvent(type="done")
            yield f"data: {json.dumps(done.model_dump())}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
