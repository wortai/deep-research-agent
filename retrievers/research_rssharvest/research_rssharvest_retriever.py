import json
import feedparser
import requests
import logging
import time
import re
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    """Data class to store retrieval results with metadata."""
    urls: Dict[str, List[str]] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)
    stats: Dict[str, any] = field(default_factory=dict)

class PreprintRetrieverError(Exception):
    """Custom exception for PreprintRetriever errors."""
    pass

class RSSPreprintRetriever:
    """
    Fast RSS-based preprint retriever for MedRxiv and BioRxiv.
    
    Downloads RSS feeds in real-time and searches through them for matching papers.
    Much faster than browser automation while still being comprehensive.
    
    Args:
        queries: List of search queries
        ppq: Papers per query (default: 5)
        timeout: Request timeout for RSS feeds (default: 15)
        search_mode: 'any' (match any word) or 'all' (match all words) (default: 'any')
    """
    
    def __init__(
        self,
        queries: List[str],
        ppq: int = 5,
        timeout: int = 15,
        search_mode: str = 'any'
    ):
        if not queries:
            raise ValueError("Queries list cannot be empty")
        
        self.queries = queries
        self.ppq = ppq
        self.timeout = timeout
        self.search_mode = search_mode
        
        # RSS feed URLs for different sources and categories
        self.rss_feeds = {
            'medrxiv': {
                'all': 'https://connect.medrxiv.org/medrxiv_xml.php',
                'infectious_diseases': 'https://connect.medrxiv.org/medrxiv_xml.php?subject=infectious_diseases',
                'public_health': 'https://connect.medrxiv.org/medrxiv_xml.php?subject=public_health',
                'epidemiology': 'https://connect.medrxiv.org/medrxiv_xml.php?subject=epidemiology',
                'cardiovascular_medicine': 'https://connect.medrxiv.org/medrxiv_xml.php?subject=cardiovascular_medicine',
                'oncology': 'https://connect.medrxiv.org/medrxiv_xml.php?subject=oncology'
            },
            'biorxiv': {
                'all': 'https://connect.biorxiv.org/biorxiv_xml.php',
                'molecular_biology': 'https://connect.biorxiv.org/biorxiv_xml.php?subject=molecular_biology',
                'neuroscience': 'https://connect.biorxiv.org/biorxiv_xml.php?subject=neuroscience',
                'cell_biology': 'https://connect.biorxiv.org/biorxiv_xml.php?subject=cell_biology',
                'genetics': 'https://connect.biorxiv.org/biorxiv_xml.php?subject=genetics',
                'bioinformatics': 'https://connect.biorxiv.org/biorxiv_xml.php?subject=bioinformatics'
            }
        }
        
        # Statistics tracking
        self.stats = {
            "total_queries": len(queries),
            "successful_queries": 0,
            "failed_queries": 0,
            "total_papers_found": 0,
            "total_feeds_processed": 0,
            "medrxiv_papers": 0,
            "biorxiv_papers": 0,
            "start_time": None,
            "end_time": None
        }
    
    def _fetch_rss_feed(self, url: str, source: str, category: str) -> List[Dict]:
        """Fetch and parse a single RSS feed."""
        papers = []
        
        try:
            logger.debug(f"Fetching RSS feed: {source}/{category}")
            
            # Add timeout and headers to avoid blocks
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; RSS Reader; +http://example.com/bot)'
            }
            
            # Use requests with timeout first, then feedparser
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse with feedparser
            feed = feedparser.parse(response.content)
            
            # Check if feed parsed successfully
            if hasattr(feed, 'bozo') and feed.bozo:
                logger.warning(f"RSS feed parsing warning for {source}/{category}: {feed.bozo_exception}")
            
            # Extract papers from feed entries
            for entry in feed.entries:
                try:
                    paper = {
                        'title': entry.get('title', '').strip(),
                        'url': entry.get('link', '').strip(),
                        'abstract': entry.get('summary', '').strip(),
                        'published': entry.get('published', ''),
                        'authors': self._extract_authors(entry),
                        'source': source,
                        'category': category
                    }
                    
                    # Validate essential fields
                    if paper['title'] and paper['url'] and self._is_valid_paper_url(paper['url'], source):
                        papers.append(paper)
                    
                except Exception as e:
                    logger.debug(f"Error parsing feed entry: {e}")
                    continue
            
            logger.info(f"Fetched {len(papers)} papers from {source}/{category}")
            self.stats['total_feeds_processed'] += 1
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch RSS feed {source}/{category}: {e}")
        except Exception as e:
            logger.error(f"Error processing RSS feed {source}/{category}: {e}")
        
        return papers
    
    def _extract_authors(self, entry) -> List[str]:
        """Extract authors from RSS entry."""
        authors = []
        
        try:
            # Try different author fields
            if hasattr(entry, 'authors') and entry.authors:
                for author in entry.authors:
                    if hasattr(author, 'name'):
                        authors.append(author.name)
                    elif isinstance(author, dict) and 'name' in author:
                        authors.append(author['name'])
            
            # Fallback: extract from title (common in preprint RSS)
            if not authors and hasattr(entry, 'title'):
                # Look for author patterns in title like "Title (Author1, Author2)"
                author_match = re.search(r'\(([^)]+)\)$', entry.title)
                if author_match:
                    author_string = author_match.group(1)
                    authors = [name.strip() for name in author_string.split(',')]
        
        except Exception as e:
            logger.debug(f"Error extracting authors: {e}")
        
        return authors
    
    def _is_valid_paper_url(self, url: str, source: str) -> bool:
        """Validate if URL is a valid paper URL."""
        if not url:
            return False
        
        # Check for proper preprint URL format
        valid_patterns = [
            f'{source}.org/content/',
            f'{source}.org/cgi/content/',
            '/content/10.1101/'
        ]
        
        return any(pattern in url for pattern in valid_patterns)
    
    def _harvest_all_feeds(self) -> List[Dict]:
        """Harvest papers from all RSS feeds."""
        all_papers = []
        
        logger.info("Starting RSS feed harvesting...")
        
        # Harvest from all sources and categories
        for source, categories in self.rss_feeds.items():
            for category, url in categories.items():
                papers = self._fetch_rss_feed(url, source, category)
                all_papers.extend(papers)
                
                # Small delay between feeds to be respectful
                time.sleep(0.5)
        
        # Remove duplicates by URL
        seen_urls = set()
        unique_papers = []
        
        for paper in all_papers:
            if paper['url'] not in seen_urls:
                seen_urls.add(paper['url'])
                unique_papers.append(paper)
        
        logger.info(f"Harvested {len(unique_papers)} unique papers from {self.stats['total_feeds_processed']} feeds")
        return unique_papers
    
    def _search_papers(self, papers: List[Dict], query: str) -> List[str]:
        """Search through harvested papers for query matches."""
        matching_urls = []
        query_terms = [term.lower().strip() for term in query.split()]
        
        for paper in papers:
            # Create searchable text from title and abstract
            searchable_text = f"{paper['title']} {paper['abstract']}".lower()
            
            # Check for matches based on search mode
            if self.search_mode == 'all':
                # All query terms must be present
                if all(term in searchable_text for term in query_terms):
                    matching_urls.append(paper['url'])
            else:  # search_mode == 'any'
                # Any query term can match
                if any(term in searchable_text for term in query_terms):
                    matching_urls.append(paper['url'])
            
            # Stop when we have enough papers
            if len(matching_urls) >= self.ppq:
                break
        
        return matching_urls
    
    def search_preprints(self) -> RetrievalResult:
        """Main method to search preprints using RSS harvesting."""
        result = RetrievalResult()
        self.stats["start_time"] = datetime.now()
        
        try:
            # Step 1: Harvest all papers from RSS feeds
            all_papers = self._harvest_all_feeds()
            
            if not all_papers:
                error_msg = "No papers could be harvested from RSS feeds"
                logger.error(error_msg)
                for query in self.queries:
                    result.errors[query] = error_msg
                    self.stats["failed_queries"] += 1
                return result
            
            # Step 2: Search through harvested papers for each query
            all_seen_urls = set()
            
            for query in self.queries:
                logger.info(f"Searching for query: '{query}'")
                
                try:
                    # Search through all harvested papers
                    matching_urls = self._search_papers(all_papers, query)
                    
                    # Remove global duplicates (across queries)
                    unique_urls = []
                    for url in matching_urls:
                        if url not in all_seen_urls:
                            unique_urls.append(url)
                            all_seen_urls.add(url)
                    
                    if unique_urls:
                        result.urls[query] = unique_urls
                        self.stats["successful_queries"] += 1
                        self.stats["total_papers_found"] += len(unique_urls)
                        
                        # Count by source
                        for url in unique_urls:
                            if 'medrxiv.org' in url:
                                self.stats["medrxiv_papers"] += 1
                            elif 'biorxiv.org' in url:
                                self.stats["biorxiv_papers"] += 1
                        
                        logger.info(f"Found {len(unique_urls)} papers for query: '{query}'")
                    else:
                        result.errors[query] = "No matching papers found"
                        self.stats["failed_queries"] += 1
                        logger.warning(f"No papers found for query: '{query}'")
                
                except Exception as e:
                    error_msg = f"Error searching for query '{query}': {e}"
                    logger.error(error_msg)
                    result.errors[query] = error_msg
                    self.stats["failed_queries"] += 1
        
        except Exception as e:
            error_msg = f"Critical error during RSS harvesting: {e}"
            logger.error(error_msg)
            for query in self.queries:
                result.errors[query] = error_msg
                self.stats["failed_queries"] += 1
        
        self.stats["end_time"] = datetime.now()
        self.stats["duration_seconds"] = (
            self.stats["end_time"] - self.stats["start_time"]
        ).total_seconds()
        
        result.stats = self.stats
        return result
    
    def run(self) -> Dict[str, List[str]]:
        """Run the retriever and return URLs in scraper-compatible format."""
        logger.info(f"Starting RSS preprint retrieval for {len(self.queries)} queries")
        
        result = self.search_preprints()
        
        # Log summary
        logger.info(
            f"RSS retrieval complete: {self.stats['successful_queries']}/{self.stats['total_queries']} "
            f"queries successful, {self.stats['total_papers_found']} papers found in "
            f"{self.stats['duration_seconds']:.1f} seconds"
        )
        
        if self.stats["successful_queries"] == 0:
            raise PreprintRetrieverError(
                f"All {self.stats['total_queries']} queries failed. Errors: {result.errors}"
            )
        
        return result.urls
    
    def run_with_metadata(self) -> RetrievalResult:
        """Run the retriever and return full results with metadata."""
        logger.info(f"Starting RSS preprint retrieval for {len(self.queries)} queries")
        return self.search_preprints()


