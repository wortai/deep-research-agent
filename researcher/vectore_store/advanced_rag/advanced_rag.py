"""
Advanced RAG Orchestrator.

Main class orchestrating the complete advanced RAG pipeline:
ingestion, Qdrant native hybrid search with RRF, cross-encoder reranking, parent fetch.
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

from .redis_parent_store import RedisParentStore
from .hybrid_qdrant_db import HybridQdrantDatabase
from .hybrid_document_ingestion import HybridDocumentIngestion
from .hybrid_retriever import HybridRetriever
from .cross_encoder_reranker import CrossEncoderReranker, RerankResult

logger = logging.getLogger(__name__)


@dataclass
class RAGContext:
    """
    Final context returned by Advanced RAG pipeline.
    
    Attributes:
        parent_id: Parent document ID.
        content: Full parent document content.
        source: Source URL.
        title: Document title.
        matched_chunks: Chunks that matched the query.
        scores: Cross-encoder scores for matched chunks.
    """
    parent_id: str
    content: str
    source: str
    title: str
    matched_chunks: List[str]
    scores: List[float]


class AdvancedRAG:
    """
    Complete Advanced RAG pipeline using Qdrant native hybrid search.
    
    Ingestion Flow:
    1. Document → Redis (full parent with unique ID)
    2. Document → LangChain splitter → Child chunks with parent_id
    3. Chunks → OpenAI embeddings (dense) + FastEmbed BM25 (sparse)
    4. Chunks → Qdrant (hybrid collection with dense + sparse vectors)
    
    Retrieval Flow:
    1. Query → Qdrant hybrid search with RRF fusion → Top 20 candidates
    2. Candidates → Cross-encoder reranking → Top 3-5 chunks
    3. Top chunks → Extract parent_ids → Redis → Full parent documents
    4. Return parent documents as complete context
    """
    
    def __init__(
        self,
        collection_name: str = "advanced_rag_docs",
        redis_url: Optional[str] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        embedding_model: str = "text-embedding-3-small",
        reranker_model: str = "mixedbread-ai/mxbai-rerank-xsmall-v1"
    ):
        """
        Initialize Advanced RAG system.
        
        Args:
            collection_name: Qdrant collection name.
            redis_url: Redis connection URL.
            chunk_size: Characters per chunk.
            chunk_overlap: Overlap between chunks.
            embedding_model: OpenAI embedding model.
            reranker_model: Cross-encoder model for reranking.
        """
        self.parent_store = RedisParentStore(redis_url=redis_url)
        self.qdrant_db = HybridQdrantDatabase(collection_name=collection_name)
        
        self.ingestion = HybridDocumentIngestion(
            parent_store=self.parent_store,
            qdrant_db=self.qdrant_db,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            embedding_model=embedding_model
        )
        
        self.retriever = HybridRetriever(
            qdrant_db=self.qdrant_db,
            embedding_model=embedding_model
        )
        
        self.reranker = CrossEncoderReranker(model_name=reranker_model)
        logger.info(f"AdvancedRAG initialized: {collection_name}")
    
    def ingest_documents(self, documents: List[Dict[str, str]]) -> int:
        """
        Ingest documents into RAG system.
        
        Each document: {content: str, url: Optional[str], title: Optional[str]}
        
        Returns:
            Number of chunks indexed.
        """
        return self.ingestion.ingest(documents)
    
    def retrieve_context(
        self,
        query: str,
        top_k_retrieval: int = 20,
        top_k_rerank: int = 5
    ) -> List[RAGContext]:
        """
        Retrieve parent documents for query.
        
        Pipeline:
        1. Qdrant hybrid search with RRF → top_k_retrieval candidates
        2. Cross-encoder rerank → top_k_rerank chunks
        3. Fetch parent documents from Redis
        
        Args:
            query: Search query.
            top_k_retrieval: Candidates from hybrid search (default: 20).
            top_k_rerank: Final results after reranking (default: 5).
        
        Returns:
            List of RAGContext with full parent documents.
        """
        candidates = self.retriever.retrieve(query=query, top_k=top_k_retrieval)
        
        if not candidates:
            return []
        
        reranked = self.reranker.rerank(query, candidates, top_k=top_k_rerank)
        
        return self._fetch_parents(reranked)
    
    def _fetch_parents(self, reranked: List[RerankResult]) -> List[RAGContext]:
        """Fetch parent documents for reranked chunks."""
        parent_chunks: Dict[str, List[RerankResult]] = {}
        for r in reranked:
            parent_chunks.setdefault(r.parent_id, []).append(r)
        
        parent_docs = self.parent_store.get_many(list(parent_chunks.keys()))
        doc_map = {d["parent_id"]: d for d in parent_docs}
        
        contexts = []
        for parent_id, chunks in parent_chunks.items():
            if parent_id not in doc_map:
                continue
            
            doc = doc_map[parent_id]
            contexts.append(RAGContext(
                parent_id=parent_id,
                content=doc["content"],
                source=doc.get("metadata", {}).get("source", ""),
                title=doc.get("metadata", {}).get("title", ""),
                matched_chunks=[c.text for c in chunks],
                scores=[c.rerank_score for c in chunks]
            ))
        
        contexts.sort(key=lambda x: max(x.scores) if x.scores else 0, reverse=True)
        return contexts


# =============================================================================
# TEST DATA - Comprehensive documents for testing ingestion and retrieval
# 20 documents across various fields with substantial content
# =============================================================================




def test_advanced_rag():
    """Test the Advanced RAG pipeline with sample data."""
    print("=" * 60)
    print("ADVANCED RAG SYSTEM TEST")
    print("=" * 60)
    
    # Initialize RAG system
    print("\n[1] Initializing AdvancedRAG...")
    rag = AdvancedRAG(
        collection_name="test_advanced_rag",
        chunk_size=200,
        chunk_overlap=50
    )
    print("    ✓ AdvancedRAG initialized")
    
    # Ingest test documents
    print(f"\n[2] Ingesting {len(TEST_DOCUMENTS)} documents...")
    chunk_count = rag.ingest_documents(TEST_DOCUMENTS)
    print(f"    ✓ Ingested {chunk_count} chunks from {len(TEST_DOCUMENTS)} documents")
    
    # Test retrieval with each query
    print("\n[3] Testing retrieval queries...")
    print("-" * 60)
    
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n  Query {i}: \"{query}\"")
        
        contexts = rag.retrieve_context(
            query=query,
            top_k_retrieval=10,
            top_k_rerank=3
        )
        
        if contexts:
            print(f"    Found {len(contexts)} parent document(s):")
            for ctx in contexts:
                print(f"      - {ctx.title}")
                print(f"        Score: {max(ctx.scores):.4f}")
                print(f"        Matched chunks: {len(ctx.matched_chunks)}")
                print(f"        Preview: {ctx.content[:100].strip()}...")
        else:
            print("    No results found")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_advanced_rag()

