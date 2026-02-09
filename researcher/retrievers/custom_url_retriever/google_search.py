from ddgs import DDGS
import logging
import asyncio
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSearchRetriever:
    """
    Retrieves search results using DuckDuckGo as a reliable fallback for Google.
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless

    async def search(self, query: str, max_results: int = 10) -> List[str]:
        """
        Performs a search and returns a list of result URLs.
        
        Args:
            query: The search query.
            max_results: Maximum number of URLs to return.
            
        Returns:
            List of URL strings.
        """
        logger.info(f"Starting search for: {query}")
        extracted_urls = set()
        
        try:
            def run_search():
                with DDGS() as ddgs:
                    raw_results = list(ddgs.text(query, max_results=max_results))
                    if not raw_results:
                         logger.warning("DDGS returned no results.")
                    return [r.get('href', r.get('url')) for r in raw_results if r.get('href') or r.get('url')]
            
            results = await asyncio.to_thread(run_search)
            
            for url in results:
                extracted_urls.add(url)

            logger.info(f"Extracted {len(extracted_urls)} URLs")
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
                
        return list(extracted_urls)

if __name__ == "__main__":
    # Test block
    async def main():
        retriever = GoogleSearchRetriever(headless=True)
        query = "How neural networks work "
        urls = await retriever.search(query, max_results=20)
        print("\nFound URLs:")
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
            
    asyncio.run(main())
