#!/usr/bin/env python3
"""
Simple MedRxiv Scraper - Subject-based with Full Text

Usage: asyncio.run(scraper.run())

Output: 
- JSON output with metadata and paper content
- JSON file with metadata and paper content (medrxiv_papers.json) -commented-out
- Markdown file for each paper (medrxiv_markdown/) -commented-out
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
class MedPaper:
    doi: str
    title: str = ""
    authors: List[str] = field(default_factory=list)
    published: str = ""
    abstract: str = ""
    content: str = ""
    method: str = ""
    subject: str = ""
    pdf_url: str = ""
    error: str = ""
    
    def to_markdown(self) -> str:
        if self.error: return f"# Error: {self.doi}\n{self.error}"
        return f"""# {self.title}
**Authors:** {', '.join(self.authors)}
**DOI:** {self.doi} | **Published:** {self.published}
**Subject:** {self.subject} | **Method:** {self.method}

## Abstract
{self.abstract or "N/A"}

## Content
{self.content or "N/A"}"""

class AsyncMedRxivScraper:
    def __init__(self, subjects: Dict[str, List[str]], output: str = "medrxiv_papers.json", 
                 concurrent: int = 5, timeout: int = 30):
        self.subjects = subjects
        self.output = output
        self.concurrent = concurrent
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.stats = {'total': sum(len(v) for v in subjects.values()), 'success': 0, 'api': 0, 'pdf': 0}
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.papers = []
    
    async def fetch(self, session: aiohttp.ClientSession, url: str) -> Optional[bytes]:
        try:
            await asyncio.sleep(0.3)  # Rate limiting
            async with session.get(url) as r:
                return await r.read() if r.status == 200 else None
        except: return None
    
    async def fetch_json(self, session: aiohttp.ClientSession, url: str) -> Optional[Dict]:
        content = await self.fetch(session, url)
        return json.loads(content.decode('utf-8')) if content else None
    
    def parse_api_paper(self, data: Dict, subject: str) -> MedPaper:
        try:
            doi = data.get('doi', '')
            title = data.get('title', '')
            abstract = data.get('abstract', '')
            published = data.get('date', '')
            
            # Parse authors
            authors = []
            if 'authors' in data:
                authors_data = data['authors']
                if isinstance(authors_data, str):
                    authors = [name.strip() for name in authors_data.split(',')]
                elif isinstance(authors_data, list):
                    for author in authors_data:
                        name = author.get('author_name', '') if isinstance(author, dict) else str(author)
                        if name: authors.append(name)
            
            pdf_url = f"https://www.medrxiv.org/content/10.1101/{doi.split('/')[-1]}v1.full.pdf"
            
            return MedPaper(
                doi=doi, title=title, authors=authors, published=published,
                abstract=abstract, method="API", subject=subject, pdf_url=pdf_url
            )
        except Exception as e:
            return MedPaper(doi=data.get('doi', 'unknown'), subject=subject, error=f"Parse failed: {e}")
    
    def parse_pdf(self, pdf_bytes: bytes) -> str:
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = '\n'.join(page.get_text() for page in doc)
            doc.close()
            
            lines = text.split('\n')
            content = []
            for line in lines:
                line = line.strip()
                if line and len(line) > 3 and not re.match(r'^\d+$|^medRxiv|^doi:|^NOTE:', line):
                    if len(line) < 100 and any(kw in line.lower() for kw in 
                        ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion']):
                        content.append(f"\n## {line}\n")
                    else:
                        content.append(line)
            
            return '\n'.join(content)
        except Exception as e:
            logger.debug(f"PDF parsing failed: {e}")
            return ""
    
    async def scrape_subject(self, session: aiohttp.ClientSession, subject: str, 
                           num_papers: int, sem: asyncio.Semaphore) -> List[MedPaper]:
        async with sem:
            papers = []
            cursor = 0
            
            # Use date range instead of "30d" format - get recent papers
            from datetime import datetime, timedelta
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            while len(papers) < num_papers:
                url = f"https://api.medrxiv.org/details/medrxiv/{start_date}/{end_date}/{cursor}/json"
                
                logger.info(f"Fetching papers for {subject} (cursor: {cursor}, dates: {start_date} to {end_date})")
                data = await self.fetch_json(session, url)
                
                if not data or 'collection' not in data or not data['collection']:
                    logger.warning(f"No more papers available for {subject} at cursor {cursor}")
                    break
                
                # Process papers from this batch
                batch_count = 0
                for paper_data in data['collection']:
                    if len(papers) >= num_papers:
                        break
                    
                    paper = self.parse_api_paper(paper_data, subject)
                    
                    # Download PDF and extract content
                    if paper.pdf_url and not paper.error:
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
                    
                    papers.append(paper)
                    batch_count += 1
                
                logger.info(f"Got {batch_count} papers from this batch")
                cursor += 100  # Move to next page
                
                # Safety break
                if cursor > 500:
                    logger.warning(f"Reached cursor limit for {subject}")
                    break
            
            self.stats['api'] += len(papers)
            logger.info(f"Completed {subject}: {len(papers)} papers")
            return papers
    
    async def run(self) -> Dict:
        start = time.time()
        logger.info(f"Processing {self.stats['total']} papers across {len(self.subjects)} subjects")
        
        sem = asyncio.Semaphore(self.concurrent)
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            tasks = [self.scrape_subject(session, subject, len(papers), sem) 
                    for subject, papers in self.subjects.items()]
            
            self.papers = []
            for i, coro in enumerate(asyncio.as_completed(tasks)):
                subject_papers = await coro
                self.papers.extend(subject_papers)
                self.stats['success'] += len([p for p in subject_papers if not p.error])
                logger.info(f"[{i+1}/{len(self.subjects)}] Completed subject batch")
        
        # Create output
        output = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "total": len(self.papers),
                "success": self.stats['success'],
                "success_rate": round(self.stats['success']/len(self.papers)*100, 2) if self.papers else 0,
                "methods": {"api": self.stats['api'], "pdf": self.stats['pdf']},
                "elapsed_seconds": time.time() - start
            },
            "papers": [asdict(p) for p in self.papers]
        }
        
        # Save JSON
        # with open(self.output, 'w', encoding='utf-8') as f:
        #     json.dump(output, f, indent=2, ensure_ascii=False)
        
        # Save markdown files
        # md_dir = Path("medrxiv_markdown")
        # md_dir.mkdir(exist_ok=True)
        # for p in self.papers:
        #     if not p.error:
        #         safe_title = re.sub(r'[^\w\s-]', '', p.title)[:30]
        #         (md_dir / f"{p.doi.replace('/', '_')}_{safe_title}.md").write_text(p.to_markdown())
        
        logger.info(f"Complete! Success: {self.stats['success']}/{len(self.papers)}, "
                   f"Time: {output['metadata']['elapsed_seconds']:.1f}s")
        self.executor.shutdown(wait=False)
        return output


def main():
    # Example subjects with paper counts (like your ArXiv scraper format)
    subjects = {
        "CRISPR gene editing": [
            "http://medrxiv.org/cgi/content/short/2025.06.05.25329036v1?rss=1",
            "http://medrxiv.org/cgi/content/short/2025.06.04.25328999v1?rss=1",
            "http://medrxiv.org/cgi/content/short/2025.06.05.25329058v1?rss=1"
        ],
        "machine learning drug discovery": [
            "http://medrxiv.org/cgi/content/short/2025.06.04.25329015v1?rss=1"
        ],
        "COVID-19 vaccine efficacy": [
            "http://medrxiv.org/cgi/content/short/2025.06.05.25329097v1?rss=1"
    ]
    }
    
    # Initialize and run scraper
    scraper = AsyncMedRxivScraper(subjects=subjects)
    output = asyncio.run(scraper.run())
    
    # Print results
    print(f"Total papers: {output['metadata']['total']}")
    print(f"Success: {output['metadata']['success']}")
    print(f"Time: {output['metadata']['elapsed_seconds']:.1f}s")

if __name__ == "__main__":
    main()