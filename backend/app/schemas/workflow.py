from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID


class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    configuration: Dict[str, Any]


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None


class WorkflowResponse(WorkflowBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkflowValidation(BaseModel):
    valid: bool
    errors: List[str]
    warnings: List[str]


class WorkflowExecute(BaseModel):
    user_input: str
    session_id: Optional[str] = None


class WorkflowExecutionResult(BaseModel):
    output: List[Dict[str, Any]]
    context: Dict[str, Any]
    execution_summary: Dict[str, Any]
