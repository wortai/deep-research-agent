#!/usr/bin/env python3
"""
Simple BioRxiv Scraper - URL-based with Full Text

Usage: asyncio.run(scraper.run())

Output: 
- JSON output with metadata and paper content
- JSON file with metadata and paper content (biorxiv_papers.json) -commented-out
- Markdown file for each paper (biorxiv_markdown/) -commented-out
"""

import re, json, asyncio, aiohttp, fitz, logging, time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class BioPaper:
    doi: str
    title: str = ""
    authors: List[str] = field(default_factory=list)
    published: str = ""
    abstract: str = ""
    content: str = ""
    method: str = ""
    subject: str = ""
    pdf_url: str = ""
    web_url: str = ""
    error: str = ""
    
    def to_markdown(self) -> str:
        if self.error: return f"# Error: {self.doi}\n{self.error}"
        return f"""# {self.title}
**Authors:** {', '.join(self.authors)}
**DOI:** {self.doi} | **Published:** {self.published}
**Subject:** {self.subject} | **Method:** {self.method}

**PDF URL:** {self.pdf_url}
**Web URL:** {self.web_url}

## Abstract
{self.abstract or "N/A"}

## Content
{self.content or "N/A"}"""

class AsyncBioRxivScraper:
    def __init__(self, subjects: Dict[str, List[str]], output: str = "biorxiv_papers.json", 
                 concurrent: int = 5, timeout: int = 30):
        self.subjects = subjects
        self.output = output
        self.concurrent = concurrent
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.stats = {'total': sum(len(v) for v in subjects.values()), 'success': 0, 'web': 0, 'pdf': 0}
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.papers = []
    
    def extract_doi_from_url(self, url: str) -> str:
        """Extract DOI from bioRxiv URL"""
        try:
            # Extract DOI pattern from URL
            doi_match = re.search(r'10\.1101/[\d.]+', url)
            if doi_match:
                return doi_match.group()
            # Fallback pattern
            content_match = re.search(r'/content/(.+?)(?:v\d+)?(?:\?|$)', url)
            if content_match:
                return content_match.group(1)
            return f"unknown_{hash(url)}"
        except:
            return f"unknown_{hash(url)}"
    
    def construct_pdf_url(self, web_url: str, doi: str) -> str:
        """Construct PDF URL from web URL"""
        try:
            # Method 1: Direct PDF URL from DOI
            clean_doi = doi.replace('10.1101/', '')
            return f"https://www.biorxiv.org/content/10.1101/{clean_doi}.full.pdf"
        except:
            return ""
    
    async def fetch(self, session: aiohttp.ClientSession, url: str) -> Optional[bytes]:
        try:
            await asyncio.sleep(0.3)  # Rate limiting
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; Academic Research Bot)'}
            async with session.get(url, headers=headers) as r:
                return await r.read() if r.status == 200 else None
        except: 
            return None
    
    async def fetch_text(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        content = await self.fetch(session, url)
        if content:
            try:
                return content.decode('utf-8')
            except:
                try:
                    return content.decode('latin-1')
                except:
                    return None
        return None
    
    def parse_web_page(self, html: str, url: str, subject: str) -> BioPaper:
        """Parse bioRxiv web page to extract metadata"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            doi = self.extract_doi_from_url(url)
            
            # Extract title
            title_elem = (soup.find('h1', {'id': 'page-title'}) or 
                         soup.find('h1', class_='highwire-cite-title') or
                         soup.find('h1'))
            title = title_elem.get_text(strip=True) if title_elem else "Title not found"
            
            # Extract authors - simplified approach
            authors = []
            author_metas = soup.find_all('meta', {'name': 'DC.Creator'})
            for meta in author_metas:
                author_name = meta.get('content', '').strip()
                if author_name:
                    authors.append(author_name)
            
            # If no authors from meta tags, try other selectors
            if not authors:
                author_elems = soup.select('span.nlm-given-names, span.nlm-surname')
                temp_authors = []
                for elem in author_elems:
                    temp_authors.append(elem.get_text(strip=True))
                # Combine given names and surnames
                for i in range(0, len(temp_authors), 2):
                    if i + 1 < len(temp_authors):
                        full_name = f"{temp_authors[i]} {temp_authors[i+1]}"
                        authors.append(full_name)
            
            # Extract abstract
            abstract = ""
            abstract_elem = soup.find('div', class_='section abstract') or soup.find('div', id='abstract')
            if abstract_elem:
                abstract_text = abstract_elem.get_text(strip=True)
                abstract = re.sub(r'^Abstract\s*', '', abstract_text, flags=re.IGNORECASE)
            
            # Extract publication date
            pub_date = ""
            date_elem = soup.find('meta', {'name': 'DC.Date'})
            if date_elem:
                pub_date = date_elem.get('content', '')
            
            # Construct PDF URL
            pdf_url = self.construct_pdf_url(url, doi)
            
            return BioPaper(
                doi=doi, title=title, authors=authors, published=pub_date,
                abstract=abstract, method="WEB", subject=subject,
                pdf_url=pdf_url, web_url=url
            )
            
        except Exception as e:
            return BioPaper(doi=self.extract_doi_from_url(url), subject=subject, 
                          web_url=url, error=f"Web parse failed: {e}")
    
    def parse_pdf(self, pdf_bytes: bytes) -> str:
        """Parse PDF content - simplified like medRxiv"""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = '\n'.join(page.get_text() for page in doc)
            doc.close()
            
            lines = text.split('\n')
            content = []
            for line in lines:
                line = line.strip()
                if line and len(line) > 3 and not re.match(r'^\d+$|^bioRxiv|^doi:|^www\.biorxiv', line):
                    if len(line) < 100 and any(kw in line.lower() for kw in 
                        ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion']):
                        content.append(f"\n## {line}\n")
                    else:
                        content.append(line)
            
            return '\n'.join(content)
        except Exception as e:
            logger.debug(f"PDF parsing failed: {e}")
            return ""
    
    async def scrape_paper(self, session: aiohttp.ClientSession, url: str, subject: str, 
                          sem: asyncio.Semaphore) -> BioPaper:
        """Scrape a single paper from URL - simplified approach"""
        async with sem:
            try:
                logger.info(f"Scraping: {url}")
                
                # Get web page
                html = await self.fetch_text(session, url)
                if not html:
                    return BioPaper(doi=self.extract_doi_from_url(url), subject=subject, 
                                  web_url=url, error="Could not fetch web page")
                
                # Parse web page
                paper = self.parse_web_page(html, url, subject)
                self.stats['web'] += 1
                
                if paper.error:
                    return paper
                
                # Download PDF and extract content
                if paper.pdf_url:
                    logger.info(f"Downloading PDF for: {paper.title[:50]}...")
                    pdf_content = await self.fetch(session, paper.pdf_url)
                    if pdf_content:
                        loop = asyncio.get_event_loop()
                        text = await loop.run_in_executor(self.executor, self.parse_pdf, pdf_content)
                        if text:
                            paper.content = text
                            self.stats['pdf'] += 1
                            logger.info(f"✓ Extracted {len(text)} chars from {paper.doi}")
                        else:
                            logger.warning(f"✗ PDF text extraction failed for {paper.doi}")
                    else:
                        logger.warning(f"✗ PDF download failed for {paper.doi}")
                
                self.stats['success'] += 1
                return paper
                
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                return BioPaper(doi=self.extract_doi_from_url(url), subject=subject, 
                              web_url=url, error=f"Scraping failed: {e}")
    
    async def run(self) -> Dict:
        """Run the scraping process - simplified like medRxiv"""
        start = time.time()
        logger.info(f"Processing {self.stats['total']} papers across {len(self.subjects)} subjects")
        
        sem = asyncio.Semaphore(self.concurrent)
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            tasks = []
            
            # Create tasks for all URLs
            for subject, urls in self.subjects.items():
                for url in urls:
                    task = self.scrape_paper(session, url, subject, sem)
                    tasks.append(task)
            
            # Execute tasks
            self.papers = []
            for i, coro in enumerate(asyncio.as_completed(tasks)):
                paper = await coro
                self.papers.append(paper)
                logger.info(f"[{i+1}/{len(tasks)}] Completed paper")
        
        # Create output
        output = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "total": len(self.papers),
                "success": self.stats['success'],
                "success_rate": round(self.stats['success']/len(self.papers)*100, 2) if self.papers else 0,
                "methods": {"web": self.stats['web'], "pdf": self.stats['pdf']},
                "elapsed_seconds": time.time() - start
            },
            "papers": [asdict(p) for p in self.papers]
        }
        
        # Save JSON (commented out like medRxiv)
        # with open(self.output, 'w', encoding='utf-8') as f:
        #     json.dump(output, f, indent=2, ensure_ascii=False)
        
        # Save markdown files (commented out like medRxiv)
        # md_dir = Path("biorxiv_markdown")
        # md_dir.mkdir(exist_ok=True)
        # for p in self.papers:
        #     if not p.error:
        #         safe_title = re.sub(r'[^\w\s-]', '', p.title)[:30]
        #         safe_title = re.sub(r'\s+', '_', safe_title)
        #         filename = f"{p.doi.replace('/', '_')}_{safe_title}.md"
        #         (md_dir / filename).write_text(p.to_markdown(), encoding='utf-8')
        
        logger.info(f"Complete! Success: {self.stats['success']}/{len(self.papers)}, "
                   f"Time: {output['metadata']['elapsed_seconds']:.1f}s")
        self.executor.shutdown(wait=False)
        return output


def main():
    """Test with specific bioRxiv URLs - matching medRxiv format"""
    # Example subjects with actual bioRxiv URLs (like your medRxiv format)
    subjects = {
        'Ecology': [
            'https://www.biorxiv.org/content/10.1101/2025.01.30.634607v2', 
            'https://www.biorxiv.org/content/10.1101/2024.12.20.629406v2'
        ],
        'Cancer Biology': [
            'https://www.biorxiv.org/content/10.1101/2025.06.06.658155v1'
        ],
        'Neuroscience': [
            'https://www.biorxiv.org/content/10.1101/2024.12.19.629234v1'
        ]
    }
    
    # Initialize and run scraper
    scraper = AsyncBioRxivScraper(subjects=subjects)
    output = asyncio.run(scraper.run())
    
    # Print results (same format as medRxiv)
    print(f"Total papers: {output['metadata']['total']}")
    print(f"Success: {output['metadata']['success']}")
    print(f"Time: {output['metadata']['elapsed_seconds']:.1f}s")
    
    # Show sample paper details
    if output['papers']:
        print(f"\nSample papers:")
        for i, paper in enumerate(output['papers'][:3], 1):
            print(f"\n{i}. {paper['title'][:60]}...")
            print(f"   DOI: {paper['doi']}")
            print(f"   Subject: {paper['subject']}")
            print(f"   Authors: {', '.join(paper['authors'][:2])}{'...' if len(paper['authors']) > 2 else ''}")
            print(f"   Content length: {len(paper['content'])} chars")
            print(f"   Error: {paper['error'] if paper['error'] else 'None'}")


if __name__ == "__main__":
    # Install beautifulsoup4 if needed
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("Installing beautifulsoup4...")
        import subprocess
        subprocess.run(["pip", "install", "beautifulsoup4"])
        from bs4 import BeautifulSoup
    
    main()