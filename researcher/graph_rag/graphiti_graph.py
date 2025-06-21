import os
import json
import logging
from datetime import datetime, timezone

from graphiti_core import Graphiti
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.bge_reranker_client import BGERerankerClient

# Import search configuration recipes as needed
from graphiti_core.search.search_config_recipes import (
    COMBINED_HYBRID_SEARCH_RRF,
    COMBINED_HYBRID_SEARCH_CROSS_ENCODER,
    NODE_HYBRID_SEARCH_CROSS_ENCODER,
    EDGE_HYBRID_SEARCH_CROSS_ENCODER,
    EDGE_HYBRID_SEARCH_RRF,
    NODE_HYBRID_SEARCH_RRF
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraphRAG:
    """
    A production-level Graph RAG (Retrieval-Augmented Generation) class using the Graphiti framework.
    This class initializes Graphiti with Gemini clients and provides methods to update data and perform searches.
    """

    def __init__(self,
                 neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_user: str = "neo4j",
                 neo4j_password: str = "password"):
        """
        Initialize the GraphRAG instance by reading environment variables and creating
        a Graphiti instance with proper Gemini clients.
        """
        # Load Google API key from environment variables
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            logger.error("GOOGLE_API_KEY environment variable is not set.")
            raise ValueError("GOOGLE_API_KEY environment variable must be set")

        # Log a snippet of the API key (avoid logging the full value)
        logger.info(f"Using Google API Key (first few chars): {self.api_key[:5]}...")

        # Initialize Graphiti with the Gemini components
        try:
            # IMPORTANT: Use empty string for password if NEO4J_AUTH=none
            self.graphiti = Graphiti(
                neo4j_uri,
                neo4j_user,
                neo4j_password,
                llm_client=GeminiClient(
                    config=LLMConfig(
                        api_key=self.api_key,
                        model="gemini-1.5-flash"  # Update this model as needed
                    )
                ),
                embedder=GeminiEmbedder(
                    config=GeminiEmbedderConfig(
                        api_key=self.api_key,
                        embedding_model="embedding-001"  # Update embedding model if necessary
                    )
                ),
                cross_encoder=BGERerankerClient()
            )
            logger.info("Graphiti initialized successfully with Gemini clients.")
        except Exception as e:
            logger.exception(f"Graphiti initialization failed: {e}")
            raise e

    async def connect(self):
        """
        Build indices and apply constraints on the Neo4j database connection.
        """
        try:
            logger.info("Building indices and constraints...")
            await self.graphiti.build_indices_and_constraints()
            logger.info("Indices and constraints built successfully.")
        except Exception as e:
            logger.exception(f"Failed to build indices and constraints: {e}")
            raise e

    async def add_episode(self,
                          name: str,
                          content: str,
                          source,
                          description: str,
                          reference_time: datetime = None):
        """
        Add a new episode to the graph. If reference_time is not provided, use the current UTC time.
        """
        if reference_time is None:
            reference_time = datetime.now(timezone.utc)

        try:
            # If the content is not a string, assume it is JSON serializable.
            episode_body = content if isinstance(content, str) else json.dumps(content)
            await self.graphiti.add_episode(
                name=name,
                episode_body=episode_body,
                source=source,
                source_description=description,
                reference_time=reference_time,
            )
            logger.info(f"Added episode: {name} ({source})")
        except Exception as e:
            logger.exception(f"Failed to add episode '{name}': {e}")
            raise e

    async def update_episode(self, episode_uuid: str, new_content: str):
        """
        Update an existing episode in the graph.
        (Assumes that Graphiti has an update_episode method; adjust if the API is different.)
        """
        try:
            # Note: Replace this with the correct API to update an episode if available
            await self.graphiti.update_episode(episode_uuid, new_content)
            logger.info(f"Updated episode with UUID: {episode_uuid}")
        except Exception as e:
            logger.exception(f"Failed to update episode '{episode_uuid}': {e}")
            raise e

    async def search(self, query: str, search_config) -> any:
        """
        Perform a search using a provided search configuration.
        :param query: The search query.
        :param search_config: The search configuration (e.g., NODE_HYBRID_SEARCH_RRF).
        :return: Search results.
        """
        try:
            logger.info(f"Performing search for query: {query}")
            results = await self.graphiti._search(query=query, config=search_config)
            logger.info("Search completed successfully.")
            return results
        except Exception as e:
            logger.exception(f"Search failed for query '{query}': {e}")
            raise e

    async def search_nodes(self, query: str, limit: int = 5):
        """
        Perform a node-based search using a hybrid search configuration.
        """
        # Create a copy of the configuration to adjust the limit.
        node_search_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
        node_search_config.limit = limit
        return await self.search(query, node_search_config)

    async def search_edges(self, query: str, limit: int = 5):
        """
        Perform an edge-based search using a hybrid search configuration.
        """
        edge_search_config = EDGE_HYBRID_SEARCH_CROSS_ENCODER.model_copy(deep=True)
        edge_search_config.limit = limit
        return await self.search(query, edge_search_config)

    async def combined_search(self, query: str, config_variant: str = 'RRF', limit: int = 5):
        """
        Perform a combined hybrid search. Choose between 'RRF' and 'CROSS_ENCODER' variants.
        """
        if config_variant.upper() == 'RRF':
            combined_config = COMBINED_HYBRID_SEARCH_RRF.model_copy(deep=True)
        elif config_variant.upper() == 'CROSS_ENCODER':
            combined_config = COMBINED_HYBRID_SEARCH_CROSS_ENCODER.model_copy(deep=True)
        else:
            raise ValueError("config_variant must be either 'RRF' or 'CROSS_ENCODER'")
        combined_config.limit = limit
        return await self.search(query, combined_config)

    def get_config_info(self, config) -> str:
        """
        Return a JSON string representation of the configuration.
        """
        try:
            info = config.model_dump_json(indent=2)
            return info
        except Exception as e:
            logger.warning(f"Failed to dump config info: {e}")
            return ""

    async def print_search_results(self, results: any):
        """
        Utility method to print search results in a formatted way.
        """
        try:
            # Assume 'results' can contain nodes and/or edges
            if hasattr(results, 'nodes'):
                for node in results.nodes:
                    logger.info(f"Node Name: {node.name}")
                    logger.info(f"Summary: {node.summary}")
            if hasattr(results, 'edges'):
                for edge in results.edges:
                    logger.info("Edge:")
                    logger.info(f"  Source: {edge.source_node_uuid}")
                    logger.info(f"  Fact: {edge.fact}")
                    logger.info(f"  Target: {edge.target_node_uuid}")
        except Exception as e:
            logger.exception(f"Failed to print search results: {e}")



