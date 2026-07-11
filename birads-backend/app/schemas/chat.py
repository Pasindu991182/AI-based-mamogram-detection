from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    # Keeps per-conversation memory; the frontend generates one per chat window.
    session_id: str = "default"
    # Optional: attach a case so the assistant can reason about live values.
    case_id: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []
    session_id: str


class ChatStatus(BaseModel):
    ready: bool
    key_configured: bool
    index_ready: bool
    llm_model: str
    embed_model: str
