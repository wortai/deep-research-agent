from serpapi import GoogleSearch
import os 
import logging
from dotenv import load_dotenv
load_dotenv()
class SerpApiClient:
    def __init__(self):
        self.engine: str | None = None
        self.params: dict = {}

    def _build_params(self, engine: str, **kwargs) -> dict:
        
        """
        Builds the parameters dictionary for the SerpApi search using a dictionary dispatch for engines.
        """
        base_params = {"api_key": self.get_api_key(), "engine": engine}

        # Dictionary to simulate switch-case for engine-specific parameter validation and building
        param_builders = {
            "google": self._build_google_params,
            "youtube": self._build_youtube_params,
            "amazon": self._build_amazon_params,
            "google_images": self._build_google_images_params,
            "google_finance": self._build_google_finance_params,
        }

        builder_func = param_builders.get(engine)
        if builder_func:
            engine_specific_params = builder_func(**kwargs)
            base_params.update(engine_specific_params)
        else:
            raise ValueError(f"Unsupported engine: {engine}")

        return base_params

    def get_api_key(self):
        try:
            print(os.environ.get("SERP_API_KEY"))
            return os.environ.get("SERP_API_KEY")
        except KeyError:
            logging.error("SERP API key not found.") # Improved error message
            raise Exception("SERP API key not found. Please set the SERP API KEY environment variable.")

    def _build_google_params(self, **kwargs) -> dict:
        # Check required parameter 'q'
        if "q" not in kwargs:
            raise ValueError("For Google Search, 'q' (query) parameter is required.")
        
        # Initialize params with the query value
        params = {"q": kwargs["q"]}
        
        # List of optional parameters to include if provided
        optional_keys = ["location", "start", "num", "hl", "gl"]
        for key in optional_keys:
            if key in kwargs:
                params[key] = kwargs[key]
        
        return params

    def _build_youtube_params(self, **kwargs) -> dict:
        params = {}
        if "search_query" not in kwargs:
            raise ValueError("For YouTube, 'search_query' parameter is required.")
        params["search_query"] = kwargs["search_query"]
        return params

    def _build_amazon_params(self, **kwargs) -> dict:
        params = {}
        if "q" not in kwargs:
            raise ValueError("For Amazon Search, 'q' (query) parameter is required.")
        params["q"] = kwargs["q"]
        if "asin" in kwargs:
            params["asin"] = kwargs["asin"]
        return params

    def _build_google_images_params(self, **kwargs) -> dict:
        params = {}
        if "q" not in kwargs:
            raise ValueError("For Google Images, 'q' (query) parameter is required.")
        params["q"] = kwargs["q"]
        return params

    def _build_google_finance_params(self, **kwargs) -> dict:
        params = {}
        if "q" not in kwargs:
            raise ValueError("For Google Finance, 'q' (query) parameter is required.")
        params["q"] = kwargs["q"]
        return params

    def search(self, engine: str, **kwargs) -> dict:
        """
        Executes the SerpApi search for the specified engine and parameters.
        """
        self.engine = engine
        self.params = self._build_params(engine, **kwargs)

        search = GoogleSearch(self.params)
        return search.get_dict()

    def get_clean_urls(self, results: dict) -> list[str]:
        """
        Extracts URLs from the search results based on the engine using a dictionary dispatch.
        """
        urls: list[str] = []

        if not self.engine:
            return urls # No engine set in this instance

        # Dictionary to simulate switch-case for engine-specific URL extraction
        url_extractors = {
            "google": self._extract_google_urls,
            "youtube": self._extract_youtube_urls,
            "amazon": self._extract_amazon_urls,
            "google_images": self._extract_google_images_urls,
            "google_finance": self._extract_google_finance_urls,
        }

        extractor_func = url_extractors.get(self.engine)
        if extractor_func:
            urls.extend(extractor_func(results))

        return urls

    def _extract_google_urls(self, results: dict) -> list[str]:
        extracted_urls: list[str] = []
        if "organic_results" in results:
            for result in results["organic_results"]:
                if "link" in result:
                    extracted_urls.append(result["link"])
        return extracted_urls

    def _extract_youtube_urls(self, results: dict) -> list[str]:
        extracted_urls: list[str] = []
        if "video_results" in results:
            for result in results["video_results"]:
                if "link" in result:
                    extracted_urls.append(result["link"])
        if "channels" in results:
            for channel in results["channels"]:
                if "link" in channel:
                    extracted_urls.append(channel["link"])
        return extracted_urls

    def _extract_amazon_urls(self, results: dict) -> list[str]:
        extracted_urls: list[str] = []
        if "products" in results:
            for product in results["products"]:
                if "link" in product:
                    extracted_urls.append(product["link"])
        if "organic_results" in results:
            for result in results["organic_results"]:
                if "link" in result:
                    extracted_urls.append(result["link"])
        return extracted_urls

    def _extract_google_images_urls(self, results: dict) -> list[str]:
        extracted_urls: list[str] = []
        if "images_results" in results:
            for image in results["images_results"]:
                if "original" in image:
                    extracted_urls.append(image["original"])
        return extracted_urls

    def _extract_google_finance_urls(self, results: dict) -> list[str]:
        extracted_urls: list[str] = []
        if "news_results" in results:
            for news in results["news_results"]:
                if "link" in news:
                    extracted_urls.append(news["link"])
        if "markets" in results:
            for market in results["markets"]:
                if "link" in market:
                    extracted_urls.append(market["link"])
        return extracted_urls
    


# if __name__ == "__main__":
#     client = SerpApiClient()
#     try:
#         # Replace "your-search-term" with an actual query and adjust "start" as needed.
#         results = client.search("google", q="your-search-term", start=5)
#         urls = client.get_clean_urls(results)
#         print("Extracted URLs:")
#         for url in urls:
#             print(url)
#     except Exception as e:
#         print(f"An error occurred: {e}")