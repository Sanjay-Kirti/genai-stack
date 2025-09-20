from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from app.core.config import settings as app_settings
import logging
import uuid

logger = logging.getLogger(__name__)


class VectorStoreService:
    def __init__(self):
        self.client = None
        self.collection = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client."""
        try:
            self.client = chromadb.HttpClient(
                host=app_settings.CHROMA_HOST,
                port=app_settings.CHROMA_PORT,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=app_settings.CHROMA_COLLECTION_NAME,
                metadata={"description": "GenAI Stack document embeddings"}
            )
            
            logger.info(f"Connected to ChromaDB at {app_settings.CHROMA_HOST}:{app_settings.CHROMA_PORT}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {str(e)}")
            # Fallback to in-memory client for development
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(
                name=app_settings.CHROMA_COLLECTION_NAME
            )
            logger.warning("Using in-memory ChromaDB client")
    
    async def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add documents with their embeddings to the vector store."""
        
        if not ids:
            ids = [str(uuid.uuid4()) for _ in range(len(documents))]
        
        if not metadatas:
            metadatas = [{} for _ in range(len(documents))]
        
        try:
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to vector store")
            return ids
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise
    
    async def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for similar documents using query embedding."""
        
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            
            # Format results
            formatted_results = {
                "documents": results.get("documents", [[]])[0],
                "distances": results.get("distances", [[]])[0],
                "metadatas": results.get("metadatas", [[]])[0],
                "ids": results.get("ids", [[]])[0]
            }
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise
    
    async def search_by_text(
        self,
        query_text: str,
        embedding_service,
        n_results: int = 5,
        provider: str = "openai",
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for similar documents using text query."""
        
        # Generate embedding for query
        query_embeddings = await embedding_service.generate_embeddings(
            [query_text], provider=provider
        )
        query_embedding = query_embeddings[0]
        
        # Search using embedding
        return await self.search(
            query_embedding=query_embedding,
            n_results=n_results,
            where=where
        )
    
    async def update_document(
        self,
        document_id: str,
        document: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Update a document in the vector store."""
        
        try:
            update_params = {"ids": [document_id]}
            
            if document:
                update_params["documents"] = [document]
            if embedding:
                update_params["embeddings"] = [embedding]
            if metadata:
                update_params["metadatas"] = [metadata]
            
            self.collection.update(**update_params)
            
            logger.info(f"Updated document {document_id} in vector store")
            
        except Exception as e:
            logger.error(f"Error updating document in vector store: {str(e)}")
            raise
    
    async def delete_documents(
        self,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None
    ):
        """Delete documents from the vector store."""
        
        try:
            if ids:
                self.collection.delete(ids=ids)
                logger.info(f"Deleted {len(ids)} documents from vector store")
            elif where:
                self.collection.delete(where=where)
                logger.info(f"Deleted documents matching criteria from vector store")
            else:
                raise ValueError("Either ids or where must be provided")
                
        except Exception as e:
            logger.error(f"Error deleting documents from vector store: {str(e)}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID."""
        
        try:
            result = self.collection.get(ids=[document_id])
            
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "document": result.get("documents", [None])[0],
                    "metadata": result.get("metadatas", [{}])[0]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting document from vector store: {str(e)}")
            raise
    
    async def list_documents(
        self,
        limit: int = 100,
        offset: int = 0,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List documents in the vector store."""
        
        try:
            # ChromaDB doesn't have direct pagination, so we get all and slice
            result = self.collection.get(where=where)
            
            documents = []
            for i in range(offset, min(offset + limit, len(result["ids"]))):
                documents.append({
                    "id": result["ids"][i],
                    "document": result.get("documents", [])[i] if result.get("documents") else None,
                    "metadata": result.get("metadatas", [])[i] if result.get("metadatas") else {}
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Error listing documents from vector store: {str(e)}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        
        try:
            count = self.collection.count()
            
            return {
                "name": self.collection.name,
                "count": count,
                "metadata": self.collection.metadata
            }
            
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            raise
