from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "GenAI Stack"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default="your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost/genai_stack"
    )
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost",
    ]
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # Google Gemini
    GEMINI_API_KEY: Optional[str] = None
    
    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION_NAME: str = "genai_stack_docs"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".txt", ".md", ".doc", ".docx"}
    
    # WebSocket
    WS_MESSAGE_QUEUE: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
