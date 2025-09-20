from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class DocumentBase(BaseModel):
    filename: str
    doc_metadata: Optional[Dict[str, Any]] = None


class DocumentUpload(BaseModel):
    workflow_id: Optional[UUID] = None
    embedding_provider: str = "openai"


class DocumentResponse(DocumentBase):
    id: UUID
    workflow_id: Optional[UUID]
    content: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentProcessResult(BaseModel):
    document_id: UUID
    filename: str
    chunks_created: int
    embeddings_generated: int
    metadata: Dict[str, Any]


class DocumentSearchRequest(BaseModel):
    query: str
    workflow_id: Optional[UUID] = None
    n_results: int = Field(default=5, ge=1, le=20)
    embedding_provider: str = "openai"


class DocumentSearchResult(BaseModel):
    documents: List[str]
    distances: List[float]
    metadatas: List[Dict[str, Any]]
    ids: List[str]
