from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - Skip database creation for dev mode
    logger.info("Starting up GenAI Stack backend (Development Mode - No Database)...")
    yield
    # Shutdown
    logger.info("Shutting down GenAI Stack backend...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME + " (Dev Mode)",
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

# Import only LLM-related endpoints (no database required)
from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService

llm_service = LLMService()
embedding_service = EmbeddingService()

# Simple test endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mode": "development"
    }

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} (Development Mode)",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "note": "Database features disabled for quick testing"
    }

@app.post("/test-llm")
async def test_llm(prompt: str = "Hello, how are you?"):
    """Test LLM functionality without database"""
    try:
        response = await llm_service.generate_completion(
            prompt=prompt,
            temperature=0.7
        )
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

@app.post("/test-embeddings")
async def test_embeddings(text: str = "Hello world"):
    """Test embedding generation"""
    try:
        embeddings = await embedding_service.generate_embeddings([text])
        return {
            "text": text,
            "embedding_length": len(embeddings[0]) if embeddings else 0,
            "success": True
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_dev:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
