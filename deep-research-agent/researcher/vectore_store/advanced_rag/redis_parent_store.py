"""
Redis Parent Document Store for Advanced RAG.

Stores full parent documents in Redis for context expansion after retrieval.
"""

import json
import uuid
import logging
from typing import List, Dict, Optional
import redis
from dotenv import load_dotenv
import os

load_dotenv()
logger = logging.getLogger(__name__)


class RedisParentStore:
    """
    Stores and retrieves parent documents from Redis.
    
    Parent documents are stored with unique IDs. Child chunks in Qdrant
    reference these IDs to enable full document retrieval after reranking.
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        prefix: str = "parent_doc:"
    ):
        """
        Initialize Redis connection.
        
        Uses environment variables for connection:
        - REDIS_HOST: Redis server host
        - REDIS_PORT: Redis server port
        - REDIS_USERNAME: Username (default: "default")
        - REDIS_PASSWORD: Password for authentication
        
        Args:
            redis_url: Full Redis URL (optional, for backwards compatibility).
            host: Redis host (overrides env).
            port: Redis port (overrides env).
            prefix: Key prefix for parent documents.
        """
        self.prefix = prefix
        
        # Get connection details from env
        redis_host = host or os.environ.get("REDIS_HOST", "localhost")
        redis_port = port or int(os.environ.get("REDIS_PORT", "6379"))
        username = os.environ.get("REDIS_USERNAME", "default")
        password = os.environ.get("REDIS_PASSWORD") or os.environ.get("REDIS_API_KEY")
        
        # Use Redis Cloud recommended connection format
        self.client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            username=username,
            password=password
        )
        
        self.client.ping()
        logger.info(f"RedisParentStore connected to {redis_host}:{redis_port}")
    
    def generate_id(self) -> str:
        """Generate unique parent ID."""
        return str(uuid.uuid4())
    
    def store(self, parent_id: str, content: str, metadata: Optional[Dict] = None) -> str:
        """
        Store parent document.
        
        Args:
            parent_id: Unique document ID.
            content: Full document text.
            metadata: Optional metadata (source, title, etc.).
        
        Returns:
            The parent_id.
        """
        doc = {"content": content, "metadata": metadata or {}, "parent_id": parent_id}
        self.client.set(f"{self.prefix}{parent_id}", json.dumps(doc))
        return parent_id
    
    def get(self, parent_id: str) -> Optional[Dict]:
        """Retrieve single parent document."""
        data = self.client.get(f"{self.prefix}{parent_id}")
        return json.loads(data) if data else None
    
    def get_many(self, parent_ids: List[str]) -> List[Dict]:
        """Retrieve multiple parent documents."""
        if not parent_ids:
            return []
        
        keys = [f"{self.prefix}{pid}" for pid in parent_ids]
        results = self.client.mget(keys)
        return [json.loads(r) for r in results if r]
    
    def delete(self, parent_id: str) -> bool:
        """Delete parent document."""
        return self.client.delete(f"{self.prefix}{parent_id}") > 0
