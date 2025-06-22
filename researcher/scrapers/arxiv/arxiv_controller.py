
# Scrapers and Retrievers Modules Import
from retrievers.arxiv import ArxivRetriever
from scrapers.arxiv import AsyncArxivScraper
from retrievers.research_rssharvest import RSSPreprintRetriever
from scrapers.medrxiv import AsyncMedRxivScraper
from scrapers.biorxiv import AsyncBioRxivScraper

import traceback
import asyncio
from typing import List, Dict, Any

class ResearchSearch:
    @staticmethod
    def arxiv(queries: List[str], papers_per_query: int = 5) -> Dict[str, Any]:
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
            error_details = traceback.format_exc()
            print(f"Error in arxiv_tool: {error_details}")
            return {
                "status": "error",
                "error": str(e),
                "error_details": error_details,
                "data": None
            }

    @staticmethod
    def medrxiv_biorxiv(queries: List[str], papers_per_query: int = 3, search_mode: str = 'any') -> Dict[str, Any]:
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
            error_details = traceback.format_exc()
            print(f"Error in medrxiv_biorxiv_tool: {error_details}")
            return {
                "status": "error",
                "error": str(e),
                "error_details": error_details,
                "data": None
            }


def main():
    """
    Main function to demonstrate the usage of ResearchSearch class.
    """
    print("--- Testing ArXiv Search ---")
    arxiv_queries = ["large language models", "quantum computing"]
    arxiv_results = ResearchSearch.arxiv(queries=arxiv_queries, papers_per_query=1)
    # print(f"ArXiv Results: {arxiv_results['data']['papers']}")
    for i , paper in enumerate(arxiv_results['data']['papers']):
        print(paper['arxiv_id'])





    # print("\n--- Testing medRxiv/bioRxiv Search ---")
    # medbio_queries = ["CRISPR", "cancer immunotherapy"]
    # medbio_results = ResearchSearch.medrxiv_biorxiv(queries=medbio_queries, papers_per_query=1)
    # print(f"medRxiv/bioRxiv Results: {medbio_results['Results']}")

if __name__ == "__main__":
    main()