# Example usage
def main():
    queries = [
        "CRISPR gene editing",
        "machine learning drug discovery",
        "COVID-19 vaccine efficacy"
    ]
    
    try:
        retriever = RSSPreprintRetriever(
            queries=queries,
            ppq=3,                    # Papers per query
            timeout=15,               # RSS fetch timeout
            search_mode='any'         # Match any word in query
        )
        
        # Get URLs in scraper format
        subjects = retriever.run()
        
        print("\nRetrieved URLs in scraper format:")
        for query, url_list in subjects.items():
            print(f"\n'{query}': [")
            for i, url in enumerate(url_list):
                site = 'MedRxiv' if 'medrxiv.org' in url else 'BioRxiv'
                comma = "," if i < len(url_list) - 1 else ""
                print(f"    '{url}'{comma}  # {site}")
            print("],")
        
        print(f"\n# Ready for existing scrapers:")
        print(f"# scraper = AsyncMedRxivScraper(subjects=subjects)")
        print(f"# papers = await scraper.run()")
        
        # Show detailed stats
        result = retriever.run_with_metadata()
        print(f"\nDetailed Stats:")
        print(f"  Total papers found: {result.stats['total_papers_found']}")
        print(f"  MedRxiv papers: {result.stats['medrxiv_papers']}")
        print(f"  BioRxiv papers: {result.stats['biorxiv_papers']}")
        print(f"  Feeds processed: {result.stats['total_feeds_processed']}")
        print(f"  Duration: {result.stats['duration_seconds']:.1f} seconds")
        print(f"  Success rate: {result.stats['successful_queries']}/{result.stats['total_queries']}")
        
        if result.errors:
            print(f"\nErrors: {result.errors}")
        
    except PreprintRetrieverError as e:
        logger.error(f"Retrieval failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()