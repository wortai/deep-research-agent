"""
Hybrid Qdrant Database with Native RRF Fusion.

Uses Qdrant's query_points with prefetch and RrfQuery for hybrid search.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import os
from dotenv import load_dotenv

from qdrant_client import QdrantClient, models

load_dotenv()
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result from Qdrant search."""
    chunk_id: str
    parent_id: str
    text: str
    metadata: Dict[str, Any]
    score: float


class HybridQdrantDatabase:
    """
    Qdrant collection with native hybrid search using RRF fusion.
    
    Uses Qdrant's query_points API with prefetch for both dense and sparse
    vectors, then applies RRF (Reciprocal Rank Fusion) to combine results.
    """
    
    DENSE_NAME = "dense"
    SPARSE_NAME = "sparse"
    
    def __init__(
        self,
        collection_name: str = "advanced_rag_docs",
        dense_size: int = 1536,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None
    ):
        """
        Initialize Qdrant client and create hybrid collection.
        
        Args:
            collection_name: Name for the Qdrant collection.
            dense_size: Dimension of dense embedding vectors (1536 for OpenAI).
            qdrant_url: Qdrant server URL (defaults to env QDRANT_URL).
            qdrant_api_key: Qdrant API key (defaults to env QDRANT_API_KEY).
        """
        self.collection_name = collection_name
        self.dense_size = dense_size
        
        self.client = QdrantClient(
            url=qdrant_url or os.environ.get("QDRANT_URL"),
            api_key=qdrant_api_key or os.environ.get("QDRANT_API_KEY")
        )
        
        self._ensure_collection()
        logger.info(f"HybridQdrantDatabase initialized: {collection_name}")
    
    def _ensure_collection(self) -> None:
        """Create hybrid collection if it doesn't exist."""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    self.DENSE_NAME: models.VectorParams(
                        size=self.dense_size,
                        distance=models.Distance.COSINE
                    )
                },
                sparse_vectors_config={
                    self.SPARSE_NAME: models.SparseVectorParams()
                }
            )
            logger.info(f"Created hybrid collection: {self.collection_name}")
    
    def upsert_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Batch upsert chunks with hybrid vectors.
        
        Each chunk dict should contain:
        - chunk_id, parent_id, text, dense_vector, sparse_vector, metadata
        """
        points = []
        for c in chunks:
            # Build vectors dict with both dense and sparse vectors
            vectors = {
                self.DENSE_NAME: c["dense_vector"],
                self.SPARSE_NAME: models.SparseVector(
                    indices=c["sparse_vector"]["indices"],
                    values=c["sparse_vector"]["values"]
                )
            }
            
            point = models.PointStruct(
                id=hash(c["chunk_id"]) % (2**63),
                payload={"parent_id": c["parent_id"], "text": c["text"], **c.get("metadata", {})},
                vector=vectors
            )
            points.append(point)
        
        self.client.upsert(collection_name=self.collection_name, points=points)
        logger.info(f"Upserted {len(points)} chunks")
        return len(points)
    
    def hybrid_search(
        self,
        dense_vector: List[float],
        sparse_vector: Dict[str, Any],
        top_k: int = 20,
        rrf_k: int = 60
    ) -> List[SearchResult]:
        """
        Perform hybrid search using Qdrant's native RRF fusion.
        
        Uses query_points with prefetch for both dense and sparse vectors,
        then applies RRF to combine results.
        
        Args:
            dense_vector: Dense embedding vector.
            sparse_vector: Sparse vector dict with 'indices' and 'values'.
            top_k: Number of results to return.
            rrf_k: RRF constant (default: 60).
        
        Returns:
            List of SearchResult ordered by RRF score.
        """
        results = self.client.query_points(
            collection_name=self.collection_name,
            prefetch=[
                models.Prefetch(
                    query=models.SparseVector(
                        indices=sparse_vector["indices"],
                        values=sparse_vector["values"]
                    ),
                    using=self.SPARSE_NAME,
                    limit=top_k * 2
                ),
                models.Prefetch(
                    query=dense_vector,
                    using=self.DENSE_NAME,
                    limit=top_k * 2
                )
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=top_k,
            with_payload=True
        )
        
        return self._to_results(results.points)
    
    def _to_results(self, points) -> List[SearchResult]:
        """Convert Qdrant points to SearchResult objects."""
        return [
            SearchResult(
                chunk_id=str(p.id),
                parent_id=p.payload.get("parent_id", ""),
                text=p.payload.get("text", ""),
                metadata={k: v for k, v in p.payload.items() if k not in ["parent_id", "text"]},
                score=p.score
            )
            for p in points
        ]
