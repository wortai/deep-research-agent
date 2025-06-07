import os
import logging
import asyncio
from typing import Any, List, Dict, Tuple
from dotenv import load_dotenv
from tavily import TavilyClient, AsyncTavilyClient

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Tavily:

    def __init__(
        self,
        query: str = None,
        queries: List[str] = None,
        depth: bool = False,
        topic: str = "general",
        max_result: int = 5,
        include_images: bool = False,
        include_raw_content: bool = False
    ):
        self.query = query
        self.depth = "basic" if not depth else "advanced"
        self.topic = topic
        self.max_result = max_result
        self.include_images = include_images
        self.queries = queries if queries is not None else []
        self.include_raw_content = include_raw_content

        self.tavily_client = TavilyClient(api_key=self.get_api_key())
        self.async_tavily_client = AsyncTavilyClient(api_key=self.get_api_key())
        self.semaphore = asyncio.Semaphore(5) # Initialize semaphore for 5 concurrent tasks

    def get_api_key(self):
        try:
            api_key = os.environ.get("TAVILY_API_KEY")
            if not api_key:
                raise ValueError("TAVILY_API_KEY environment variable not set.")
            return api_key
        except ValueError as e:
            logging.error(f"Configuration error: {e}")
            raise

    async def basic_search(self) -> List[Dict[str, str]]:
        if not self.query:
            logging.error("Query is required for basic_search.")
            return []
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
            logging.error(f"Error in basic search for query '{self.query}': {str(e)}")
            return []

    async def advance_search(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        if not self.query:
            logging.error("Query is required for advance_search.")
            return [], []
        try:
            response = await self.async_tavily_client.search(
                query=self.query,
                search_depth=self.depth,
                topic=self.topic,
                max_results=self.max_result,
                include_images=self.include_images,
                include_raw_content=self.include_raw_content,
            )

            images = response.get("images", [])
            results = response.get("results", [])

            return images, results
        except Exception as e:
            logging.error(f"Error Occurred in advance_search for query '{self.query}': {e}")
            return [], []

    async def resolve_query(self) -> Any:
        if self.depth == "advanced":
            return await self.advance_search()
        else:
            return await self.basic_search()

    async def multiple_advance_queries(self) -> List[Dict[str, Any]]:
        if not self.queries:
            logging.warning("No queries provided to multiple_advance_queries. Returning empty list.")
            return []

        async def _single_query_task(query_item: str) -> Dict[str, Any]:
            async with self.semaphore:
                try:
                    response = await self.async_tavily_client.search(
                        query=query_item,
                        search_depth=self.depth,
                        topic=self.topic,
                        max_results=self.max_result,
                        include_images=self.include_images,
                        include_raw_content=self.include_raw_content,
                    )
                    return {"query": response.get("query"), "results": response.get("results", [])}
                except Exception as e:
                    logging.error(f"Error for query '{query_item}': {e}")
                    return {"query": query_item, "results": [], "error": str(e)}

        tasks = [_single_query_task(query_item) for query_item in self.queries]
        return await asyncio.gather(*tasks)

    async def extract_content(self, url: str) -> Dict[str, str]:
        async with self.semaphore:
            try:
                extracted_data = await self.async_tavily_client.extract(url, extract_depth="advanced", format="markdown")

                # Handle API-level errors first (e.g., rate limits, invalid URL)
                if extracted_data and "detail" in extracted_data:
                    error_message = extracted_data["detail"].get("error", "Unknown API error")
                    logging.error(f"Tavily API error for URL '{url}': {error_message}")
                    return {"url": url, "content": None, "error": f"API error: {error_message}"}

           
                # Extract content from the first result
                first_result = extracted_data["results"][0]
                extracted_url = first_result.get("url")
                content_text = first_result.get("raw_content")

                # Fallback to 'content' if 'raw_content' is not present
                if content_text is None:
                    content_text = "No content find Skip this url data"

                return {"url": extracted_url , "content": content_text}

            except Exception as e:
                # Catch any other unexpected exceptions like  network issues, invalid JSON response from client library etc.
                logging.error(f"An unexpected error occurred during content extraction for URL '{url}': {e}")
                return {"url": url, "content": None, "error": f"Unexpected error: {str(e)}"}




    async def multiple_extract_content(self, urls: List[str]) -> List[Dict[str, Any]]:
        if not urls:
            logging.warning("No URLs provided to multiple_extract_content. Returning empty list.")
            return []

        tasks = [self.extract_content(url) for url in urls]
        responses = await asyncio.gather(*tasks)

        # Filter out successful extractions and log errors for failed ones
        structured_responses = []
        for res in responses:
            if res.get("content") is not None:
                structured_responses.append({"url": res["url"], "content": res["content"]})
            else:
                logging.error(f"Failed to extract content for URL: {res.get('url')} - Error: {res.get('error', 'Unknown error')}")
        return structured_responses



async def main():
    # Test Cases

    # # Test 1: Basic Search
    # logging.info("\n--- Test Case 1: Basic Search ---")
    # tavily_basic = Tavily(query="latest news on AI", depth=False, max_result=2)
    # basic_results = await tavily_basic.resolve_query()
    # for res in basic_results:
    #     logging.info(f"URL: {res.get('url')}, Content snippet: {res.get('content')[:100] if res.get('content') else 'N/A'}...")

    # # Test 2: Advanced Search with Images
    # logging.info("\n--- Test Case 2: Advanced Search with Images ---")
    # tavily_advanced = Tavily(query="Mars Rover images", depth=True, max_result=1, include_images=True)
    # images, results = await tavily_advanced.resolve_query()
    # logging.info(f"Advanced Search Results (First URL): {results[0].get('url') if results else 'N/A'}")
    # if images:
    #     logging.info(f"First Image URL: {images[0].get('src')}")

    # # Test 3: Multiple Advanced Queries
    # logging.info("\n--- Test Case 3: Multiple Advanced Queries ---")
    # queries_list = ["current price of gold", "weather in New York City", "upcoming tech conferences 2025"]
    # tavily_multi_query = Tavily(queries=queries_list, depth=True, max_result=1)
    # multi_query_results = await tavily_multi_query.multiple_advance_queries()
    # for res in multi_query_results:
    #     logging.info(f"Query: {res.get('query')}")
    #     if res.get("results"):
    #         logging.info(f"  First result URL: {res['results'][0].get('url')}")
    #     else:
    #         logging.info("  No results found or an error occurred.")

    # Test 4: Single URL Content Extraction (needs a valid URL)
    # logging.info("\n--- Test Case 4: Single URL Content Extraction ---")
    # # You'll need to replace this with an actual URL that Tavily can extract.
    # # A good example would be a news article URL.
    # sample_url = "https://towardsdatascience.com/advanced-techniques-for-fine-tuning-transformers-82e4e61e16e/"
    # tavily_extract = Tavily(query="dummy") # query is not used here, but needed for init for client setup
    # data = await tavily_extract.extract_content(sample_url)
    # if data:
    #    print(data.get('url'))
    #    print(data.get('content'))
    # else:
    #     logging.info(f"Failed to extract content from {extracted_content.get('url') if extracted_content.get('url') else sample_url}: {extracted_content.get('error', 'No content and no error specified')}")


    # Test 5: Multiple URL Content Extraction (needs valid URLs)
    logging.info("\n--- Test Case 5: Multiple URL Content Extraction ---")
    # Replace these with actual URLs for testing
    sample_urls = [
        "https://www.reddit.com/r/Piracy/comments/155vjyr/how_do_i_pirate_articles_on_medium/",
        "https://abcnews.go.com/Politics/day-after-blistering-exchange-trump-calls-elon-musk/story?id=122567621",
        "https://myanimelist.net/character/174185/Jin-Woo_Sung"
    ]
    tavily_multi_extract = Tavily(query="dummy") # query is not used here, but needed for init
    multi_extracted_contents = await tavily_multi_extract.multiple_extract_content(sample_urls)
    for item in multi_extracted_contents:
        if item.get("content"):
            logging.info(f"Extracted from {item.get('url')[:50] if item.get('url') else 'N/A'}...: {item.get('content')[:150]}...")
        else:
            logging.info(f"Failed to extract from {item.get('url') if item.get('url') else 'N/A'}: {item.get('error', 'No content and no error specified')}")

if __name__ == "__main__":
    asyncio.run(main())
