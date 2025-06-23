import asyncio
import logging
from typing import Dict, Any, List

# Import the WebSearch class
from researcher.web_search.web_search import WebSearch

logging.basicConfig(level=logging.INFO)

class ResearchEngine:
    def __init__(self, research_depth: str, research_category: str, websocket, report_format: str):
        self.research_depth = research_depth
        self.research_category = research_category
        self.websocket = websocket # Assuming websocket is an object with a send_json method
        self.report_format = report_format

    async def web_search(self, query: str) -> List[Dict[str, Any]]:
        """Performs a standard web search with limited depth."""
        logging.info(f"Performing standard web search for: {query}")
        try:
            # Small search: limited web results, no paper search
            web_search_instance = WebSearch(
                query=query,
                max_results=5, # Small number of web results
                arxiv_research_paper_queries=[], # No arxiv papers
                arxiv_max_results=0,
                medbio_research_paper_queries=[], # No medrxiv/biorxiv papers
                medbio_max_results=0
            )
            results = await web_search_instance.initiate_research()
            logging.info(f"Standard web search complete for: {query}")
            return results
        except Exception as e:
            logging.error(f"Error during standard web search for '{query}': {e}")
            # Depending on requirements, you might want to re-raise or return an empty list/error indicator
            return []

    async def deep_search(self, query: str) -> List[Dict[str, Any]]:
        """Performs a deeper research search including some papers."""
        logging.info(f"Performing deep search for: {query}")
        try:
            # Deep search: more web results, some paper search
            deep_search_instance = WebSearch(
                query=query,
                max_results=15, # Moderate number of web results
                arxiv_research_paper_queries=[query], # Search arxiv with the main query
                arxiv_max_results=5, # Some arxiv papers
                medbio_research_paper_queries=[query], # Search medrxiv/biorxiv with the main query
                medbio_max_results=5 # Some medrxiv/biorxiv papers
            )
            results = await deep_search_instance.initiate_research()
            logging.info(f"Deep search complete for: {query}")
            return results
        except Exception as e:
            logging.error(f"Error during deep search for '{query}': {e}")
            return []

    async def extreme_search(self, query: str) -> List[Dict[str, Any]]:
        """Performs an intense research search including more papers."""
        logging.info(f"Performing extreme search for: {query}")
        try:
            # Extreme search: many web results, more intense paper search
            extreme_search_instance = WebSearch(
                query=query,
                max_results=25, # Larger number of web results
                arxiv_research_paper_queries=[query], # Search arxiv with the main query
                arxiv_max_results=10, # More arxiv papers
                medbio_research_paper_queries=[query], # Search medrxiv/biorxiv with the main query
                medbio_max_results=10 # More medrxiv/biorxiv papers
            )
            results = await extreme_search_instance.initiate_research()
            logging.info(f"Extreme search complete for: {query}")
            return results
        except Exception as e:
            logging.error(f"Error during extreme search for '{query}': {e}")
            return []

    async def SearchEngine(self, query: str) -> List[Dict[str, Any]]:
        """
        Routes the research query to the appropriate search method based on research_depth.
        """
        logging.info(f"Routing search for query: '{query}' with depth: '{self.research_depth}'")
        try:
            if self.research_depth == "web":
                return await self.web_search(query)
            elif self.research_depth == "deep":
                return await self.deep_search(query)
            elif self.research_depth == "extreme":
                return await self.extreme_search(query)
            else:
                logging.warning(f"Unknown research depth: '{self.research_depth}'. Defaulting to web search.")
                # Optionally raise an error or return an empty list for unknown depth
                return await self.web_search(query) # Default to web search for safety
        except Exception as e:
            logging.error(f"An error occurred in SearchEngine for query '{query}': {e}")
            return []


# if __name__ == '__main__':
#     # Example Usage (requires an async context)
#     async def main():
#         # Dummy websocket object for demonstration
#         class DummyWebsocket:
#             async def send_json(self, data):
#                 # In a real application, this would send data over a websocket connection
#                 # For this example, we'll just print
#                 # print(f"Sending via websocket: {data}")
#                 pass # Suppress print for cleaner output during search

#         dummy_ws = DummyWebsocket()

#         # Test different research depths
#         print("\n--- Testing Web Search ---")
#         engine_web = ResearchEngine(
#             research_depth="web",
#             research_category="technology",
#             websocket=dummy_ws,
#             report_format="markdown"
#         )
#         web_results = await engine_web.SearchEngine("latest AI trends")
#         print(f"Web Search Results Count: {len(web_results)}")
#         # for i, res in enumerate(web_results[:3]): # Print first 3 results
#         #     print(f"Result {i+1}: URL={res.get('url', 'N/A')}, Content Snippet={res.get('content', 'N/A')[:200]}...")


#         print("\n--- Testing Deep Search ---")
#         engine_deep = ResearchEngine(
#             research_depth="deep",
#             research_category="science",
#             websocket=dummy_ws,
#             report_format="markdown"
#         )
#         deep_results = await engine_deep.SearchEngine("quantum computing breakthroughs")
#         print(f"Deep Search Results Count: {len(deep_results)}")
#         # for i, res in enumerate(deep_results[:3]): # Print first 3 results
#         #     print(f"Result {i+1}: URL={res.get('url', 'N/A')}, Content Snippet={res.get('content', 'N/A')[:200]}...")


#         print("\n--- Testing Extreme Search ---")
#         engine_extreme = ResearchEngine(
#             research_depth="extreme",
#             research_category="biotechnology",
#             websocket=dummy_ws,
#             report_format="markdown"
#         )
#         extreme_results = await engine_extreme.SearchEngine("future of biotechnology")
#         print(f"Extreme Search Results Count: {len(extreme_results)}")
#         # for i, res in enumerate(extreme_results[:3]): # Print first 3 results
#         #     print(f"Result {i+1}: URL={res.get('url', 'N/A')}, Content Snippet={res.get('content', 'N/A')[:200]}...")

#         print("\n--- Testing Unknown Depth (should default to web) ---")
#         engine_unknown = ResearchEngine(
#             research_depth="unknown",
#             research_category="general",
#             websocket=dummy_ws,
#             report_format="markdown"
#         )
#         unknown_results = await engine_unknown.SearchEngine("random topic")
#         print(f"Unknown Depth Search Results Count: {len(unknown_results)}")


#     # Run