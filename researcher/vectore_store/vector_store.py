# In vectore_store/vector_store.py

from typing import List, Dict, Tuple
from langchain.docstore.document import Document
from langchain.vectorstores.base import VectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import logging
from .qdrant_db import QdrantService

logger = logging.getLogger(__name__)

class VectorStoreManager:
   
    def __init__(self, vector_store: VectorStore):
        # The vector_store instance passed here should already be initialized
        # with an embedding model.
        self.vector_store = vector_store
        
        # Extract embedding model for batch operations
        self.embedding_model = getattr(vector_store, 'embeddings', None)
        if self.embedding_model is None:
            logger.warning("No embedding model found in vector store - batch operations may not work")

    def load(self, documents: List[Dict[str, str]]):
        """Load documents using the original method."""
        langchain_documents = self._create_langchain_documents(documents)
        splitted_documents = self._split_documents(langchain_documents)
        self.vector_store.add_documents(splitted_documents)
        print("Documents have been successfully loaded and indexed.")
    
    def load_batch_optimized(self, documents: List[Dict[str, str]], batch_size: int = 100):
        """Load documents with optimized batch embedding to minimize API calls."""
        try:
            if not documents:
                logger.warning("No documents provided for batch loading")
                return False
            
            logger.info(f"Starting batch optimized loading for {len(documents)} documents")
            
            # Step 1: Prepare all documents and split them
            langchain_documents = self._create_langchain_documents(documents)
            splitted_documents = self._split_documents(langchain_documents)
            
            if not splitted_documents:
                logger.warning("No documents after splitting")
                return False
            
            logger.info(f"Total document chunks after splitting: {len(splitted_documents)}")
            
            # Step 2: Process in batches to respect API rate limits
            total_chunks = len(splitted_documents)
            successfully_processed = 0
            
            for i in range(0, total_chunks, batch_size):
                batch = splitted_documents[i:i+batch_size]
                batch_num = i // batch_size + 1
                total_batches = (total_chunks + batch_size - 1) // batch_size
                
                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)")
                
                try:
                    # Batch process this chunk
                    success = self._process_document_batch(batch)
                    if success:
                        successfully_processed += len(batch)
                        logger.info(f"Batch {batch_num} processed successfully")
                    else:
                        logger.error(f"Failed to process batch {batch_num}")
                        
                except Exception as e:
                    logger.error(f"Error processing batch {batch_num}: {e}")
                    continue
            
            logger.info(f"Batch loading completed: {successfully_processed}/{total_chunks} chunks processed")
            print(f"Documents have been successfully loaded and indexed ({successfully_processed} chunks).")
            
            return successfully_processed > 0
            
        except Exception as e:
            logger.error(f"Batch optimized loading failed: {e}")
            return False
    
    def _process_document_batch(self, documents: List[Document]) -> bool:
        """Process a batch of documents with optimized embedding."""
        try:
            if not self.embedding_model:
                # Fallback to original method if no embedding model available
                logger.warning("No embedding model available, using fallback method")
                self.vector_store.add_documents(documents)
                return True
            
            # Extract texts for batch embedding
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            # Qdrant will handle embeddings internally through its embedding model
            # Just pass texts and metadata
            logger.info(f"Adding {len(texts)} texts to vector store in batch")
            self.vector_store.add_texts(texts, metadatas=metadatas)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            return False

    def _create_langchain_documents(self, data: List[Dict[str, str]]) -> List[Document]:
        # Converts a list of dictionaries into LangChain's Document format.
        # Each dictionary should have 'raw_content' and 'url' keys.
        return [
        Document(
            page_content=item["content"],
            metadata={"source": item["url"]} if item.get("url") else {}
        )
        for item in data]
            


    def _split_documents(self, documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 100) -> List[Document]:
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True,
        )
        return text_splitter.split_documents(documents)

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        results = self.vector_store.similarity_search(query=query, k=k)
        return results
    
    def batch_similarity_search(self, queries: List[str], k: int = 4) -> Dict[str, List[Document]]:
        """
        Perform batch similarity search for multiple queries.
        This method can be optimized by vector stores that support batch embedding.
        
        Args:
            queries: List of search queries
            k: Number of results per query
            
        Returns:
            Dictionary mapping queries to their search results
        """
        results = {}
        
        # Note: Some vector stores support batch embeddings internally
        # For now, we process sequentially but the embedding model may batch internally
        for query in queries:
            results[query] = self.vector_store.similarity_search(query=query, k=k)
        
        return results
    
    def get_optimal_batch_size(self, total_documents: int, rate_limit_rpm: int = 500) -> int:
        """
        Calculate optimal batch size based on rate limits and document count.
        
        Args:
            total_documents: Total number of documents to process
            rate_limit_rpm: Rate limit in requests per minute
            
        Returns:
            Optimal batch size to respect rate limits
        """
        # Conservative approach: use 80% of rate limit
        safe_rpm = int(rate_limit_rpm * 0.8)
        
        # Calculate batch size to stay within rate limits
        if total_documents <= safe_rpm:
            return total_documents
        
        # For large document sets, use smaller batches
        if total_documents > 1000:
            return min(100, safe_rpm // 5)  # 5 API calls per minute max
        else:
            return min(50, safe_rpm // 10)  # 10 API calls per minute max
    

if __name__ == "__main__":
    vector = QdrantService("web-documents").vector_store
    vector_class= VectorStoreManager(vector)
    # documents = [
    # {
    #     "content": (
    #         "LangChain is a framework for building applications with language models. "
    #         "It enables chaining of LLM calls, retrieval from vector databases, and interaction with tools. "
    #         "LangChain supports both open-source and proprietary models."
    #     ),
    #     "url": "https://www.langchain.com"
    # },
    # {
    #     "content": (
    #         "Qdrant is a high-performance vector database for similarity search. "
    #         "It provides features such as filtering, payload support, and hybrid search. "
    #         "Qdrant is suitable for production-grade semantic search applications."
    #     ),
    #     "url": "https://qdrant.tech"
    # },
    # {
    #     "content": (
    #         "OpenAI provides cutting-edge models like GPT-4 and embedding APIs. "
    #         "The `text-embedding-3-small` model is optimized for cost and performance. "
    #         "OpenAI's tools are widely used in RAG, chatbots, and document understanding."
    #     ),
    #     "url": "https://platform.openai.com"
    # },
    # {
    #     "content": (
    #         "Vector search is a powerful technique used to find semantically similar documents. "
    #         "It uses high-dimensional embeddings of text to compute relevance using cosine similarity or other distance metrics."
    #     ),
    #     "url": "https://en.wikipedia.org/wiki/Vector_search"
    # },
    # {
    #     "content": (
    #         "Embeddings are numerical representations of text that capture semantic meaning. "
    #         "They are used in tasks like search, classification, clustering, and more. "
    #         "Popular models include OpenAI embeddings, BGE, and MiniLM."
    #     ),
    #     "url": "https://huggingface.co/docs/transformers/model_doc/all-MiniLM-L6-v2"
    # }
    # ]
    
    # vector_class.load(documents)
    documents=vector_class.similarity_search("what are the best embeddings")
    # print(data)
    for i, doc in enumerate(documents):

        print(f"--- Document {i+1} ---")

        # Accessing the page_content
        print("\nPage Content:")
        print(doc.page_content)

        # Accessing the entire metadata dictionary
        print("\nMetadata (Full Dictionary):")
        print(doc.metadata)

        # Accessing individual data inside metadata
        print("\nData Inside Metadata:")
        if 'source' in doc.metadata:
            print(f"  Source: {doc.metadata['source']}")
        if 'start_index' in doc.metadata:
            print(f"  Start Index: {doc.metadata['start_index']}")
        if '_id' in doc.metadata:
            print(f"  ID: {doc.metadata['_id']}")
        if '_collection_name' in doc.metadata:
            print(f"  Collection Name: {doc.metadata['_collection_name']}")
        # You can add more checks for other metadata keys if they might not always be present