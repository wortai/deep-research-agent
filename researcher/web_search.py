import asyncio
import logging
from typing import List, Dict, Any
from langchain_core.tools import tool
import json
from datetime import datetime
import os

from retrievers.serpapi import SerpApiClient
from scrapers.agentql import AgentQLScraper
from scrapers.browser import UniversalLoader
from scrapers.tavily import Tavily          
from scrapers.arxiv import ResearchSearch



logging.basicConfig(level=logging.INFO)

class WebSearch:
    def __init__(self,
            query: str,
            agentql_prompt:str =None,
            max_results: int = 10,
            arxiv_research_paper_queries: List[str] = None,
            arxiv_max_results:int = 0,
            medbio_research_paper_queries: List[str] = None,
            medbio_max_results:int = 0,

                      ):
        
        # Validate query input
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
        
        # Clean and validate query
        self.query = query.strip()
        if not self.query:
            raise ValueError("Query cannot be empty or contain only whitespace")
        
        # Validate max_results
        if max_results <= 0:
            raise ValueError("max_results must be a positive integer")
   
        self.agentql_prompt = agentql_prompt if agentql_prompt else f"Extract all Important data from the page related to this query :{self.query}"
        self.max_results = max_results
        self.serpapi_client = SerpApiClient()
        self.universal_loader = UniversalLoader()
        self.tavily_scraper = Tavily(query=self.query, max_result=max_results)
        self.completed_urls = []
        self.results = []
        self.arxiv_research_paper_queries = arxiv_research_paper_queries if arxiv_research_paper_queries else []
        self.arxiv_max_results = arxiv_max_results
        self.medbio_research_paper_queries = medbio_research_paper_queries if medbio_research_paper_queries else []
        self.medbio_max_results = medbio_max_results




    async def search_with_browser(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrapes data using the browser-based UniversalLoader.
        Args:
            urls (List[str]): List of URLs to scrape.
        Returns:
            List[Dict[str, Any]]: Extracted data from the URLs.
        """

        extracted_data = []
        for url in urls:
            try:
                data = self.universal_loader.load_data(url)
                if data.get("content"):
                    extracted_data.append({"url": url, "content": data["content"]})
                    self.completed_urls.append(url)
            except Exception as e:
                logging.error(f"Browser search failed for {url}: {e}")
        return extracted_data


    async def search_with_tavily(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrapes data using Tavily for unresolved URLs.
        Args:
            urls (List[str]): List of URLs to scrape.
        Returns:
            List[Dict[str, Any]]: Extracted data from the URLs.
        """

        extracted_data = []
        try:
            # Assuming 'multiple_extract_content' is an async method returning a list of results.
            tavily_results = await self.tavily_scraper.multiple_extract_content(urls)
            for res in tavily_results:
                if res.get("content"):
                    extracted_data.append({"metadata": res.get("metadata"), "content": res.get("content")})
                    self.completed_urls.append(res.get("url"))
        except Exception as e:
            logging.error(f"Tavily search failed: {e}")
        return extracted_data

    async def search_with_agentql(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrapes data using AgentQL for unresolved URLs.
        Args:
            urls (List[str]): List of URLs to scrape.
        Returns:
            List[Dict[str, Any]]: Extracted data from the URLs.
        """
        extracted_data = []
        for url in urls:
            try:
                async with AgentQLScraper(url=url, prompt=self.agentql_prompt) as scraper:
                    data = await scraper.extract_data()
                    # Assume the AgentQL extraction returns a dict with a "content" key
                    if "error" not in data :
                        extracted_data.append({"url": url, "content": data})
                        self.completed_urls.append(url)
            except Exception as e:
                logging.error(f"AgentQL search failed for {url}: {e}")
        return extracted_data
    
    async def get_serpapi_results(self) -> list:
        serpapi_results_combined = []
        start = max(0, self.max_results - 10)
        # Loop to accumulate results until we have at least max_results or no more results are returned.
        while len(serpapi_results_combined) < self.max_results:
            page_results = await asyncio.to_thread(self.serpapi_client.search, engine="google", q=self.query, start=start)
            if not page_results:
                break
            urls = await asyncio.to_thread(self.serpapi_client.get_clean_urls, page_results)
            serpapi_results_combined.extend(urls)
            start += len(urls)
        return serpapi_results_combined




    async def search_with_arxiv(self) -> List[Dict[str, Any]]:
        """
        Searches for research papers on Arxiv.
        Returns:
            List[Dict[str, Any]]: List of research paper details.
        """
        try:
            if not hasattr(self, 'reserach_paper_queries') or not hasattr(self, 'arxiv_max_results'):
                 logging.error("Arxiv search parameters (reserach_paper_queries, arxiv_max_results) are not set.")
                 return []

            arxiv_results = await ResearchSearch.arxiv(queries=self.arxiv_reserach_paper_queries, papers_per_query=self.arxiv_max_results)

            if arxiv_results and arxiv_results.get("status") == "success" and arxiv_results.get("data"):

                return arxiv_results["data"]
            else:
                # Log specific error if status is not success or data is missing
                status = arxiv_results.get('status', 'Unknown status') if arxiv_results else 'No results returned'
                logging.error(f"Arxiv search failed or returned no data. Status: {status}")
                return []
        except Exception as e:
            logging.error(f"An unexpected error occurred during Arxiv search: {e}")
            return []




    async def search_with_medrxiv_biorxiv(self) -> List[Dict[str, Any]]:
        """
        Searches for research papers on MedRxiv and BioRxiv.
        Returns:
            List[Dict[str, Any]]: List of research paper details.
        """
        try:
            # Check if the required parameters are set
            if not self.medbio_research_paper_queries or self.medbio_max_results <= 0:
                 logging.info("MedRxiv/BioRxiv search parameters (medbio_research_paper_queries, medbio_max_results) are not set or max_results is zero. Skipping search.")
                 return []

            # Call the research tool
            medbioxiv_results = await ResearchSearch.medrxiv_biorxiv(
                queries=self.medbio_research_paper_queries,
                papers_per_query=self.medbio_max_results
            )

            return medbioxiv_results['data']
            


        except Exception as e:
            # Catch any unexpected exceptions during the process
            logging.error(f"An unexpected error occurred during MedRxiv/BioRxiv search: {e}")
            return []


    async def initiate_research(self) -> List[Dict[str, Any]]:
        """
        Initiates the research process by retrieving URLs and scraping data using
        browser-based extraction, then Tavily and AgentQL for unresolved URLs.
        Returns:
            List[Dict[str, Any]]: Combined list of dicts in the format:
                                  {"url": <resolved URL>, "content": <extracted content>}
                                  Only resolved URLs with content are included.
        """
        try:
            # Additional validation check
            if not self.query or not self.query.strip():
                logging.error("Cannot initiate research with empty query")
                return []
            
            logging.info(f"Initiating research for query: '{self.query}'")
            # Step 1: Retrieve URLs using SerpApi
            urls  =  await self.get_serpapi_results()
            

            print("--------------------------------------------------")
            # Step 2: Scrape data using browser
            browser_results = await self.search_with_browser(urls)
      
          

            print("--------------------------------------------------")
            # # Step 3: Scrape unresolved URLs using Tavily
            unresolved_urls = [url for url in urls if url not in self.completed_urls]
            tavily_results = await self.search_with_tavily(unresolved_urls)
            print("--------------------------------------------------")



            # # Step 4: Scrape remaining unresolved URLs using AgentQL
            remaining_urls = [url for url in unresolved_urls if url not in self.completed_urls]
            agentql_results = await self.search_with_agentql(remaining_urls)       
            print("--------------------------------------------------")

            # Step 5: using research papers if mentioned 
            if len(self.arxiv_research_paper_queries) > 0 and len(self.arxiv_max_results) > 0:
                


            # Combine all results
            self.results.extend(browser_results)
            self.results.extend(tavily_results)
            self.results.extend(agentql_results)





            # Only include results with non-error content
            final_results = [{"url": res["url"], "content": res["content"]}
                             for res in self.results if res.get("content")]
            return final_results

        except Exception as e:
            logging.error(f"Error during research initiation: {e}")
            return []
# Example usage:
if __name__ == "__main__":
    async def main():
        web_search = WebSearch(query="latest AI advancements", max_results=5)
        results = await web_search.initiate_research() # results is an array contains [{} , {} ,{}]-->{}each obj contains url , content 

        for result in results:
            print(f"URL: {result['url']}")
            print(f"Content: {result['content'][:100]}...\n")

        ResearchSearch.test_arxiv_tool()
        ResearchSearch.test_medrxiv_biorxiv_tool()
        
    # Run the test main
    import asyncio
    asyncio.run(main())  