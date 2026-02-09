"""
Cross-Encoder Reranker for Advanced RAG.

Uses cross-encoder model to rerank retrieval candidates with high precision.
"""

import logging
from typing import List
from dataclasses import dataclass
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)


@dataclass
class RerankResult:
    """Result after cross-encoder reranking."""
    chunk_id: str
    parent_id: str
    text: str
    metadata: dict
    rerank_score: float


class CrossEncoderReranker:
    """
    Reranks retrieval results using cross-encoder model.
    
    Cross-encoders jointly encode query and document together for
    accurate relevance scoring. Used to filter top 20 candidates
    down to top 3-5 most relevant chunks.
    
    Default: mixedbread-ai/mxbai-rerank-xsmall-v1 (fast and accurate)
    """
    
    def __init__(self, model_name: str = "mixedbread-ai/mxbai-rerank-xsmall-v1"):
        """
        Initialize cross-encoder model.
        
        Args:
            model_name: Hugging Face cross-encoder model name.
        """
        self.model = CrossEncoder(model_name)
        logger.info(f"CrossEncoderReranker loaded: {model_name}")
    
    def rerank(self, query: str, candidates: List, top_k: int = 5) -> List[RerankResult]:
        """
        Rerank candidates and return top-K.
        
        Args:
            query: Search query.
            candidates: List of retrieval results with .text, .chunk_id, .parent_id, .metadata.
            top_k: Number of top results to return.
        
        Returns:
            Top-K reranked results.
        """
        if not candidates:
            return []
        
        pairs = [[query, c.text] for c in candidates]
        scores = self.model.predict(pairs)
        
        scored = [
            RerankResult(
                chunk_id=c.chunk_id,
                parent_id=c.parent_id,
                text=c.text,
                metadata=c.metadata,
                rerank_score=float(scores[i])
            )
            for i, c in enumerate(candidates)
        ]
        
        scored.sort(key=lambda x: x.rerank_score, reverse=True)
        return scored[:top_k]
