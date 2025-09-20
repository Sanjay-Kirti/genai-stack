from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base
from app.api.endpoints import workflows, documents, chat
from app.api.websocket.chat_ws import websocket_endpoint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLite engine for testing
sqlite_engine = create_engine("sqlite:///./genai_stack.db", echo=settings.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up GenAI Stack backend with SQLite...")
    # Create database tables
    Base.metadata.create_all(bind=sqlite_engine)
    yield
    # Shutdown
    logger.info("Shutting down GenAI Stack backend...")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME + " (SQLite)",
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

# Override database dependency for SQLite
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Monkey patch the database dependency
import app.core.database
app.core.database.get_db = get_db

# Include routers
app.include_router(workflows.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)

# WebSocket endpoint
@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket, session_id: str):
    await websocket_endpoint(websocket, session_id)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "SQLite"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} (SQLite Mode)",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_sqlite:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
