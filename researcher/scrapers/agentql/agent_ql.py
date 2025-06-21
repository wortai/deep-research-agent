import os
import json
import logging
from typing import Any, Dict, Optional, Union

from langchain_agentql.tools import ExtractWebDataBrowserTool
from langchain_agentql.utils import create_async_playwright_browser
from langchain_community.tools.playwright import NavigateTool
from playwright.async_api import Browser as PlaywrightBrowser

from dotenv import load_dotenv
load_dotenv()
os.environ.get("AGENTQL_API_KEY")
# Basic logging for essential messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# AgentQLScraper class
# This class provides a utility for scraping web data using AgentQL's browser and extraction tools.
# It supports both 'prompt' and 'query' based extraction.
#


# How to use this class:
# async def main():
#     # Example using prompt
#     async with AgentQLScraper(url="https://www.example.com", prompt="Extract the main heading and all paragraphs.") as scraper:
#         data = await scraper.extract_data()
#         print(data)
#
#     # Example using query (ensure 'query' is a valid JSON string or structure as expected by AgentQL)
#     # For instance, a simple query might look like: '{"title": "h1", "description": "p"}'
#     async with AgentQLScraper(url="https://www.example.com", query='{"title": "h1", "description": "p"}') as scraper:
#         data = await scraper.extract_data()
#         print(data)
#
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())
class AgentQLScraper:
    # Initializes the AgentQLScraper with a URL and either a prompt or a query.
    def __init__(self, url: str, prompt: Optional[str] = None, query: Optional[str] = None):
        if not (prompt or query) or (prompt and query):
            raise ValueError("You must provide either 'prompt' or 'query', but not both.")
        self.url = url  # - url (str): The URL of the webpage to scrape.
        self.prompt = prompt  # - prompt (Optional[str]): A natural language prompt describing the data to extract.
        self.query = query # - query (Optional[str]): A structured query (e.g., JSON string) defining the data to extract.
        self.browser: Optional[PlaywrightBrowser] = None
        self.navigate_tool: Optional[NavigateTool] = None
        self.extract_tool: Optional[ExtractWebDataBrowserTool] = None
        
        # ! IMP - #   Note: Exactly one of 'prompt' or 'query' must be provided.
        
    



#

    # Retrieves the AgentQL API key from environment variables.
    @staticmethod
    def _get_api_key() -> str:
        api_key = os.environ.get("AGENTQL_API_KEY")
        if not api_key:
            raise ValueError("AGENTQL_API_KEY environment variable is required.")
        return api_key

    # Asynchronously initializes the Playwright browser and AgentQL tools (NavigateTool, ExtractWebDataBrowserTool).
    async def __aenter__(self) -> 'AgentQLScraper':
        try:
            self._get_api_key() # Ensures API key is present
            self.browser = await create_async_playwright_browser(headless=True)
            self.navigate_tool = NavigateTool(async_browser=self.browser)
            self.extract_tool = ExtractWebDataBrowserTool(async_browser=self.browser)
            return self
        except Exception:
            if self.browser:
                await self.browser.close()
            raise

    # Asynchronously closes the Playwright browser when exiting the async context.
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
            self.browser = None

    # Navigates to the specified URL and extracts data using the provided prompt or query.
    # Returns the extracted data as a dictionary.
    async def extract_data(self) -> Dict[str, Any]:
        if not self.browser or not self.navigate_tool or not self.extract_tool:
            raise ValueError("Browser and tools are not initialized. Use 'async with'.")

        try:
            await self.navigate_tool.ainvoke({"url": self.url, "wait_until": "domcontentloaded"})
            
            if self.prompt:
                extracted_result = await self.extract_tool.ainvoke({"prompt": self.prompt})
            elif self.query:
                extracted_result = await self.extract_tool.ainvoke({"query": self.query})
            else:
                raise ValueError("No prompt or query provided.")

            if isinstance(extracted_result, dict):
                return extracted_result
            else:
                try:
                    return json.loads(extracted_result)
                except json.JSONDecodeError:
                    return {"error": "Failed to parse extracted data", "raw_output": str(extracted_result)}

        except Exception as e:
            logger.error(f"Error during extraction for {self.url}: {e}")
            raise

async def main():
    # Example using prompt
    async with AgentQLScraper(url="https://www.goldavenue.com/en/gold-price/usd", prompt="Get me the current price of Gold.") as scraper:
        data = await scraper.extract_data()
        print(data)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())