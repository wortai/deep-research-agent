import asyncio
import logging
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WebScraper:
    def __init__(self, requests_per_second: int = 2, default_parser: str = 'lxml'):
        self.requests_per_second = requests_per_second
        self.default_parser = default_parser
        logging.info(f"WebScraper initialized with requests_per_second: {requests_per_second}, default_parser: {default_parser}")

    async def _extract_title_and_images(self, soup: BeautifulSoup, base_url: str) -> dict:
        # Extracts title and image URLs using BeautifulSoup from a given soup object.
        title = soup.title.string if soup.title else "No Title"

        image_urls = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and src.strip():
                absolute_src = urljoin(base_url, src)
                if absolute_src.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')):
                    image_urls.append(absolute_src)
        return {"title": title, "images": image_urls}

    async def _get_content_with_webbaseloader(self, url: str) -> Document | None:
        # Extracts main text content using LangChain's WebBaseLoader.
        loader = WebBaseLoader(
            web_paths=[url],
            requests_per_second=self.requests_per_second,
            default_parser=self.default_parser,
            continue_on_failure=True,
            raise_for_status=False
        )
        try:
            async for doc in loader.alazy_load():
                return doc
            return None
        except Exception as e:
            logging.error(f"Error loading content with WebBaseLoader for {url}: {e}")
            return None

    async def _scrape_single_page_combined(self, url: str) -> dict:
        # Scrapes a single page, combining data from WebBaseLoader and BeautifulSoup.
        extracted_data = {
            "url": url,
            "title": "N/A",
            "body": "No content extracted.",
            "images": []
        }

        # Use WebBaseLoader's scrape_all to get a BeautifulSoup object for title/image extraction
        loader_for_soup = WebBaseLoader(
            web_paths=[url],
            requests_per_second=self.requests_per_second,
            default_parser=self.default_parser,
            continue_on_failure=True,
            raise_for_status=False
        )
        try:
            soups = await loader_for_soup.ascrape_all(urls=[url])
            if soups:
                bs_extracted = await self._extract_title_and_images(soups[0], url)
                extracted_data["title"] = bs_extracted["title"]
                extracted_data["images"] = bs_extracted["images"]
        except Exception as e:
            logging.error(f"Error getting soup for {url}: {e}")

        # Get main content using WebBaseLoader's alazy_load
        doc = await self._get_content_with_webbaseloader(url)
        if doc:
            extracted_data["body"] = doc.page_content
            # Fallback for title from WebBaseLoader metadata if not found by direct BeautifulSoup
            if extracted_data["title"] == "N/A" and doc.metadata.get("title"):
                extracted_data["title"] = doc.metadata["title"]

        return extracted_data

    async def scrape_multiple_pages(self, urls: list[str]) -> list[dict]:
        # Scrapes a list of URLs concurrently.
        logging.info(f"Starting parallel scraping for {len(urls)} URLs.")
        tasks = [self._scrape_single_page_combined(url) for url in urls]
        results = await asyncio.gather(*tasks)
        logging.info("All scraping tasks completed.")
        return results

# Example Usage:
async def main():
    urls_to_scrape = [
        "https://en.wikipedia.org/wiki/Elon_Musk",
        "https://medium.com/inside-machine-learning/what-is-a-transformer-d07dd1fbec04",
        "https://www.cars.com/",
        "https://doesnotexist.com"
    ]

    # Initialize WebScraper
    scraper = WebScraper(requests_per_second=2, default_parser='lxml')
    print("Starting parallel scraping...")
    scraped_data = await scraper.scrape_multiple_pages(urls_to_scrape)
    print("\nScraping complete. Results:")
    for data in scraped_data:
        print(f"--- URL: {data.get('url', 'N/A')}")
        print(f"Title: {data['title']}")
        print(f"Body snippet: {data['body'][:200]}..." if data['body'] else "No body content.")
        print(f"Images found: {len(data['images'])}")
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(main())
