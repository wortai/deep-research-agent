"""
Tools:

1. Arxiv Tool
2. Medrxiv Tool
3. BioRxiv Tool

"""
from langchain_core.tools import tool
from typing import List, Dict, Any
import asyncio
import json
from datetime import datetime
import os

# Scrapers and Retrievers Modules Import
from researcher.retrievers.arxiv import ArxivRetriever
from researcher.scrapers.arxiv import AsyncArxivScraper
from researcher.retrievers.research_rssharvest import RSSPreprintRetriever
from researcher.scrapers.medrxiv import AsyncMedRxivScraper
from researcher.scrapers.biorxiv import AsyncBioRxivScraper


# Arxiv Tool: Input = List of Queries, Output = Returns papers in JSON format
@tool
def arxiv_tool(queries: List[str], papers_per_query: int = 5) -> Dict[str, Any]:
    """
    Search and scrape ArXiv papers based on queries.
    
    Args:
        queries: List of search queries for ArXiv papers
        papers_per_query: Number of papers to retrieve per query (default: 5)
    
    Returns:
        Dictionary containing scraped paper data organized by query
    """
    try:
        # Initialize retriever
        retriever = ArxivRetriever(queries, ppq=papers_per_query, max_retries=3)
        retrieved_urls = retriever.run()
        
        # Initialize scraper
        scraper = AsyncArxivScraper(urls=retrieved_urls)
        
        # Run scraper
        output = asyncio.run(scraper.run())
        
        return {
            "status": "success",
            "data": output,
            "queries_processed": len(queries),
            "total_papers": sum(len(urls) for urls in retrieved_urls.values())
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "data": None
        }


@tool
def medrxiv_biorxiv_tool(queries: List[str], papers_per_query: int = 3, search_mode: str = 'any') -> Dict[str, Any]:
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
        # Initialize retriever
        retriever = RSSPreprintRetriever(
            queries=queries, 
            ppq=papers_per_query, 
            timeout=15,
            search_mode=search_mode
        )
        
        # Get URLs in the format your scrapers expect
        retrieved_urls = retriever.run()
        
        # Separate medRxiv and bioRxiv URLs
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
        
        # Initialize combined results
        all_papers_by_query = {}
        medrxiv_paper_count = 0
        biorxiv_paper_count = 0
        
        # Scrape medRxiv papers
        if medrxiv_subjects:
            print(f"🔬 Scraping medRxiv papers for {len(medrxiv_subjects)} subjects...")
            medrxiv_scraper = AsyncMedRxivScraper(subjects=medrxiv_subjects)
            medrxiv_results = asyncio.run(medrxiv_scraper.run())
            
            # Extract papers from medRxiv scraper output
            if isinstance(medrxiv_results, dict) and 'papers' in medrxiv_results:
                for paper in medrxiv_results['papers']:
                    if isinstance(paper, dict):
                        # Add source identifier
                        paper['source'] = 'medrxiv'
                        
                        # Get the subject/query this paper belongs to
                        subject = paper.get('subject', 'Unknown')
                        
                        # Initialize query list if not exists
                        if subject not in all_papers_by_query:
                            all_papers_by_query[subject] = []
                        
                        all_papers_by_query[subject].append(paper)
                        medrxiv_paper_count += 1
        
        # Scrape bioRxiv papers  
        if biorxiv_subjects:
            print(f"🧬 Scraping bioRxiv papers for {len(biorxiv_subjects)} subjects...")
            biorxiv_scraper = AsyncBioRxivScraper(subjects=biorxiv_subjects)
            biorxiv_results = asyncio.run(biorxiv_scraper.run())
            
            # Extract papers from bioRxiv scraper output
            if isinstance(biorxiv_results, dict) and 'papers' in biorxiv_results:
                for paper in biorxiv_results['papers']:
                    if isinstance(paper, dict):
                        # Add source identifier
                        paper['source'] = 'biorxiv'
                        
                        # Get the subject/query this paper belongs to
                        subject = paper.get('subject', 'Unknown')
                        
                        # Initialize query list if not exists
                        if subject not in all_papers_by_query:
                            all_papers_by_query[subject] = []
                        
                        all_papers_by_query[subject].append(paper)
                        biorxiv_paper_count += 1
        
        # Calculate totals
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
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in medrxiv_biorxiv_tool: {error_details}")
        return {
            "status": "error",
            "error": str(e),
            "error_details": error_details,
            "data": None
        }


# ----------- ArXiv Tool Test --------------
def test_arxiv_tool():
    print("Testing ArXiv Search Tool...")
    
    # Test with a simple query
    result = arxiv_tool.invoke({
        "queries": ["low rank adaptation in large language models", "attention mechanism of transformers"],
        "papers_per_query": 2
    })
    
    print(f"Status: {result['status']}")
    
    if result['status'] == 'success':
        print(f"✅ Success! Found {result['total_papers']} papers")
        
        # # Save the Output to a json file START -- FOR OUTPUT OBSERVATION (Testing only)
        # output_dir = "output"
        # os.makedirs(output_dir, exist_ok=True)
        
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # filename = f"arxiv_papers_{timestamp}.json"
        # filepath = os.path.join(output_dir, filename)
        
        # with open(filepath, 'w', encoding='utf-8') as f:
        #     json.dump(result['data'], f, indent=2, ensure_ascii=False)
        # print(f"📄 Results saved to: {filepath}")
        
        print(f"Processed {result['queries_processed']} queries")
    else:
        print(f"❌ Error: {result['error']}")
    

# ----------- Biorxiv + Medrxiv Tool Test --------------
def test_medrxiv_biorxiv_tool():
    """Test the Biorxiv+Medrxiv tool with sample queries"""
    test_queries = ["COVID-19 vaccine immunology",
    "cancer immunotherapy mechanisms",
    "single cell RNA sequencing clinical",
    "Short-term management of kelp forests for marine heatwaves requires planning"]
    
    print("🧬 Testing Combined Tool")
    print("=" * 30)
    
    result = medrxiv_biorxiv_tool.invoke({
        "queries": test_queries,
        "papers_per_query": 2,
        "search_mode": "any"
    })
    
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Total papers: {result['total_papers']}")
        print(f"medRxiv papers: {result.get('medrxiv_papers', 0)}")
        print(f"bioRxiv papers: {result.get('biorxiv_papers', 0)}")
    else:
        print(f"Error: {result['error']}")


if __name__ == "__main__":
    test_arxiv_tool()
    test_medrxiv_biorxiv_tool()