from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import json

from app.core.database import get_db
from app.core.config import settings
from app.models import Document
from app.schemas.document import (
    DocumentResponse,
    DocumentProcessResult,
    DocumentSearchRequest,
    DocumentSearchResult
)
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService

router = APIRouter(prefix="/documents", tags=["documents"])
document_service = DocumentService()
embedding_service = EmbeddingService()
vector_store_service = VectorStoreService()


@router.post("/upload", response_model=DocumentProcessResult)
async def upload_document(
    file: UploadFile = File(...),
    workflow_id: Optional[str] = Form(None),
    embedding_provider: str = Form("openai"),
    db: Session = Depends(get_db)
):
    """Upload and process a document."""
    
    # Validate file
    file_content = await file.read()
    try:
        document_service.validate_file(
            filename=file.filename,
            file_size=len(file_content),
            max_size=settings.MAX_UPLOAD_SIZE
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Process document
    try:
        processed = await document_service.process_document(
            file_content=file_content,
            filename=file.filename,
            metadata={"workflow_id": workflow_id} if workflow_id else {}
        )
        
        # Save to database
        db_document = Document(
            workflow_id=UUID(workflow_id) if workflow_id else None,
            filename=file.filename,
            content=processed["text"],
            metadata=processed["metadata"]
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Generate embeddings
        embeddings = await embedding_service.batch_embeddings(
            texts=processed["chunks"],
            provider=embedding_provider
        )
        
        # Store in vector database
        chunk_ids = await vector_store_service.add_documents(
            documents=processed["chunks"],
            embeddings=embeddings,
            metadatas=[
                {
                    **processed["metadata"],
                    "document_id": str(db_document.id),
                    "chunk_index": i
                }
                for i in range(len(processed["chunks"]))
            ]
        )
        
        return DocumentProcessResult(
            document_id=db_document.id,
            filename=file.filename,
            chunks_created=len(processed["chunks"]),
            embeddings_generated=len(embeddings),
            metadata=processed["metadata"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific document by ID."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a document and its embeddings."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    
    # Delete from vector store
    try:
        await vector_store_service.delete_documents(
            where={"document_id": str(document_id)}
        )
    except Exception as e:
        # Log error but continue with database deletion
        print(f"Error deleting from vector store: {e}")
    
    # Delete from database
    db.delete(document)
    db.commit()


@router.post("/search", response_model=DocumentSearchResult)
async def search_documents(
    search_request: DocumentSearchRequest
):
    """Search for similar documents."""
    try:
        where_filter = None
        if search_request.workflow_id:
            where_filter = {"workflow_id": str(search_request.workflow_id)}
        
        results = await vector_store_service.search_by_text(
            query_text=search_request.query,
            embedding_service=embedding_service,
            n_results=search_request.n_results,
            provider=search_request.embedding_provider,
            where=where_filter
        )
        
        return DocumentSearchResult(**results)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching documents: {str(e)}"
        )


@router.post("/extract-text")
async def extract_text(
    file: UploadFile = File(...)
):
    """Extract text from a document without storing it."""
    file_content = await file.read()
    
    try:
        text = await document_service.extract_text_from_file(
            file_content=file_content,
            filename=file.filename
        )
        
        return {
            "filename": file.filename,
            "text": text,
            "length": len(text)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error extracting text: {str(e)}"
        )


@router.post("/generate-embeddings")
async def generate_embeddings(
    texts: List[str],
    provider: str = "openai"
):
    """Generate embeddings for provided texts."""
    try:
        embeddings = await embedding_service.generate_embeddings(
            texts=texts,
            provider=provider
        )
        
        return {
            "embeddings": embeddings,
            "count": len(embeddings),
            "provider": provider
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating embeddings: {str(e)}"
        )
