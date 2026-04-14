# Amazon

import os
import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProductResult:
    """Data class to standardize product results across platforms"""
    title: str
    price: Optional[str]
    rating: Optional[float]
    reviews_count: Optional[int]
    source: str
    link: Optional[str]
    image: Optional[str]
    platform: str
    raw_data: Dict[str, Any]

class SerpApiProductSearch:
    """
    A production-ready class for searching products across multiple platforms using SerpApi.
    Supports Google Shopping, Walmart, Home Depot, and eBay.
    """
    
    BASE_URL = "https://serpapi.com/search"
    
    def __init__(self, api_key: str):
        """
        Initialize the SerpApi client.
        
        Args:
            api_key (str): Your SerpApi API key
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SerpApiProductSearch/1.0'
        })
    
    def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to SerpApi with error handling.
        
        Args:
            params (Dict[str, Any]): Request parameters
            
        Returns:
            Dict[str, Any]: API response data
            
        Raises:
            Exception: If API request fails
        """
        params['api_key'] = self.api_key
        
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise Exception(f"SerpApi request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise Exception(f"Invalid JSON response: {e}")
    
    def _extract_google_products(self, data: Dict[str, Any]) -> List[ProductResult]:
        """Extract and standardize Google Shopping results."""
        products = []
        shopping_results = data.get('shopping_results', [])
        
        for item in shopping_results:
            products.append(ProductResult(
                title=item.get('title', ''),
                price=item.get('price', ''),
                rating=item.get('rating'),
                reviews_count=item.get('reviews'),
                source=item.get('source', ''),
                link=item.get('link') or item.get('product_link', ''),
                image=item.get('thumbnail', ''),
                platform='Google Shopping',
                raw_data=item
            ))
        
        return products
    
    def _extract_walmart_products(self, data: Dict[str, Any]) -> List[ProductResult]:
        """Extract and standardize Walmart results."""
        products = []
        organic_results = data.get('organic_results', [])
        
        for item in organic_results:
            # Walmart's product link is often in 'product_page_url'
            link = item.get('product_page_url') or item.get('link') or item.get('product_link', '')
            products.append(ProductResult(
                title=item.get('title', ''),
                price=item.get('primary_offer', {}).get('offer_price', ''),
                rating=item.get('rating'),
                reviews_count=item.get('reviews_count'),
                source='Walmart',
                link=link,
                image=item.get('thumbnail', ''),
                platform='Walmart',
                raw_data=item
            ))
        
        return products
    
    def _extract_homedepot_products(self, data: Dict[str, Any]) -> List[ProductResult]:
        """Extract and standardize Home Depot results."""
        products = []
        products_results = data.get('products', [])
        
        for item in products_results:
            products.append(ProductResult(
                title=item.get('title', ''),
                price=item.get('price', ''),
                rating=item.get('rating'),
                reviews_count=item.get('reviews_count'),
                source='Home Depot',
                link=item.get('link', ''),
                image=item.get('thumbnail', ''),
                platform='Home Depot',
                raw_data=item
            ))
        
        return products
    
    def _extract_ebay_products(self, data: Dict[str, Any]) -> List[ProductResult]:
        """Extract and standardize eBay results."""
        products = []
        organic_results = data.get('organic_results', [])
        
        for item in organic_results:
            products.append(ProductResult(
                title=item.get('title', ''),
                price=item.get('price', {}).get('raw', '') if isinstance(item.get('price'), dict) else item.get('price', ''),
                rating=None,  # eBay results may not always have ratings
                reviews_count=None,
                source='eBay',
                link=item.get('link', ''),
                image=item.get('thumbnail', ''),
                platform='eBay',
                raw_data=item
            ))
        
        return products
    
    def search_google_shopping(self, query: str, **kwargs) -> List[ProductResult]:
        """
        Search Google Shopping for products.
        
        Args:
            query (str): Search query
            **kwargs: Additional parameters (num, hl, gl, location, etc.)
            
        Returns:
            List[ProductResult]: List of standardized product results
        """
        params = {
            'engine': 'google_shopping',
            'q': query,
            'num': kwargs.get('num', 20),
            'hl': kwargs.get('hl', 'en'),
            'gl': kwargs.get('gl', 'us'),
            **{k: v for k, v in kwargs.items() if k not in ['num', 'hl', 'gl']}
        }
        
        logger.info(f"Searching Google Shopping for: {query}")
        data = self._make_request(params)
        return self._extract_google_products(data)
    
    def search_walmart(self, query: str, **kwargs) -> List[ProductResult]:
        """
        Search Walmart for products.
        
        Args:
            query (str): Search query
            **kwargs: Additional parameters (max_page, sort, facets, etc.)
            
        Returns:
            List[ProductResult]: List of standardized product results
        """
        params = {
            'engine': 'walmart',
            'query': query,
            'max_page': kwargs.get('max_page', 1),
            **{k: v for k, v in kwargs.items() if k != 'max_page'}
        }
        
        logger.info(f"Searching Walmart for: {query}")
        data = self._make_request(params)
        return self._extract_walmart_products(data)
    
    def search_homedepot(self, query: str, **kwargs) -> List[ProductResult]:
        """
        Search Home Depot for products.
        
        Args:
            query (str): Search query
            **kwargs: Additional parameters (max_page, delivery_zip, store_id, etc.)
            
        Returns:
            List[ProductResult]: List of standardized product results
        """
        params = {
            'engine': 'home_depot',
            'q': query,
            'max_page': kwargs.get('max_page', 1),
            **{k: v for k, v in kwargs.items() if k != 'max_page'}
        }
        
        logger.info(f"Searching Home Depot for: {query}")
        data = self._make_request(params)
        return self._extract_homedepot_products(data)
    
    def search_ebay(self, query: str, **kwargs) -> List[ProductResult]:
        """
        Search eBay for products.
        
        Args:
            query (str): Search query
            **kwargs: Additional parameters (_nkw, _sacat, _from, etc.)
            
        Returns:
            List[ProductResult]: List of standardized product results
        """
        params = {
            'engine': 'ebay',
            '_nkw': query,
            **kwargs
        }
        
        logger.info(f"Searching eBay for: {query}")
        data = self._make_request(params)
        return self._extract_ebay_products(data)
    
    def search_all_platforms(self, query: str, **kwargs) -> Dict[str, List[ProductResult]]:
        """
        Search all platforms for products.
        
        Args:
            query (str): Search query
            **kwargs: Additional parameters (will be applied to all platforms where applicable)
            
        Returns:
            Dict[str, List[ProductResult]]: Results grouped by platform
        """
        # Map 'zipcode' to 'delivery_zip' for Home Depot
        if 'zipcode' in kwargs:
            kwargs['delivery_zip'] = kwargs['zipcode']
        results = {}
        
        try:
            results['google_shopping'] = self.search_google_shopping(query, **kwargs)
        except Exception as e:
            logger.error(f"Google Shopping search failed: {e}")
            results['google_shopping'] = []
        
        try:
            results['walmart'] = self.search_walmart(query, **kwargs)
        except Exception as e:
            logger.error(f"Walmart search failed: {e}")
            results['walmart'] = []
        
        try:
            results['homedepot'] = self.search_homedepot(query, **kwargs)
        except Exception as e:
            logger.error(f"Home Depot search failed: {e}")
            results['homedepot'] = []
        
        try:
            results['ebay'] = self.search_ebay(query, **kwargs)
        except Exception as e:
            logger.error(f"eBay search failed: {e}")
            results['ebay'] = []
        
        return results



# ---------- TEST SCRIPT ---------- #
def print_products(products: list, platform_name: str = "", limit: int = 3):
    """Helper function to print product results in a readable format."""
    if not products:
        print(f"No products found for {platform_name}")
        return
    
    print(f"\n=== {platform_name} Results ===")
    for i, product in enumerate(products[:limit], 1):
        print(f"{i}. {product.title}")
        print(f"   Price: {product.price}")
        print(f"   Rating: {product.rating}/5 ({product.reviews_count} reviews)" if product.rating else "   Rating: N/A")
        print(f"   Source: {product.source}")
        print(f"   Platform: {product.platform}")
        print(f"   Link: {product.link}")
        print("-" * 80)


def example_single_platform_searches():
    """Example of searching individual platforms."""
    # Initialize the API client
    # Replace 'your_api_key_here' with your actual SerpApi key
    api_key = os.getenv('SERP_API_KEY')
    search_client = SerpApiProductSearch(api_key)
    
    search_query = "wireless headphones"
    
    print("🔍 Single Platform Search Examples")
    print("=" * 50)
    
    # Google Shopping search
    try:
        google_results = search_client.search_google_shopping(
            search_query, 
            num=10,
            hl='en',
            gl='us'
        )
        print_products(google_results, "Google Shopping", 3)
    except Exception as e:
        print(f"Google Shopping search failed: {e}")
    
    # Walmart search
    try:
        walmart_results = search_client.search_walmart(
            search_query,
            max_page=1
        )
        print_products(walmart_results, "Walmart", 3)
    except Exception as e:
        print(f"Walmart search failed: {e}")
    
    # Home Depot search
    try:
        homedepot_results = search_client.search_homedepot(
            search_query,
            max_page=1,
            delivery_zip='10001'  # NYC zip code
        )
        print_products(homedepot_results, "Home Depot", 3)
    except Exception as e:
        print(f"Home Depot search failed: {e}")
    
    # eBay search
    try:
        ebay_results = search_client.search_ebay(
            search_query,
            _sacat='0',  # All categories
            _from='R40'  # Buy It Now
        )
        print_products(ebay_results, "eBay", 3)
    except Exception as e:
        print(f"eBay search failed: {e}")


def example_multi_platform_search():
    """Example of searching all platforms at once."""
    api_key = os.getenv('SERP_API_KEY')
    search_client = SerpApiProductSearch(api_key)
    
    search_query = "bluetooth speaker"
    
    print("\n\n🔍 Multi-Platform Search Example")
    print("=" * 50)
    
    try:
        all_results = search_client.search_all_platforms(
            search_query,
            num=5,  # For Google Shopping
            max_page=1,  # For Walmart and Home Depot
            zipcode='30301'  # Example: Atlanta, GA zip code
        )
        
        for platform, products in all_results.items():
            platform_name = platform.replace('_', ' ').title()
            print_products(products, platform_name, 2)
            
    except Exception as e:
        print(f"Multi-platform search failed: {e}")

def main():
    """Main function to run all examples."""
    
    # Run examples
    example_single_platform_searches()
    example_multi_platform_search()
    
    print("\n\n✨ All examples completed!")


if __name__ == "__main__":
    main()