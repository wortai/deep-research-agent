import asyncio
import logging
from typing import List, Dict, Any
from langchain_core.tools import tool
import json
from datetime import datetime
import os

# Scrapers and Retrievers Modules Import
from retrievers.arxiv import ArxivRetriever
from scrapers.arxiv import AsyncArxivScraper
from retrievers.research_rssharvest import RSSPreprintRetriever
from scrapers.medrxiv import AsyncMedRxivScraper
from scrapers.biorxiv import AsyncBioRxivScraper
from retrievers.serpapi import SerpApiClient
from scrapers.agentql import AgentQLScraper
from scrapers.browser import UniversalLoader
from scrapers.tavily import Tavily


logging.basicConfig(level=logging.INFO)

class WebSearch:
    def __init__(self, query: str, agentql_prompt:str =None, max_results: int = 10):
        """
        Initializes the WebSearch class with a query and maximum results.
        Args:
            query (str): The search query.
            max_results (int): Maximum number of results to retrieve.
        """
        self.query = query
        self.agentql_prompt = agentql_prompt if agentql_prompt else f"Extract all Important data from the page related to this query :{self.query}"
        self.max_results = max_results
        self.serpapi_client = SerpApiClient()
        self.universal_loader = UniversalLoader()
        self.tavily_scraper = Tavily(query=query, max_result=max_results)
        self.completed_urls = []
        self.results = []

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
            # Step 1: Retrieve URLs using SerpApi
            # Add the following method within the WebSearch class


            # Then, replace the $SELECTION_PLACEHOLDER$ code inside initiate_research with:

            urls  =  await self.get_serpapi_results()
            

            print("--------------------------------------------------")
            # Step 2: Scrape data using browser
            browser_results = await self.search_with_browser(urls)
            # for i, data in enumerate(browser_results):
            #     print(f"{i}: {data['url']}")
            #     print('--------------------------')
            #     print(data["content"][:100])
          
          
            # # print(f"browser_results {browser_results}")
            # print("--------------------------------------------------")
            # # Step 3: Scrape unresolved URLs using Tavily
            unresolved_urls = [url for url in urls if url not in self.completed_urls]
            tavily_results = await self.search_with_tavily(unresolved_urls)



            print(f" tavily data urls {tavily_results}")
            print("--------------------------------------------------")



            # # Step 4: Scrape remaining unresolved URLs using AgentQL
            remaining_urls = [url for url in unresolved_urls if url not in self.completed_urls]
            agentql_results = await self.search_with_agentql(remaining_urls)
            print(f"agent_ql reults {agentql_results}")
            print("--------------------------------------------------")




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


