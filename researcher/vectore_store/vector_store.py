# In src/vector_store_manager.py

from typing import List, Dict
from langchain.docstore.document import Document
from langchain.vectorstores.base import VectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .qdrant_db import QdrantService

class VectorStoreManager:
   
    def __init__(self, vector_store: VectorStore):
        # The vector_store instance passed here should already be initialized
        # with an embedding model.
        self.vector_store = vector_store

    def load(self, documents: List[Dict[str, str]]):
   
        langchain_documents = self._create_langchain_documents(documents)
        splitted_documents = self._split_documents(langchain_documents)
        self.vector_store.add_documents(splitted_documents)
        print("Documents have been successfully loaded and indexed.")

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





