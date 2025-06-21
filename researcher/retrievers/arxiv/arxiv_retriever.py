import arxiv
import logging
import time
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Data class to store retrieval results with metadata."""
    urls: Dict[str, List[str]] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)
    stats: Dict[str, any] = field(default_factory=dict)
    

class ArxivRetrieverError(Exception):
    """Custom exception for ArxivRetriever errors."""
    pass


class ArxivRetriever:
    """
    Enhanced ArXiv paper retriever with robust error handling and monitoring.
    
    This class retrieves arXiv paper URLs based on search queries with:
    - Comprehensive error handling and retry logic
    - Duplicate URL detection across queries
    - Performance monitoring and statistics
    - Configurable rate limiting
    
    Args:
        queries: List of search queries
        ppq: Papers per query (default: 1)
        max_retries: Maximum retry attempts for failed requests (default: 3)
        retry_delay: Delay between retries in seconds (default: 2)
        timeout: Request timeout in seconds (default: 30)
    """
    
    def __init__(
        self, 
        queries: List[str], 
        ppq: int = 1,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        timeout: float = 30.0
    ):
        # Validate inputs
        if not queries:
            raise ValueError("Queries list cannot be empty")
        if not isinstance(queries, list):
            raise TypeError("Queries must be a list")
        if ppq < 1:
            raise ValueError("Papers per query must be at least 1")
        
        self.queries = queries
        self.ppq = ppq
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        
        # Initialize client with timeout
        self.client = arxiv.Client(
            page_size=100,
            delay_seconds=0.5,  # Rate limiting
            num_retries=self.max_retries
        )
        
        # Statistics tracking
        self.stats = {
            "total_queries": len(queries),
            "successful_queries": 0,
            "failed_queries": 0,
            "total_papers_found": 0,
            "duplicate_papers_removed": 0,
            "start_time": None,
            "end_time": None
        }
    
    def _retrieve_arxiv_urls(self, query: str) -> Tuple[List[str], Optional[str]]:
        """
        Retrieve arXiv URLs for a single query with error handling.
        
        Args:
            query: Search query string
            
        Returns:
            Tuple of (list of URLs, error message if any)
        """
        search_results = []
        error_message = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Searching for query: '{query}' (attempt {attempt + 1}/{self.max_retries})")
                
                search = arxiv.Search(
                    query=query,
                    max_results=self.ppq,
                    sort_by=arxiv.SortCriterion.Relevance
                )
                
                results_found = 0
                for result in self.client.results(search):
                    try:
                        # Validate result has required attributes
                        if not result.title or not result.pdf_url:
                            logger.warning(f"Incomplete result for query '{query}': missing title or URL")
                            continue
                        
                        logger.debug(f"Found: {result.title[:50]}... - {result.pdf_url}")
                        search_results.append(result.pdf_url)
                        results_found += 1
                        
                    except AttributeError as e:
                        logger.error(f"Error processing result for query '{query}': {e}")
                        continue
                
                logger.info(f"Found {results_found} papers for query: '{query}'")
                return search_results, None
                
            except arxiv.HTTPError as e:
                error_message = f"HTTP error: {e}"
                logger.error(f"HTTP error for query '{query}': {e}")
                if e.status == 429:  # Rate limit
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                    
            except arxiv.UnexpectedEmptyPageError:
                error_message = "No results found"
                logger.warning(f"No results found for query: '{query}'")
                break  # No point retrying
                
            except Exception as e:
                error_message = f"Unexpected error: {type(e).__name__}: {str(e)}"
                logger.error(f"Unexpected error for query '{query}': {e}")
                
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        return search_results, error_message
    
    def search_arxiv(self) -> RetrievalResult:
        """
        Search arXiv for all queries and return deduplicated results.
        
        Returns:
            RetrievalResult object containing URLs, errors, and statistics
        """
        result = RetrievalResult()
        all_seen_urls: Set[str] = set()
        
        self.stats["start_time"] = datetime.now()
        
        for i, query in enumerate(self.queries, 1):
            logger.info(f"Processing query {i}/{len(self.queries)}: '{query}'")
            
            try:
                urls, error = self._retrieve_arxiv_urls(query)
                
                if error:
                    result.errors[query] = error
                    self.stats["failed_queries"] += 1
                else:
                    # Filter duplicates
                    unique_urls = []
                    duplicates_count = 0
                    
                    for url in urls:
                        if url not in all_seen_urls:
                            unique_urls.append(url)
                            all_seen_urls.add(url)
                        else:
                            duplicates_count += 1
                            logger.debug(f"Duplicate URL filtered: {url}")
                    
                    result.urls[query] = unique_urls
                    self.stats["successful_queries"] += 1
                    self.stats["total_papers_found"] += len(unique_urls)
                    self.stats["duplicate_papers_removed"] += duplicates_count
                    
                    if duplicates_count > 0:
                        logger.info(f"Removed {duplicates_count} duplicate(s) for query: '{query}'")
                        
            except Exception as e:
                logger.error(f"Critical error processing query '{query}': {e}")
                result.errors[query] = f"Critical error: {str(e)}"
                self.stats["failed_queries"] += 1
        
        self.stats["end_time"] = datetime.now()
        self.stats["duration_seconds"] = (
            self.stats["end_time"] - self.stats["start_time"]
        ).total_seconds()
        
        result.stats = self.stats
        return result
    
    def run(self) -> Dict[str, List[str]]:
        """
        Run the retriever and return URLs dictionary.
        
        Returns:
            Dictionary of query to URLs mapping
            
        Raises:
            ArxivRetrieverError: If all queries fail
        """
        logger.info(f"Starting ArXiv retrieval for {len(self.queries)} queries")
        
        result = self.search_arxiv()
        
        # Log summary
        logger.info(
            f"Retrieval complete: {self.stats['successful_queries']}/{self.stats['total_queries']} "
            f"queries successful, {self.stats['total_papers_found']} papers found, "
            f"{self.stats['duplicate_papers_removed']} duplicates removed"
        )
        
        # Raise error if all queries failed
        if self.stats["successful_queries"] == 0:
            raise ArxivRetrieverError(
                f"All {self.stats['total_queries']} queries failed. Errors: {result.errors}"
            )
        
        # Warn if some queries failed
        if result.errors:
            logger.warning(f"Failed queries: {list(result.errors.keys())}")
        
        return result.urls
    
    def run_with_metadata(self) -> RetrievalResult:
        """
        Run the retriever and return full results with metadata.
        
        Returns:
            RetrievalResult object with URLs, errors, and statistics
        """
        logger.info(f"Starting ArXiv retrieval for {len(self.queries)} queries")
        result = self.search_arxiv()
        return result


# Example usage with proper error handling
if __name__ == "__main__":
    queries = [
        "Low Rank Adaptation of Large Language Models",
        "Generative Pre-trained Transformer 3",
        "Quantum Computers",
        "Invalid Query #$%@!"  # This might fail
    ]
    
    try:
        retriever = ArxivRetriever(queries, ppq=5, max_retries=3)
        
        # Simple usage - just get URLs
        retrieved_urls = retriever.run()
        print("\nRetrieved URLs:")
        for query, urls in retrieved_urls.items():
            print(f"\n{query}: {len(urls)} papers")
            for url in urls:
                print(f"  - {url}")
        
        # Advanced usage - get full metadata
        result = retriever.run_with_metadata()
        print(f"\nStatistics:")
        for key, value in result.stats.items():
            print(f"  {key}: {value}")
        
    except ArxivRetrieverError as e:
        logger.error(f"Retrieval failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")