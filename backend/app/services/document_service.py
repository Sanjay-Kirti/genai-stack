import os
import io
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
from pathlib import Path
import logging
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self):
        self.supported_formats = {'.pdf', '.txt', '.md', '.doc', '.docx'}
    
    async def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file."""
        try:
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
            text = ""
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text += page.get_text()
            
            pdf_document.close()
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
    
    async def extract_text_from_file(
        self,
        file_content: bytes,
        filename: str
    ) -> str:
        """Extract text from various file formats."""
        
        file_ext = Path(filename).suffix.lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        try:
            if file_ext == '.pdf':
                return await self.extract_text_from_pdf(file_content)
            elif file_ext in ['.txt', '.md']:
                return file_content.decode('utf-8', errors='ignore')
            elif file_ext in ['.doc', '.docx']:
                # For Word documents, we'd need python-docx library
                # This is a placeholder for now
                raise NotImplementedError("Word document support coming soon")
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
                
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {str(e)}")
            raise
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[str]:
        """Split text into overlapping chunks."""
        
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            
            # Try to find a sentence boundary
            if end < text_length:
                # Look for sentence endings
                for delimiter in ['. ', '.\n', '! ', '!\n', '? ', '?\n']:
                    delimiter_pos = text.rfind(delimiter, start, end)
                    if delimiter_pos != -1:
                        end = delimiter_pos + len(delimiter)
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - chunk_overlap if end < text_length else text_length
        
        return chunks
    
    async def process_document(
        self,
        file_content: bytes,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a document and prepare it for embedding."""
        
        # Extract text
        text = await self.extract_text_from_file(file_content, filename)
        
        # Generate document hash for deduplication
        doc_hash = hashlib.md5(file_content).hexdigest()
        
        # Chunk the text
        chunks = self.chunk_text(text)
        
        # Prepare metadata
        doc_metadata = {
            "filename": filename,
            "file_size": len(file_content),
            "doc_hash": doc_hash,
            "total_chunks": len(chunks),
            "processed_at": datetime.utcnow().isoformat(),
            **(metadata or {})
        }
        
        return {
            "text": text,
            "chunks": chunks,
            "metadata": doc_metadata
        }
    
    def validate_file(
        self,
        filename: str,
        file_size: int,
        max_size: int = 10 * 1024 * 1024  # 10MB default
    ) -> bool:
        """Validate file before processing."""
        
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Check file size
        if file_size > max_size:
            raise ValueError(f"File size exceeds maximum allowed size of {max_size} bytes")
        
        return True
    
    async def extract_metadata(
        self,
        file_content: bytes,
        filename: str
    ) -> Dict[str, Any]:
        """Extract metadata from document."""
        
        metadata = {
            "filename": filename,
            "file_size": len(file_content),
            "file_extension": Path(filename).suffix.lower()
        }
        
        file_ext = Path(filename).suffix.lower()
        
        if file_ext == '.pdf':
            try:
                pdf_document = fitz.open(stream=file_content, filetype="pdf")
                metadata.update({
                    "page_count": pdf_document.page_count,
                    "pdf_metadata": pdf_document.metadata
                })
                pdf_document.close()
            except Exception as e:
                logger.error(f"Error extracting PDF metadata: {str(e)}")
        
        return metadata
    
    def prepare_for_embedding(
        self,
        chunks: List[str],
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Prepare document chunks for embedding with metadata."""
        
        prepared_chunks = []
        
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                "chunk_index": i,
                "chunk_text_length": len(chunk)
            }
            
            prepared_chunks.append({
                "text": chunk,
                "metadata": chunk_metadata
            })
        
        return prepared_chunks
