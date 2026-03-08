import asyncio
from researcher.scrapers.tavily.tavily_scraper import Tavily

async def main():
    tavily = Tavily(query="painting styles", depth=False, max_result=2, include_images=True)
    images, results = await tavily.basic_search()
    print("IMAGES:", images)
    print("RESULTS:")
    for r in results:
        print("KEYS:", r.keys())
        # print("URL:", r.get('url'))

if __name__ == "__main__":
    asyncio.run(main())
