from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import asyncio
import json
from contextlib import asynccontextmanager
from typing import Dict

from app.core.database import get_db, Base, engine
from app.api.endpoints import workflows, chat, documents
from app.services.vector_store_service import VectorStoreService
from app.services.workflow_engine import WorkflowEngine
from app.models.workflow import Workflow
from app.core.config import settings
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)

manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up GenAI Stack backend...")
    # Create database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    logger.info("Shutting down GenAI Stack backend...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workflows.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)

# WebSocket endpoint
@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    logger.info(f"WebSocket connection attempt for session {session_id}")
    await manager.connect(websocket, session_id)
    logger.info(f"WebSocket connected for session {session_id}")
    
    try:
        # Send a welcome message to confirm connection
        await manager.send_message(json.dumps({
            "type": "system",
            "message": "Connected to chat",
            "timestamp": asyncio.get_event_loop().time()
        }), session_id)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            logger.info(f"Received message: {data}")
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            if user_message:
                # Send user message back to confirm receipt
                await manager.send_message(json.dumps({
                    "type": "user_message",
                    "message": user_message,
                    "timestamp": asyncio.get_event_loop().time()
                }), session_id)
                
                # Send thinking status
                await manager.send_message(json.dumps({
                    "type": "thinking",
                    "status": True
                }), session_id)
                
                try:
                    # Get the workflow for this session
                    db = next(get_db())
                    try:
                        # Get chat session to find workflow
                        from app.models.chat import ChatSession
                        chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
                        if not chat_session:
                            raise ValueError("Chat session not found")
                        
                        # Get the workflow
                        workflow = db.query(Workflow).filter(Workflow.id == chat_session.workflow_id).first()
                        if not workflow:
                            raise ValueError("Workflow not found")
                        
                        # Execute the workflow
                        workflow_engine = WorkflowEngine()
                        result = await workflow_engine.execute_workflow(
                            workflow_config=workflow.configuration,
                            user_input=user_message,
                            session_id=session_id
                        )
                        
                        # Extract the response from the output
                        output = result.get("output", [])
                        if output and len(output) > 0:
                            response = output[0].get("content", "No response generated")
                        else:
                            response = "No output generated from workflow"
                        
                        # Send assistant response
                        await manager.send_message(json.dumps({
                            "type": "assistant_message",
                            "message": response,
                            "timestamp": asyncio.get_event_loop().time()
                        }), session_id)
                        
                    finally:
                        db.close()
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    await manager.send_message(json.dumps({
                        "type": "error",
                        "message": f"Error processing message: {str(e)}"
                    }), session_id)
                finally:
                    # Stop thinking
                    await manager.send_message(json.dumps({
                        "type": "thinking",
                        "status": False
                    }), session_id)
                    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        manager.disconnect(session_id)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
