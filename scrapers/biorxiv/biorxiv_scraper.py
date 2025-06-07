#!/usr/bin/env python3
"""
Simple BioRxiv Scraper - Subject-based with Full Text

Usage: asyncio.run(scraper.run())

Output: 
- JSON file with metadata and paper content (biorxiv_papers.json)
- Markdown files for each paper (biorxiv_markdown/)
"""

import re, json, asyncio, aiohttp, fitz, logging, time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from datetime import datetime, timedelta
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
    category: str = ""
    pdf_url: str = ""
    web_url: str = ""
    version: str = ""
    error: str = ""
    
    def to_markdown(self) -> str:
        if self.error: return f"# Error: {self.doi}\n{self.error}"
        return f"""# {self.title}
**Authors:** {', '.join(self.authors)}
**DOI:** {self.doi} | **Published:** {self.published} | **Version:** {self.version}
**Subject:** {self.subject} | **Category:** {self.category} | **Method:** {self.method}

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
        self.stats = {'total': sum(len(v) for v in subjects.values()), 'success': 0, 'api': 0, 'pdf': 0}
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.papers = []
        
        # BioRxiv subject categories
        self.bio_subjects = [
            "animal_behavior", "biochemistry", "bioengineering", "bioinformatics", "biophysics",
            "cancer_biology", "cell_biology", "developmental_biology", "ecology", "epidemiology",
            "evolutionary_biology", "genetics", "genomics", "immunology", "microbiology",
            "molecular_biology", "neuroscience", "paleontology", "pathology", "pharmacology",
            "physiology", "plant_biology", "scientific_communication", "synthetic_biology",
            "systems_biology", "zoology"
        ]
    
    async def fetch(self, session: aiohttp.ClientSession, url: str) -> Optional[bytes]:
        try:
            await asyncio.sleep(0.3)  # Rate limiting for bioRxiv
            async with session.get(url) as r:
                return await r.read() if r.status == 200 else None
        except Exception as e:
            logger.debug(f"Fetch failed for {url}: {e}")
            return None
    
    async def fetch_json(self, session: aiohttp.ClientSession, url: str) -> Optional[Dict]:
        content = await self.fetch(session, url)
        if content:
            try:
                return json.loads(content.decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.debug(f"JSON decode failed for {url}: {e}")
        return None
    
    def parse_api_paper(self, data: Dict, subject: str) -> BioPaper:
        try:
            doi = data.get('doi', '')
            title = data.get('title', '')
            abstract = data.get('abstract', '')
            published = data.get('date', '')
            version = data.get('version', '1')
            category = data.get('category', '')
            
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
            
            # Construct URLs for bioRxiv
            pdf_url = f"https://www.biorxiv.org/content/biorxiv/early/{published[:4]}/{published[5:7]}/{published[8:10]}/{doi}.full.pdf"
            web_url = f"https://www.biorxiv.org/content/{doi}v{version}"
            
            return BioPaper(
                doi=doi, title=title, authors=authors, published=published,
                abstract=abstract, method="API", subject=subject, category=category,
                pdf_url=pdf_url, web_url=web_url, version=version
            )
        except Exception as e:
            return BioPaper(doi=data.get('doi', 'unknown'), subject=subject, error=f"Parse failed: {e}")
    
    def parse_pdf(self, pdf_bytes: bytes) -> str:
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = '\n'.join(page.get_text() for page in doc)
            doc.close()
            
            lines = text.split('\n')
            content = []
            for line in lines:
                line = line.strip()
                if line and len(line) > 3:
                    # Skip bioRxiv headers/footers
                    skip_patterns = [
                        r'^\d+$',  # Page numbers
                        r'^bioRxiv preprint',
                        r'^doi: https://doi\.org',
                        r'^copyright holder',
                        r'^was not certified',
                        r'^www\.biorxiv\.org',
                    ]
                    
                    if any(re.match(pattern, line, re.I) for pattern in skip_patterns):
                        continue
                    
                    # Detect biological paper section headers
                    if len(line) < 100 and any(kw in line.lower() for kw in 
                        ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion',
                         'background', 'materials', 'experimental', 'analysis', 'supplementary']):
                        content.append(f"\n## {line}\n")
                    else:
                        content.append(line)
            
            # Clean up final text
            final_text = '\n'.join(content)
            final_text = re.sub(r'\n{3,}', '\n\n', final_text)
            final_text = re.sub(r' {2,}', ' ', final_text)
            
            return final_text
        except Exception as e:
            logger.debug(f"PDF parsing failed: {e}")
            return ""
    
    async def scrape_subject(self, session: aiohttp.ClientSession, subject: str, 
                           num_papers: int, sem: asyncio.Semaphore) -> List[BioPaper]:
        async with sem:
            papers = []
            cursor = 0
            
            # Use date range for recent papers (last 30 days)
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            while len(papers) < num_papers:
                url = f"https://api.biorxiv.org/details/biorxiv/{start_date}/{end_date}/{cursor}/json"
                
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
                            # Try alternative PDF URL format
                            alt_pdf_url = f"https://www.biorxiv.org/content/10.1101/{paper.doi.split('/')[-1]}.full.pdf"
                            logger.info(f"Trying alternative PDF URL...")
                            pdf_content = await self.fetch(session, alt_pdf_url)
                            if pdf_content:
                                loop = asyncio.get_event_loop()
                                text = await loop.run_in_executor(self.executor, self.parse_pdf, pdf_content)
                                if text:
                                    paper.content = text
                                    paper.pdf_url = alt_pdf_url
                                    self.stats['pdf'] += 1
                                    logger.info(f"✓ Extracted {len(text)} chars from {paper.doi} (alt URL)")
                                else:
                                    logger.warning(f"✗ PDF text extraction failed for {paper.doi}")
                            else:
                                logger.warning(f"✗ PDF download failed for {paper.doi} (both URLs)")
                    
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
                "elapsed_seconds": time.time() - start,
                "available_subjects": self.bio_subjects
            },
            "papers": [asdict(p) for p in self.papers]
        }
        
        # Save JSON
        with open(self.output, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        # Save markdown files
        md_dir = Path("biorxiv_markdown")
        md_dir.mkdir(exist_ok=True)
        for p in self.papers:
            if not p.error:
                safe_title = re.sub(r'[^\w\s-]', '', p.title)[:30]
                safe_title = re.sub(r'\s+', '_', safe_title)
                filename = f"{p.doi.replace('/', '_')}_{safe_title}.md"
                (md_dir / filename).write_text(p.to_markdown(), encoding='utf-8')
        
        logger.info(f"Complete! Success: {self.stats['success']}/{len(self.papers)}, "
                   f"Time: {output['metadata']['elapsed_seconds']:.1f}s")
        logger.info(f"Saved {len([p for p in self.papers if not p.error])} markdown files to {md_dir}")
        
        # Print available subjects
        logger.info(f"Available biological subjects: {', '.join(self.bio_subjects[:10])}... and {len(self.bio_subjects)-10} more")
        
        self.executor.shutdown(wait=False)
        return output


def main():
    # Example subjects with paper counts (like your ArXiv scraper format)
    subjects = {
        'Recent Biology Research': ['paper1', 'paper2'],        # Gets 2 recent papers
        'Computational Biology': ['paper1'],                    # Gets 1 recent paper  
        'Neuroscience Studies': ['paper1', 'paper2', 'paper3'] # Gets 3 recent papers
    }
    
    # Initialize and run scraper
    scraper = AsyncBioRxivScraper(subjects=subjects)
    output = asyncio.run(scraper.run())
    
    # Print results
    print(f"Total papers: {output['metadata']['total']}")
    print(f"Success: {output['metadata']['success']}")
    print(f"Time: {output['metadata']['elapsed_seconds']:.1f}s")
    
    # Show available biological subjects
    print("\nAvailable biological subjects for future searches:")
    bio_subjects = output['metadata']['available_subjects']
    for i, subject in enumerate(bio_subjects[:15]):  # Show first 15
        print(f"  - {subject}")
    print(f"  ... and {len(bio_subjects)-15} more biological categories")


if __name__ == "__main__":
    main()