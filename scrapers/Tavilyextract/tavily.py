import os
import logging
from tavily import TavilyClient, AsyncTavilyClient
# No need for BeautifulSoup if not using it for HTML parsing
import asyncio 
from typing import Any, List, Dict, Tuple # Corrected import for Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Tavily:


    # instance of class can be customized as per query needs 
    #   only required to provide query :  temp = Tavily(query: required )
    def __init__(
        self,
        query: str,
        queries :list[str] = None , # Default to None, good practice
        depth: bool = False, # advance or basic 
        topic: str = "general", # general for broader , news for more accurate and finance for more finace related
        max_result: int = 5, # how many results you want for each query 
        include_images: bool = False,  # if you want images with your query
        include_raw_content: bool = False # Added type hint consistency
    ):
        self.query = query
        self.depth = "basic" if not depth else "advanced"
        self.topic = topic
        self.max_result = max_result
        self.include_images = include_images
        self.queries = queries
        self.include_raw_content = include_raw_content
        
        self.tavily_client = TavilyClient(api_key=self.get_api_key())
        self.async_tavily_client = AsyncTavilyClient(api_key=self.get_api_key())

    def get_api_key(self):
        try:
            return os.environ["TAVILY_API_KEY"]
        except KeyError:
            logging.error("Tavily API key not found.") # Improved error message
            raise Exception("Tavily API key not found. Please set the TAVILY_API_KEY environment variable.")


# baisc search for little internet knowledge will use by coding agents and other by calling here 
    async def basic_search(self) -> List[Dict[str, str]]:
       
        try:
            response = await self.async_tavily_client.search(
                query=self.query,
                search_depth=self.depth,
                topic=self.topic,
                max_results=self.max_result
            )
            extract = []
            if response and "results" in response: 
                for result in response["results"]:
                    title = result.get("url") 
                    content = result.get("content")
                    if title and content: 
                        extract.append({"url": title, "content": content})
            return extract
        except Exception as e:
            logging.error(f"Error in basic search: {str(e)}")
            return []

# processing more accurate in depth 
    async def advance_search(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
       
        try:
            response = await self.async_tavily_client.search(
                query=self.query,
                search_depth=self.depth,
                topic=self.topic,
                max_results=self.max_result,
                include_images=self.include_images,
                include_raw_content=self.include_raw_content, # Use instance's attribute
            )
            
            images = response.get("images", [])
            results = response.get("results", [])
            
            # taking out images and results seprately and returning them 
            return images, results 
        except Exception as e:
            logging.error(f"Error Occurred in advance_search: {e}")
            return [], [] 

    async def resolve_query(self) -> Any:
        if self.depth == "advanced":
            return await self.advance_search()
        else:
            return await self.basic_search()


# for tackling multiple queries and reoslving them in parallely
    async def multiple_advance_queries(self) -> List[Dict[str, Any]]:
        tasks = []
        if not self.queries: # Safety check
            logging.warning("No queries provided to multiple_advance_queries. Returning empty list.")
            return []

      
        for query_item in self.queries: 
           
            tasks.append(
                self.async_tavily_client.search( 
                    query=query_item, # The specific query for *this* task
                    search_depth=self.depth, 
                    topic=self.topic,
                    max_results=self.max_result,
                    include_images=self.include_images,
                    include_raw_content=self.include_raw_content,
                )
            )
            
        all_raw_responses = await asyncio.gather(*tasks, return_exceptions=True)

        structured_responses = [] 
        for i, response_item in enumerate(all_raw_responses):
            current_query = self.queries[i] 
            
            if isinstance(response_item, Exception):
                logging.error(f"Error for query '{current_query}': {response_item}")
                continue
            else:
              
                structured_responses.append({
                    "query": response_item.get("query"), 
                    "results": response_item.get("results", []) 
                })
        return structured_responses