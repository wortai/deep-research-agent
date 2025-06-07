#!/usr/bin/env python3
"""
Async ArXiv Scraper - HTML5 with PDF fallback

Usage:asyncio.run(scraper.run())

Output: 
- JSON file with metadata and paper content (arxiv_papers.json)
- Markdown files for each paper (Markdown Folder)
- Stats and timing information
"""

import re, json, asyncio, aiohttp, fitz, logging, time
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict, field
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Paper:
    arxiv_id: str
    title: str = ""
    authors: List[str] = field(default_factory=list)
    published: str = ""
    abstract: str = ""
    content: str = ""
    method: str = ""
    query: str = ""
    url: str = ""
    error: str = ""
    
    def to_markdown(self) -> str:
        if self.error: return f"# Error: {self.arxiv_id}\n{self.error}"
        return f"""# {self.title}
**Authors:** {', '.join(self.authors)}
**ArXiv:** {self.arxiv_id} | **Published:** {self.published}
**Query:** {self.query} | **Method:** {self.method}

## Abstract
{self.abstract or "N/A"}

## Content
{self.content or "N/A"}"""

class AsyncArxivScraper:
    def __init__(self, urls: Dict[str, List[str]], output: str = "arxiv_papers.json",
                 concurrent: int = 10, timeout: int = 30):
        self.urls = urls
        self.output = output
        self.concurrent = concurrent
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.stats = {'total': sum(len(v) for v in urls.values()), 'success': 0, 
                      'html': 0, 'pdf': 0}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.papers = []
    
    async def fetch(self, session: aiohttp.ClientSession, url: str) -> Optional[bytes]:
        try:
            async with session.get(url) as r:
                return await r.read() if r.status == 200 else None
        except: return None
    
    def extract_id(self, url: str) -> str:
        match = re.search(r'arxiv\.org/(?:abs|pdf)/(\d+\.\d+)', url)
        return match.group(1) if match else url.split("/")[-1].replace('.pdf', '')
    
    def parse_html(self, soup: BeautifulSoup) -> Dict:
        get_text = lambda elem: elem.get_text(strip=True) if elem else ""
        
        # Title
        title = get_text(soup.find('h1', class_='ltx_title')) or \
                soup.find('meta', attrs={'name': 'title'})['content'].strip()
        
        # Authors
        authors = []
        for elem in soup.find_all('span', class_='ltx_personname'):
            name = re.sub(r'\s*\([^)]*\)|[a-zA-Z0-9._%+-]+@[^@]+|[\*&]|\s+', ' ', 
                         get_text(elem)).strip()
            if name and len(name) > 1: authors.append(name)
        
        # Abstract
        abstract = ""
        if abs_elem := soup.find('div', class_='ltx_abstract'):
            abstract = re.sub(r'^Abstract\s*', '', get_text(abs_elem), flags=re.I)
        
        # Content
        content = []
        for section in soup.find_all(['section', 'div'], class_=re.compile(r'ltx_section')):
            if h := section.find(re.compile(r'^h[1-6]'), class_=re.compile(r'ltx_title')):
                level = int(h.name[1]) if h.name[0] == 'h' else 2
                content.append(f"\n{'#' * level} {get_text(h)}\n")
            for p in section.find_all('p'):
                if text := get_text(p):
                    content.append(f"{text}\n")
        
        # Date
        date = ""
        if date_elem := soup.find('meta', attrs={'name': 'citation_date'}):
            date = date_elem.get('content', '')
        
        return {'title': title, 'authors': authors, 'abstract': abstract,
                'content': '\n'.join(content), 'published': date}
    
    def parse_pdf(self, pdf_bytes: bytes) -> Dict:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = '\n'.join(page.get_text() for page in doc)
        doc.close()
        
        lines = text.split('\n')
        title = next((l.strip() for l in lines[:10] 
                     if len(l) > 10 and not l.isupper() and 'arXiv:' not in l), "")
        
        authors = [l.strip() for l in lines[:20] 
                  if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+$', l.strip())][:5]
        
        abstract_match = re.search(r'Abstract\s*\n\s*(.*?)(?:\n\s*\n|\n\s*1\s+Introduction)',
                                  text, re.DOTALL | re.I)
        abstract = re.sub(r'\s+', ' ', abstract_match.group(1)) if abstract_match else ""
        
        # Clean content
        content = []
        for line in lines:
            line = line.strip()
            if line and len(line) > 3 and not line.isdigit() and 'arXiv:' not in line:
                if len(line) < 100 and not line[-1] in '.,' and line[0].isupper():
                    content.append(f"\n## {line}\n")
                else:
                    content.append(line)
        
        return {'title': title, 'authors': authors, 'abstract': abstract,
                'content': '\n'.join(content), 'published': "Unknown"}
    
    async def scrape_paper(self, session: aiohttp.ClientSession, url: str, 
                          query: str, sem: asyncio.Semaphore) -> Paper:
        async with sem:
            arxiv_id = self.extract_id(url)
            
            # Try HTML first
            if html := await self.fetch(session, f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}"):
                try:
                    data = self.parse_html(BeautifulSoup(html, 'html.parser'))
                    self.stats['html'] += 1
                    return Paper(arxiv_id=arxiv_id, method="HTML5", query=query, 
                               url=url, **data)
                except Exception as e:
                    logger.debug(f"HTML failed for {arxiv_id}: {e}")
            
            # Fallback to PDF
            if pdf := await self.fetch(session, f"https://arxiv.org/pdf/{arxiv_id}.pdf"):
                try:
                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(self.executor, self.parse_pdf, pdf)
                    self.stats['pdf'] += 1
                    return Paper(arxiv_id=arxiv_id, method="PDF", query=query, 
                               url=url, **data)
                except Exception as e:
                    logger.debug(f"PDF failed for {arxiv_id}: {e}")
            
            return Paper(arxiv_id=arxiv_id, query=query, url=url, 
                        error="Both HTML and PDF extraction failed")
    
    async def run(self) -> Dict:
        start = time.time()
        logger.info(f"Processing {self.stats['total']} papers (max {self.concurrent} concurrent)")
        
        sem = asyncio.Semaphore(self.concurrent)
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            tasks = [self.scrape_paper(session, url, query, sem) 
                    for query, urls in self.urls.items() for url in urls]
            
            self.papers = []
            for i, coro in enumerate(asyncio.as_completed(tasks)):
                paper = await coro
                self.papers.append(paper)
                self.stats['success'] += not bool(paper.error)
                logger.info(f"[{i+1}/{self.stats['total']}] {'✓' if not paper.error else '✗'} {paper.arxiv_id}")
        
        # Create output
        output = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "total": self.stats['total'],
                "success": self.stats['success'],
                "success_rate": round(self.stats['success']/self.stats['total']*100, 2),
                "methods": {"html": self.stats['html'], "pdf": self.stats['pdf']},
                "elapsed_seconds": time.time() - start
            },
            "papers": [asdict(p) for p in self.papers]
        }
        
        # Save JSON
        with open(self.output, 'w') as f:
            json.dump(output, f, indent=2)
        
        # Save markdown files
        md_dir = Path("arxiv_markdown")
        md_dir.mkdir(exist_ok=True)
        for p in self.papers:
            if not p.error:
                safe_title = re.sub(r'[^\w\s-]', '', p.title)[:30]
                (md_dir / f"{p.arxiv_id}_{safe_title}.md").write_text(p.to_markdown())
        
        logger.info(f"Complete! Success: {self.stats['success']}/{self.stats['total']}, Time: {output['metadata']['elapsed_seconds']:.1f}s")
        self.executor.shutdown(wait=False)
        return output


# Main function
def main():
    # Example URLs for testing
    urls = {
        'Low Rank Adaptation of Large Language Models': [
            'https://arxiv.org/abs/2106.09685',
            'https://arxiv.org/abs/2305.14314'
        ],
        'Transformer Architecture': [
            'https://arxiv.org/abs/1706.03762'
        ]
    }
    
    # Initialize and run async scraper
    scraper = AsyncArxivScraper(
        urls=urls,
    )
    
    # Run the async scraper
    output = asyncio.run(scraper.run())
    # print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()