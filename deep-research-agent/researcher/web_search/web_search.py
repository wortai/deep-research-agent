import asyncio
import logging
from typing import List, Dict, Any
from langchain_core.tools import tool
import json
from datetime import datetime
import os

from researcher.retrievers.serpapi import SerpApiClient
from researcher.scrapers.browser import UniversalLoader
from researcher.scrapers.tavily import Tavily
# from researcher.scrapers.arxiv import ResearchSearch


logging.basicConfig(level=logging.INFO)


class WebSearch:
    def __init__(
        self,
        query: str,
        agentql_prompt: str = None,
        max_results: int = 10,
        arxiv_research_paper_queries: List[str] = None,
        arxiv_max_results: int = 0,
        medbio_research_paper_queries: List[str] = None,
        medbio_max_results: int = 0,
    ):
        self.query = query
        self.agentql_prompt = (
            agentql_prompt
            if agentql_prompt
            else f"Extract all Important data from the page related to this query :{self.query}"
        )
        self.max_results = max_results
        self.serpapi_client = SerpApiClient()
        self.google_retriever = None
        self.universal_loader = UniversalLoader()
        self.tavily_scraper = Tavily(query=query, max_result=max_results)
        self.completed_urls = []
        self.results = []
        self.arxiv_research_paper_queries = (
            arxiv_research_paper_queries if arxiv_research_paper_queries else []
        )
        self.arxiv_max_results = arxiv_max_results
        self.medbio_research_paper_queries = (
            medbio_research_paper_queries if medbio_research_paper_queries else []
        )
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
                # Run synchronous loader in a thread to prevent blocking event loop
                data = await asyncio.to_thread(self.universal_loader.load_data, url)
                if isinstance(data, dict) and data.get("content"):
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
            tavily_results = await self.tavily_scraper.multiple_extract_content(urls)
            if isinstance(tavily_results, list):
                for res in tavily_results:
                    if isinstance(res, dict) and res.get("content"):
                        extracted_data.append(
                            {"url": res.get("url"), "content": res.get("content")}
                        )
                        self.completed_urls.append(res.get("url"))
            else:
                logging.error(
                    f"Tavily returned an error instead of a list: {tavily_results}"
                )
        except Exception as e:
            logging.error(f"Tavily search failed: {e}")
        return extracted_data

    @staticmethod
    async def search_with_multiple_advance_queries(
        queries: List[str],
        max_results_per_query: int = 2,
        include_images: bool = True,
        include_raw_content: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Performs multiple advanced Tavily searches concurrently.
        Uses Tavily's multiple_advance_queries for efficient batch retrieval.
        Returns results with url, content, title, and images for richer analysis.

        Args:
            queries: List of search queries to execute.
            max_results_per_query: Max results per query. Default 2.
            include_images: Include images in results. Default True.
            include_raw_content: Include raw content when available. Default True.

        Returns:
            List of dicts: {"url", "content", "title", "images"}
        """
        if not queries:
            logging.warning(
                "No queries provided to search_with_multiple_advance_queries."
            )
            return []

        try:
            tavily = Tavily(
                queries=queries,
                depth=True,
                max_result=max_results_per_query,
                include_images=include_images,
                include_raw_content=include_raw_content,
            )
            responses = await tavily.multiple_advance_queries()
        except Exception as e:
            logging.error(f"Multiple advance queries failed: {e}")
            return []

        all_results = []
        for resp in responses:
            if "error" in resp:
                logging.warning(
                    f"Query '{resp.get('query', '')}' failed: {resp['error']}"
                )
                continue

            results = resp.get("results", [])
            raw_images = resp.get("images", [])

            # Normalize images to {url, description} format (Tavily returns url + description)
            images: List[Dict[str, str]] = []
            for img in raw_images:
                img_url = img.get("url") or img.get("src", "")
                img_desc = img.get("description") or img.get("alt") or ""
                if img_url:
                    images.append({"url": img_url, "description": img_desc})

            for r in results:
                url = r.get("url")
                content = r.get("raw_content") or r.get("content") or ""
                title = r.get("title", "")

                if not url or not content:
                    continue

                item: Dict[str, Any] = {
                    "url": url,
                    "content": content,
                    "title": title,
                }
                if images:
                    item["images"] = images
                all_results.append(item)

        return all_results

    async def search_with_agentql(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrapes data using AgentQL for unresolved URLs.
        Args:
            urls (List[str]): List of URLs to scrape.
        Returns:
            List[Dict[str, Any]]: Extracted data from the URLs.
        """
        extracted_data = []
        try:
            from researcher.scrapers.agentql import AgentQLScraper
        except ImportError:
            logging.warning(
                "AgentQL not available (missing dependencies). Skipping AgentQL scraping."
            )
            return extracted_data
        for url in urls:
            try:
                async with AgentQLScraper(
                    url=url, prompt=self.agentql_prompt
                ) as scraper:
                    data = await scraper.extract_data()
                    # Assume the AgentQL extraction returns a dict with a "content" key
                    if "error" not in data:
                        extracted_data.append({"url": url, "content": data})
                        self.completed_urls.append(url)
            except Exception as e:
                logging.error(f"AgentQL search failed for {url}: {e}")
        return extracted_data

    async def get_serpapi_results(self) -> list:
        serpapi_results_combined = []
        start = 0
        # Loop to accumulate results until we have at least max_results or no more results are returned.
        while len(serpapi_results_combined) < self.max_results:
            page_results = await asyncio.to_thread(
                self.serpapi_client.search, engine="google", q=self.query, start=start
            )
            if not page_results:
                break
            urls = await asyncio.to_thread(
                self.serpapi_client.get_clean_urls, page_results
            )
            serpapi_results_combined.extend(urls)
            start += 1

        # print(serpapi_results_combined)
        return serpapi_results_combined[: self.max_results]

    async def get_google_results(self) -> list:
        """
        Retrieves URLs using the custom Google retriever (DuckDuckGo backed).
        """
        try:
            if self.google_retriever is None:
                from researcher.retrievers.custom_url_retriever.google_search import (
                    GoogleSearchRetriever,
                )

                self.google_retriever = GoogleSearchRetriever()
            urls = await self.google_retriever.search(
                self.query, max_results=self.max_results
            )
            return urls
        except Exception as e:
            logging.error(f"Google custom search failed: {e}")
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
            print("Step 1: Retrieve URLs using SerpApi")
            # urls = await self.get_serpapi_results() # Deprecated due to quota limits
            urls = await self.get_google_results()

            for url in urls:
                print(url)

            print("--------------------------------------------------")
            # Step 2: Scrape data using Tavily first
            tavily_results = await self.search_with_tavily(urls)
            print("--------------------------------------------------")

            # Step 3: Scrape unresolved URLs using  browser
            unresolved_urls = [url for url in urls if url not in self.completed_urls]
            browser_results = await self.search_with_browser(unresolved_urls)
            print("--------------------------------------------------")

            # # Step 4: Scrape remaining unresolved URLs using AgentQL
            remaining_urls = [
                url for url in unresolved_urls if url not in self.completed_urls
            ]
            agentql_results = await self.search_with_agentql(remaining_urls)
            print("--------------------------------------------------")

            # Combine all results
            self.results.extend(browser_results)
            self.results.extend(tavily_results)
            self.results.extend(agentql_results)

            # Only include results with non-error content
            final_results = [
                {"url": res["url"], "content": res["content"]}
                for res in self.results
                if res.get("content")
            ]
            return final_results

        except Exception as e:
            logging.error(f"Error during research initiation: {e}")
            return []


# Example usage:
if __name__ == "__main__":

    async def main():
        web_search = WebSearch(query="latest AI advancements", max_results=2)
        results = await web_search.initiate_research()  # results is an array contains [{} , {} ,{}]-->{}each obj contains url , content

        for result in results:
            print(f"URL: {result['url']}")
            print(f"Content: {result['content'][:100]}...\n")

    # Run the test main
    import asyncio

    asyncio.run(main())
