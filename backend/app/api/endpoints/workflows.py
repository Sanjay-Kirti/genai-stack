from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models import Workflow
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowValidation,
    WorkflowExecute,
    WorkflowExecutionResult
)
from app.services.workflow_engine import WorkflowEngine

router = APIRouter(prefix="/workflows", tags=["workflows"])
workflow_engine = WorkflowEngine()


@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all workflows."""
    workflows = db.query(Workflow).offset(skip).limit(limit).all()
    return workflows


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow: WorkflowCreate,
    db: Session = Depends(get_db)
):
    """Create a new workflow."""
    db_workflow = Workflow(**workflow.dict())
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific workflow by ID."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID,
    workflow_update: WorkflowUpdate,
    db: Session = Depends(get_db)
):
    """Update a workflow."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )
    
    update_data = workflow_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workflow, field, value)
    
    db.commit()
    db.refresh(workflow)
    return workflow


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a workflow."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )
    
    db.delete(workflow)
    db.commit()


@router.post("/{workflow_id}/validate", response_model=WorkflowValidation)
async def validate_workflow(
    workflow_id: UUID,
    db: Session = Depends(get_db)
):
    """Validate a workflow configuration."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )
    
    validation_result = await workflow_engine.validate_workflow(workflow.configuration)
    return validation_result


@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResult)
async def execute_workflow(
    workflow_id: UUID,
    execution_request: WorkflowExecute,
    db: Session = Depends(get_db)
):
    """Execute a workflow with user input."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )
    
    try:
        result = await workflow_engine.execute_workflow(
            workflow_config={
                "id": str(workflow.id),
                **workflow.configuration
            },
            user_input=execution_request.user_input,
            session_id=execution_request.session_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing workflow: {str(e)}"
        )