class ResearchSearch:
    @staticmethod
    @tool
    def arxiv_tool(queries: List[str], papers_per_query: int = 5) -> Dict[str, Any]:
        """
        Search and scrape ArXiv papers based on queries.
        Args:
            queries: List of search queries for ArXiv papers
            papers_per_query: Number of papers to retrieve per query (default: 5)
        Returns:
            Dictionary containing scraped paper data organized by query
        """
        try:
            retriever = ArxivRetriever(queries, ppq=papers_per_query, max_retries=3)
            retrieved_urls = retriever.run()
            scraper = AsyncArxivScraper(urls=retrieved_urls)
            output = asyncio.run(scraper.run())
            return {
                "status": "success",
                "data": output,
                "queries_processed": len(queries),
                "total_papers": sum(len(urls) for urls in retrieved_urls.values())
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "data": None
            }

    @staticmethod
    @tool
    def medrxiv_biorxiv_tool(queries: List[str], papers_per_query: int = 3, search_mode: str = 'any') -> Dict[str, Any]:
        """
        Search and scrape papers from medRxiv and bioRxiv preprint servers.
        Args:
            queries: List of search queries for medical/biological papers
            papers_per_query: Number of papers to retrieve per query (default: 3)
            search_mode: How to match queries - 'any', 'all', or 'exact' (default: 'any')
        Returns:
            Dictionary containing scraped paper data organized by query
        """
        try:
            retriever = RSSPreprintRetriever(
                queries=queries, 
                ppq=papers_per_query, 
                timeout=15,
                search_mode=search_mode
            )
            retrieved_urls = retriever.run()
            medrxiv_subjects = {}
            biorxiv_subjects = {}
            for query, urls in retrieved_urls.items():
                medrxiv_list = []
                biorxiv_list = []
                for url in urls:
                    if 'medrxiv.org' in url:
                        medrxiv_list.append(url)
                    elif 'biorxiv.org' in url:
                        biorxiv_list.append(url)
                if medrxiv_list:
                    medrxiv_subjects[query] = medrxiv_list
                if biorxiv_list:
                    biorxiv_subjects[query] = biorxiv_list
            all_papers_by_query = {}
            medrxiv_paper_count = 0
            biorxiv_paper_count = 0
            if medrxiv_subjects:
                print(f"🔬 Scraping medRxiv papers for {len(medrxiv_subjects)} subjects...")
                medrxiv_scraper = AsyncMedRxivScraper(subjects=medrxiv_subjects)
                medrxiv_results = asyncio.run(medrxiv_scraper.run())
                if isinstance(medrxiv_results, dict) and 'papers' in medrxiv_results:
                    for paper in medrxiv_results['papers']:
                        if isinstance(paper, dict):
                            paper['source'] = 'medrxiv'
                            subject = paper.get('subject', 'Unknown')
                            if subject not in all_papers_by_query:
                                all_papers_by_query[subject] = []
                            all_papers_by_query[subject].append(paper)
                            medrxiv_paper_count += 1
            if biorxiv_subjects:
                print(f"🧬 Scraping bioRxiv papers for {len(biorxiv_subjects)} subjects...")
                biorxiv_scraper = AsyncBioRxivScraper(subjects=biorxiv_subjects)
                biorxiv_results = asyncio.run(biorxiv_scraper.run())
                if isinstance(biorxiv_results, dict) and 'papers' in biorxiv_results:
                    for paper in biorxiv_results['papers']:
                        if isinstance(paper, dict):
                            paper['source'] = 'biorxiv'
                            subject = paper.get('subject', 'Unknown')
                            if subject not in all_papers_by_query:
                                all_papers_by_query[subject] = []
                            all_papers_by_query[subject].append(paper)
                            biorxiv_paper_count += 1
            total_papers = medrxiv_paper_count + biorxiv_paper_count
            return {
                "status": "success",
                "data": all_papers_by_query,
                "queries_processed": len(queries),
                "total_papers": total_papers,
                "medrxiv_papers": medrxiv_paper_count,
                "biorxiv_papers": biorxiv_paper_count,
                "urls_retrieved": retrieved_urls,
                "debug_info": {
                    "medrxiv_subjects": list(medrxiv_subjects.keys()) if medrxiv_subjects else [],
                    "biorxiv_subjects": list(biorxiv_subjects.keys()) if biorxiv_subjects else []
                }
            }
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in medrxiv_biorxiv_tool: {error_details}")
            return {
                "status": "error",
                "error": str(e),
                "error_details": error_details,
                "data": None
            }

    @classmethod
    def test_arxiv_tool(cls):
        print("Testing ArXiv Search Tool...")
        result = cls.arxiv_tool.invoke({
            "queries": ["low rank adaptation in large language models", "attention mechanism of transformers"],
            "papers_per_query": 2
        })
        print(f"Status: {result['status']}")
        if result['status'] == 'success':
            print(f"✅ Success! Found {result['total_papers']} papers")
            print(f"Processed {result['queries_processed']} queries")
        else:
            print(f"❌ Error: {result['error']}")

    @classmethod
    def test_medrxiv_biorxiv_tool(cls):
        test_queries = [
            "COVID-19 vaccine immunology",
            "cancer immunotherapy mechanisms",
            "single cell RNA sequencing clinical",
            "Short-term management of kelp forests for marine heatwaves requires planning"
        ]
        print("🧬 Testing Combined Tool")
        print("=" * 30)
        result = cls.medrxiv_biorxiv_tool.invoke({
            "queries": test_queries,
            "papers_per_query": 2,
            "search_mode": "any"
        })
        print(f"Status: {result['status']}")
        if result['status'] == 'success':
            print(f"Total papers: {result['total_papers']}")
            print(f"medRxiv papers: {result.get('medrxiv_papers', 0)}")
            print(f"bioRxiv papers: {result.get('biorxiv_papers', 0)}")
        else:
            print(f"Error: {result['error']}")

# Example usage:
if __name__ == "__main__":
    async def main():
        web_search = WebSearch(query="latest AI advancements", max_results=5)
        results = await web_search.initiate_research() # results is an array contains [{} , {} ,{}]-->{}each obj contains url , content 

        # for result in results:
        #     print(f"URL: {result['url']}")
        #     print(f"Content: {result['content'][:100]}...\n")

        ResearchSearch.test_arxiv_tool()
        ResearchSearch.test_medrxiv_biorxiv_tool()
        
    # Run the test main
    import asyncio
    asyncio.run(main())  