from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


class MessageOut(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    tool_calls: Optional[Any] = None
    tool_call_id: Optional[str] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class SessionOut(BaseModel):
    id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SessionDetailOut(BaseModel):
    id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageOut]


class UpdateTitleRequest(BaseModel):
    title: str
