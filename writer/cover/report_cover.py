"""
Research report cover generator using LLM-generated designs and Playwright.

Generates aesthetic PDF covers by having an LLM create HTML/CSS/Canvas code,
then rendering it to PDF via Playwright's headless Chromium.
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import List, Dict, Any
from playwright.async_api import async_playwright
from pypdf import PdfReader, PdfWriter
from writer.prompts_utils.cover_llm import generate_cover_code


class ReportCover:
    """
    Generates aesthetic PDF covers for research reports.
    
    Uses LLM to generate HTML/CSS/Canvas code based on topic,
    then renders to PDF using Playwright headless browser.
    """
    
    def __init__(self, width_inches: float = 8.5, height_inches: float = 11):
        """
        Args:
            width_inches: Cover page width, defaults to US Letter
            height_inches: Cover page height, defaults to US Letter
        """
        self.width_inches = width_inches
        self.height_inches = height_inches
    
    async def generate(
        self,
        topic: str,
        output_path: str,
        planner_queries: List[Dict[str, Any]] = None
    ) -> str:
        """
        Generates cover PDF for given topic.
        
        Calls LLM to generate HTML cover code, then renders to PDF.
        
        Args:
            topic: Main research topic for cover title
            output_path: Path to save the generated PDF
            planner_queries: Optional planner queries for additional context
            
        Returns:
            Path to generated cover PDF
        """
        html_code = await generate_cover_code(topic, planner_queries)
        await self._render_to_pdf(html_code, output_path)
        return output_path
    
    async def _render_to_pdf(self, html_code: str, output_path: str) -> None:
        """
        Renders HTML with canvas to PDF using Playwright async API.
        
        Saves HTML to temp file, loads in headless Chromium,
        waits for canvas rendering, then exports as PDF.
        
        Args:
            html_code: Complete HTML document with CSS and JS
            output_path: Path to save the PDF
        """
        temp_html_path = '/tmp/cover_temp.html'
        with open(temp_html_path, 'w') as f:
            f.write(html_code)

        # 96 DPI is standard for web
        dpi = 96
        width_px = int(self.width_inches * dpi)
        height_px = int(self.height_inches * dpi)

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            # Set viewport to match page size for correct layout rendering
            page = await browser.new_page(viewport={'width': width_px, 'height': height_px})
            await page.goto(f'file://{temp_html_path}')
            
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(1.5)
            
            await page.pdf(
                path=output_path,
                width=f'{self.width_inches}in',
                height=f'{self.height_inches}in',
                print_background=True,
                margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'}
            )
            await browser.close()
        
        os.remove(temp_html_path)
    
    def combine_with_report(
        self,
        cover_pdf_path: str,
        report_pdf_path: str,
        output_path: str
    ) -> str:
        """
        Merges cover PDF with main report PDF.
        
        Args:
            cover_pdf_path: Path to cover PDF
            report_pdf_path: Path to report PDF
            output_path: Path for combined output
            
        Returns:
            Path to combined PDF
        """
        writer = PdfWriter()
        
        cover = PdfReader(cover_pdf_path)
        writer.add_page(cover.pages[0])
        
        report = PdfReader(report_pdf_path)
        for page in report.pages:
            writer.add_page(page)
        
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return output_path


async def main():
    """Test cover generation with sample topic."""
    cover = ReportCover()
    output = await cover.generate(
        topic="Neural Networks and Deep Learning",
        output_path="/tmp/test_cover.pdf"
    )
    print(f"Cover generated: {output}")


if __name__ == "__main__":
    asyncio.run(main())
