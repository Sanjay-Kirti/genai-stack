from typing import List, Optional
import numpy as np
import openai
import google.generativeai as genai
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.openai_client = None
        self.gemini_model = None
        
        # Initialize OpenAI if API key is available
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_client = openai
            
        # Initialize Gemini if API key is available
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
    
    async def generate_embeddings(
        self,
        texts: List[str],
        provider: str = "openai",
        model: Optional[str] = None
    ) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        
        try:
            if provider == "openai":
                return await self._openai_embeddings(texts, model)
            elif provider == "gemini":
                return await self._gemini_embeddings(texts, model)
            else:
                raise ValueError(f"Unsupported embedding provider: {provider}")
                
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    async def _openai_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """Generate embeddings using OpenAI."""
        
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")
        
        model = model or "text-embedding-ada-002"
        
        # OpenAI embedding API can handle batch requests
        response = await self.openai_client.Embedding.acreate(
            model=model,
            input=texts
        )
        
        embeddings = [item.embedding for item in response.data]
        return embeddings
    
    async def _gemini_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """Generate embeddings using Google Gemini."""
        
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API key not configured")
        
        model = model or "models/embedding-001"
        
        embeddings = []
        for text in texts:
            result = genai.embed_content(
                model=model,
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result['embedding'])
        
        return embeddings
    
    def cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between two embeddings."""
        
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def batch_embeddings(
        self,
        texts: List[str],
        batch_size: int = 100,
        provider: str = "openai",
        model: Optional[str] = None
    ) -> List[List[float]]:
        """Generate embeddings in batches for large text lists."""
        
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = await self.generate_embeddings(
                batch, provider, model
            )
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
