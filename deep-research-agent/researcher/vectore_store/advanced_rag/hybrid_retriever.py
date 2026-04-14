"""
Hybrid Retriever using Qdrant's Native RRF Fusion.

Uses Qdrant's built-in hybrid search with prefetch and RRF.
"""

import logging
from typing import List, Optional
from dataclasses import dataclass
import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

from .hybrid_qdrant_db import HybridQdrantDatabase, SearchResult
from .sparse_vector_generator import SparseEmbedding

load_dotenv()
logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Result from hybrid retrieval."""
    chunk_id: str
    parent_id: str
    text: str
    metadata: dict
    score: float


class HybridRetriever:
    """
    Retrieves chunks using Qdrant's native hybrid search with RRF.
    
    Generates dense (OpenAI) and sparse (FastEmbed BM25) vectors for query,
    then uses Qdrant's query_points with prefetch and RRF fusion.
    """
    
    def __init__(
        self,
        qdrant_db: HybridQdrantDatabase,
        embedding_model: str = "text-embedding-3-small",
        sparse_model: str = "Qdrant/bm25"
    ):
        """
        Initialize hybrid retriever.
        
        Args:
            qdrant_db: HybridQdrantDatabase instance.
            embedding_model: OpenAI embedding model name.
            sparse_model: FastEmbed sparse model name.
        """
        self.qdrant_db = qdrant_db
        self.dense_embedder = OpenAIEmbeddings(
            model=embedding_model,
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        self.sparse_embedder = SparseEmbedding(model_name=sparse_model)
        logger.info("HybridRetriever initialized")
    
    def retrieve(self, query: str, top_k: int = 20) -> List[RetrievalResult]:
        """
        Retrieve relevant chunks using Qdrant's native hybrid search.
        
        Uses prefetch for both dense and sparse vectors with RRF fusion.
        
        Args:
            query: Search query text.
            top_k: Number of results to return.
        
        Returns:
            Top-K results ranked by RRF score.
        """
        if not query.strip():
            return []
        
        query_dense = self.dense_embedder.embed_query(query)
        query_sparse = self.sparse_embedder.embed_query(query)
        
        results = self.qdrant_db.hybrid_search(
            dense_vector=query_dense,
            sparse_vector=query_sparse,
            top_k=top_k
        )
        
        return [
            RetrievalResult(
                chunk_id=r.chunk_id,
                parent_id=r.parent_id,
                text=r.text,
                metadata=r.metadata,
                score=r.score
            )
            for r in results
        ]
