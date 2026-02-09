"""
Sparse Embedding using FastEmbed for Qdrant.

Uses Qdrant's fastembed library for efficient sparse vector generation
with SPLADE or BM25 models.
"""

import logging
from typing import List, Dict, Any
from fastembed import SparseTextEmbedding

logger = logging.getLogger(__name__)


class SparseEmbedding:
    """
    Generates sparse embeddings using FastEmbed's SPLADE model.
    
    FastEmbed provides pre-trained sparse embedding models optimized
    for Qdrant's sparse vector format (indices, values).
    """
    
    DEFAULT_MODEL = "Qdrant/bm25"
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        """
        Initialize sparse embedding model.
        
        Args:
            model_name: FastEmbed sparse model name (default: Qdrant/bm25).
        """
        self.model = SparseTextEmbedding(model_name=model_name)
        logger.info(f"SparseEmbedding initialized with model: {model_name}")
    
    def embed_documents(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Generate sparse embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed.
        
        Returns:
            List of sparse vector dicts with 'indices' and 'values'.
        """
        embeddings = list(self.model.embed(texts))
        return [
            {"indices": emb.indices.tolist(), "values": emb.values.tolist()}
            for emb in embeddings
        ]
    
    def embed_query(self, query: str) -> Dict[str, Any]:
        """
        Generate sparse embedding for a query.
        
        Args:
            query: Query text to embed.
        
        Returns:
            Sparse vector dict with 'indices' and 'values'.
        """
        embeddings = list(self.model.query_embed(query))
        emb = embeddings[0]
        return {"indices": emb.indices.tolist(), "values": emb.values.tolist()}
