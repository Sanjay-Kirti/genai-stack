from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, Set
import json
import asyncio
from uuid import UUID

from app.core.database import get_db
from app.models import ChatSession, ChatMessage, Workflow
from app.services.workflow_engine import WorkflowEngine


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast_to_session(self, message: str, session_id: str):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(message)
                except:
                    pass


manager = ConnectionManager()
workflow_engine = WorkflowEngine()


async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time chat."""
    
    # Verify session exists
    chat_session = db.query(ChatSession).filter(
        ChatSession.id == UUID(session_id)
    ).first()
    
    if not chat_session:
        await websocket.close(code=4004, reason="Session not found")
        return
    
    # Get workflow
    workflow = db.query(Workflow).filter(
        Workflow.id == chat_session.workflow_id
    ).first()
    
    if not workflow:
        await websocket.close(code=4004, reason="Workflow not found")
        return
    
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Save user message
            user_message = ChatMessage(
                session_id=UUID(session_id),
                role="user",
                content=message_data["message"]
            )
            db.add(user_message)
            db.commit()
            
            # Broadcast user message
            await manager.broadcast_to_session(
                json.dumps({
                    "type": "user_message",
                    "message": message_data["message"],
                    "timestamp": user_message.created_at.isoformat()
                }),
                session_id
            )
            
            # Send thinking indicator
            await manager.broadcast_to_session(
                json.dumps({"type": "thinking", "status": True}),
                session_id
            )
            
            try:
                # Execute workflow
                result = await workflow_engine.execute_workflow(
                    workflow_config={
                        "id": str(workflow.id),
                        **workflow.configuration
                    },
                    user_input=message_data["message"],
                    session_id=session_id
                )
                
                # Extract response
                response_content = ""
                if result["output"]:
                    response_content = result["output"][0].get("content", "No response generated")
                
                # Save assistant message
                assistant_message = ChatMessage(
                    session_id=UUID(session_id),
                    role="assistant",
                    content=response_content,
                    metadata={"execution_summary": result["execution_summary"]}
                )
                db.add(assistant_message)
                db.commit()
                
                # Send response
                await manager.broadcast_to_session(
                    json.dumps({
                        "type": "assistant_message",
                        "message": response_content,
                        "timestamp": assistant_message.created_at.isoformat()
                    }),
                    session_id
                )
                
            except Exception as e:
                # Send error message
                await manager.broadcast_to_session(
                    json.dumps({
                        "type": "error",
                        "message": f"Error processing request: {str(e)}"
                    }),
                    session_id
                )
            
            finally:
                # Stop thinking indicator
                await manager.broadcast_to_session(
                    json.dumps({"type": "thinking", "status": False}),
                    session_id
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, session_id)
