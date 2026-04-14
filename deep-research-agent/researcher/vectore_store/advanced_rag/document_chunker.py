"""
Document Chunker using LangChain's RecursiveCharacterTextSplitter.

Splits parent documents into child chunks with parent_id references.
"""

import logging
import uuid
from typing import List, Optional
from dataclasses import dataclass, field
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """
    Child chunk with reference to parent document.
    
    Attributes:
        chunk_id: Unique identifier for this chunk.
        parent_id: Reference to parent document in Redis.
        text: Text content of the chunk.
        metadata: Additional metadata from parent.
    """
    chunk_id: str
    parent_id: str
    text: str
    metadata: dict = field(default_factory=dict)


class DocumentChunker:
    """
    Splits documents into chunks using LangChain's RecursiveCharacterTextSplitter.
    
    Each chunk maintains a parent_id reference for later retrieval of
    full parent document context.
    """
    
    def __init__(self, chunk_size: int = 200, chunk_overlap: int = 50):
        """
        Initialize chunker with LangChain text splitter.
        
        Args:
            chunk_size: Maximum characters per chunk.
            chunk_overlap: Overlap between consecutive chunks.
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        logger.info(f"DocumentChunker initialized: size={chunk_size}, overlap={chunk_overlap}")
    
    def chunk_document(
        self,
        parent_id: str,
        text: str,
        metadata: Optional[dict] = None
    ) -> List[DocumentChunk]:
        """
        Split document into chunks with parent_id references.
        
        Args:
            parent_id: ID of parent document in Redis.
            text: Full document text to split.
            metadata: Optional metadata to include in each chunk.
        
        Returns:
            List of DocumentChunk objects.
        """
        if not text or not text.strip():
            return []
        
        chunk_texts = self.splitter.split_text(text)
        
        return [
            DocumentChunk(
                chunk_id=f"{parent_id}_chunk_{i}",
                parent_id=parent_id,
                text=chunk_text,
                metadata=metadata or {}
            )
            for i, chunk_text in enumerate(chunk_texts)
        ]
