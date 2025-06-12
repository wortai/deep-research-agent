from langchain_openai import OpenAIEmbeddings
# Best Practice: Use the new, dedicated package for Qdrant
from langchain_qdrant import QdrantVectorStore ,RetrievalMode
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance # ⬅️ Correct import
import os 
from dotenv import load_dotenv
load_dotenv()



class QdrantService:
  
    # A service class that sets up and provides a connection to a 
    # Qdrant vector store.
    
    def __init__(self, collection_name="my_docs"):
        self.collection_name = collection_name
        self.vector_size = 1536

        self.OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY")
        self.QDRANT_URL=os.environ.get("QDRANT_URL")
        self.QDRANT_API_KEY=os.environ.get("QDRANT_API_KEY")
        print(f"API Keys {self.OPENAI_API_KEY}  {self.QDRANT_API_KEY}  {self.QDRANT_URL}")
        # Initialize the Qdrant client
        self.client = QdrantClient(
            url=self.QDRANT_URL,
            api_key=self.QDRANT_API_KEY,
        )

        # Initialize collection (create if not exists)
        self._initialize_collection()

        # Initialize the embedding model
        embedding_model = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=self.OPENAI_API_KEY
        )

        # Initialize LangChain's Qdrant vector store
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=embedding_model,  # 
            retrieval_mode=RetrievalMode.DENSE,
        )
        print(" QdrantService initialized and vector_store is ready.")

    def _initialize_collection(self):
        try:
                    # This is a more direct way to check for a collection
            self.client.get_collection(collection_name=self.collection_name)
            print(f"ℹ️ Collection '{self.collection_name}' already exists.")
        except Exception:
            # If get_collection fails, it likely doesn't exist.
            print(f"Collection '{self.collection_name}' not found. Creating...")
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                )
            )
            print(f"✅ Collection '{self.collection_name}' created.")

if __name__ == "__main__":
    data = QdrantService("web-documents")
    