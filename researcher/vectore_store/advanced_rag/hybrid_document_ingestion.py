"""
Hybrid Document Ingestion for Advanced RAG.

Orchestrates ingestion: Redis parent storage + Qdrant hybrid vectors.
"""

import logging
import uuid
from typing import List, Dict, Optional
import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

from .redis_parent_store import RedisParentStore
from .hybrid_qdrant_db import HybridQdrantDatabase
from .sparse_vector_generator import SparseEmbedding
from .document_chunker import DocumentChunker

load_dotenv()
logger = logging.getLogger(__name__)


class HybridDocumentIngestion:
    """
    Orchestrates complete document ingestion pipeline.
    
    Ingestion Steps:
    1. Store full parent document in Redis with unique ID
    2. Split into child chunks using LangChain splitter
    3. Generate dense vectors (OpenAI embeddings)
    4. Generate sparse vectors (FastEmbed BM25)
    5. Upload to Qdrant with parent_id references
    """
    
    def __init__(
        self,
        parent_store: Optional[RedisParentStore] = None,
        qdrant_db: Optional[HybridQdrantDatabase] = None,
        collection_name: str = "advanced_rag_docs",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        embedding_model: str = "text-embedding-3-small"
    ):
        """
        Initialize ingestion pipeline components.
        
        Args:
            parent_store: RedisParentStore instance.
            qdrant_db: HybridQdrantDatabase instance.
            collection_name: Qdrant collection name.
            chunk_size: Characters per chunk.
            chunk_overlap: Overlap between chunks.
            embedding_model: OpenAI embedding model.
        """
        self.parent_store = parent_store or RedisParentStore()
        self.qdrant_db = qdrant_db or HybridQdrantDatabase(collection_name=collection_name)
        self.chunker = DocumentChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.dense_embedder = OpenAIEmbeddings(
            model=embedding_model,
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        self.sparse_embedder = SparseEmbedding()
        logger.info("HybridDocumentIngestion initialized")
    
    def ingest(self, documents: List[Dict[str, str]]) -> int:
        """
        Ingest multiple documents.
        
        Each document dict should have:
        - content: str - Full document text
        - url: Optional[str] - Source URL
        - title: Optional[str] - Document title
        
        Args:
            documents: List of document dicts.
        
        Returns:
            Number of chunks indexed.
        """
        if not documents:
            return 0
        
        all_chunks = []
        
        for doc in documents:
            parent_id = str(uuid.uuid4())
            
            self.parent_store.store(
                parent_id=parent_id,
                content=doc["content"],
                metadata={"source": doc.get("url", ""), "title": doc.get("title", "")}
            )
            
            chunks = self.chunker.chunk_document(
                parent_id=parent_id,
                text=doc["content"],
                metadata={"source": doc.get("url", ""), "title": doc.get("title", "")}
            )
            all_chunks.extend(chunks)
        
        if not all_chunks:
            return 0
        
        chunk_texts = [c.text for c in all_chunks]
        dense_vectors = self.dense_embedder.embed_documents(chunk_texts)
        sparse_vectors = self.sparse_embedder.embed_documents(chunk_texts)
        
        qdrant_chunks = [
            {
                "chunk_id": c.chunk_id,
                "parent_id": c.parent_id,
                "text": c.text,
                "dense_vector": dense_vectors[i],
                "sparse_vector": sparse_vectors[i],
                "metadata": c.metadata
            }
            for i, c in enumerate(all_chunks)
        ]
        
        count = self.qdrant_db.upsert_chunks(qdrant_chunks)
        logger.info(f"Ingested {len(documents)} docs → {count} chunks")
        return count
