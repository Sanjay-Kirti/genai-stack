from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class ChatSessionBase(BaseModel):
    workflow_id: UUID


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionResponse(ChatSessionBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatMessageBase(BaseModel):
    content: str
    role: str = Field(..., pattern="^(user|assistant|system)$")
    msg_metadata: Optional[Dict[str, Any]] = None


class ChatMessageCreate(ChatMessageBase):
    session_id: UUID


class ChatMessageResponse(ChatMessageBase):
    id: UUID
    session_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    session_id: UUID
    stream: bool = False
