from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models import ChatSession, ChatMessage, Workflow
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatRequest
)
from app.services.workflow_engine import WorkflowEngine

router = APIRouter(prefix="/chat", tags=["chat"])
workflow_engine = WorkflowEngine()


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session: ChatSessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new chat session."""
    # Verify workflow exists
    workflow = db.query(Workflow).filter(Workflow.id == session.workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {session.workflow_id} not found"
        )
    
    db_session = ChatSession(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a chat session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    return session


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    session_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get messages for a chat session."""
    # Verify session exists
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).offset(skip).limit(limit).all()
    
    return messages


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    session_id: UUID,
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Send a message in a chat session and get response."""
    # Get session and workflow
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    workflow = db.query(Workflow).filter(Workflow.id == session.workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {session.workflow_id} not found"
        )
    
    # Save user message
    user_message = ChatMessage(
        session_id=session_id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()
    
    try:
        # Execute workflow with user input
        result = await workflow_engine.execute_workflow(
            workflow_config={
                "id": str(workflow.id),
                **workflow.configuration
            },
            user_input=request.message,
            session_id=str(session_id)
        )
        
        # Extract response from output
        response_content = ""
        if result["output"]:
            response_content = result["output"][0].get("content", "No response generated")
        
        # Save assistant message
        assistant_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=response_content,
            metadata={"execution_summary": result["execution_summary"]}
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)
        
        return assistant_message
        
    except Exception as e:
        # Save error message
        error_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=f"Error processing request: {str(e)}",
            metadata={"error": True}
        )
        db.add(error_message)
        db.commit()
        db.refresh(error_message)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a chat session and all its messages."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    db.delete(session)
    db.commit()
