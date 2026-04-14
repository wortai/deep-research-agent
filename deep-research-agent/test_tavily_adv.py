import asyncio
from researcher.scrapers.tavily.tavily_scraper import Tavily

async def main():
    tavily = Tavily(query="painting styles", depth=True, max_result=2, include_images=True, include_raw_content=True)
    images, results = await tavily.advance_search()
    print("RESULTS:")
    for r in results:
        print("KEYS:", r.keys())
        if 'images' in r:
            print("HAS IMAGES")
        print("URL:", r.get('url'))

if __name__ == "__main__":
    asyncio.run(main())
