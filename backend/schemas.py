"""Pydantic models for the FastAPI SSE event stream used by the chat endpoint."""

from typing import Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None


class ToolEvent(BaseModel):
    type: Literal["tool_call"]
    tool: str
    input: dict


class TextEvent(BaseModel):
    type: Literal["text"]
    content: str


class ErrorEvent(BaseModel):
    type: Literal["error"]
    message: str


class DoneEvent(BaseModel):
    type: Literal["done"]
