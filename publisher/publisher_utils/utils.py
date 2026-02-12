"""
Utility functions for report publishing.

Provides file conversion with LaTeX math rendering via MathJax SVG API.
Uses concurrent requests for efficient batch processing of equations.
"""

import aiofiles
import urllib.parse
import uuid
import mistune
import os
import re
import base64
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
try:
    from weasyprint import HTML, CSS
except Exception as e:
    print(f"Warning: Failed to import weasyprint: {e}")
    HTML = None
    CSS = None


def get_default_css_path() -> str:
    """Returns absolute path to default_style.css for PDF styling."""
    return os.path.join(os.path.dirname(__file__), "default_style.css")


def ensure_output_directory() -> str:
    """Creates output directory if not exists, returns its path."""
    output_dir = os.path.join(os.path.dirname(__file__), "../output")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


class MathRenderer:
    """
    Renders LaTeX equations to SVG images using MathJax API.
    
    Collects all equations first, then batch-processes them
    with concurrent HTTP requests for efficiency.
    """
    
    MATHJAX_API_URL = "https://math.vercel.app/"
    MAX_WORKERS = 10
    REQUEST_TIMEOUT = 15
    
    def __init__(self):
        """Initializes renderer with cache to avoid duplicate API calls."""
        self._cache: dict[str, str] = {}
    
    def _fetch_svg(self, latex: str) -> tuple[str, str | None]:
        """
        Fetches SVG from MathJax API for a single LaTeX expression.
        
        Args:
            latex: Raw LaTeX string to render.
            
        Returns:
            Tuple of (latex, base64_svg) or (latex, None) on failure.
        """
        if latex in self._cache:
            return (latex, self._cache[latex])
        
        try:
            encoded = urllib.parse.quote(latex)
            url = f"{self.MATHJAX_API_URL}?from={encoded}&color=black&bg=transparent"
            
            response = requests.get(url, timeout=self.REQUEST_TIMEOUT)
            if response.status_code == 200:
                b64 = base64.b64encode(response.content).decode('utf-8')
                self._cache[latex] = b64
                return (latex, b64)
        except Exception:
            pass
        
        return (latex, None)
    
    def batch_render(self, latex_expressions: list[str]) -> dict[str, str | None]:
        """
        Renders multiple LaTeX expressions concurrently.
        
        Args:
            latex_expressions: List of unique LaTeX strings to render.
            
        Returns:
            Dict mapping latex string to base64 SVG (or None on failure).
        """
        unique_expressions = list(set(latex_expressions))
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = {
                executor.submit(self._fetch_svg, latex): latex 
                for latex in unique_expressions
            }
            
            for future in as_completed(futures):
                latex, svg_b64 = future.result()
                results[latex] = svg_b64
        
        return results
    
    def create_svg_html(self, latex: str, svg_b64: str | None, display: bool) -> str:
        """
        Creates HTML element for rendered math.
        
        Args:
            latex: Original LaTeX for alt text.
            svg_b64: Base64-encoded SVG, or None for fallback.
            display: True for block-level ($$), False for inline ($).
            
        Returns:
            HTML string with embedded SVG or fallback text.
        """
        if svg_b64:
            if display:
                return f'''<div class="math-display" style="text-align: center; margin: 1.5em 0;">
    <img src="data:image/svg+xml;base64,{svg_b64}" style="max-width: 100%; height: auto;" alt="{latex[:50]}..." />
</div>'''
            else:
                return f'''<span class="math-inline" style="display: inline-block; vertical-align: middle;">
    <img src="data:image/svg+xml;base64,{svg_b64}" style="height: 1.2em; width: auto;" alt="{latex[:30]}..." />
</span>'''
        
        style = "display: block; text-align: center; margin: 1em 0; font-family: monospace;" if display else "font-family: monospace;"
        tag = "div" if display else "span"
        return f'<{tag} style="{style}">${latex}$</{tag}>'


def process_math_in_markdown(markdown_content: str) -> str:
    """
    Replaces LaTeX math expressions with rendered SVG images.
    
    Efficiently processes all equations by:
    1. Extracting all unique LaTeX expressions
    2. Batch-rendering them with concurrent API calls
    3. Replacing in single pass
    
    Args:
        markdown_content: Markdown with $...$ and $$...$$ math.
        
    Returns:
        Markdown with math replaced by HTML img elements.
    """
    display_pattern = r'\$\$(.*?)\$\$'
    inline_pattern = r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)'
    
    display_matches = re.findall(display_pattern, markdown_content, re.DOTALL)
    inline_matches = re.findall(inline_pattern, markdown_content)
    
    all_latex = [m.strip() for m in display_matches + inline_matches if m.strip()]
    
    if not all_latex:
        return markdown_content
    
    renderer = MathRenderer()
    rendered = renderer.batch_render(all_latex)
    
    def replace_display(match):
        latex = match.group(1).strip()
        return renderer.create_svg_html(latex, rendered.get(latex), display=True)
    
    def replace_inline(match):
        latex = match.group(1).strip()
        if not latex:
            return match.group(0)
        return renderer.create_svg_html(latex, rendered.get(latex), display=False)
    
    text = re.sub(display_pattern, replace_display, markdown_content, flags=re.DOTALL)
    text = re.sub(inline_pattern, replace_inline, text)
    
    return text


def clean_url_links_in_markdown(markdown_content: str) -> str:
    """
    Replaces markdown links with URL-like text with 🔗 emoji.
    
    Converts links formatted as [URL](URL) or [Citation Text](URL)
    where the citation text contains the URL domain to just show 🔗
    while preserving the clickable link functionality.
    
    Args:
        markdown_content: Markdown with various link formats.
        
    Returns:
        Markdown with clean emoji icons for URL-heavy links.
    """
    # Pattern 1: Replace [https://example.com](https://example.com) with [🔗](https://example.com)
    # This handles cases where the entire URL is used as link text
    markdown_content = re.sub(
        r'\[https?://[^\]]+\]\((https?://[^\)]+)\)',
        r'[🔗](\1)',
        markdown_content
    )
    
    # Pattern 2: Replace [www.example.com](https://example.com) with [🔗](https://example.com)
    markdown_content = re.sub(
        r'\[www\.[^\]]+\]\((https?://[^\)]+)\)',
        r'[🔗](\1)',
        markdown_content
    )
    
    # Pattern 3: Replace citations that include the domain/URL in the text
    # Example: [Nature - Title](https://nature.com/article) -> [🔗](https://nature.com/article)
    # This is more conservative - only replace if link text looks like a citation
    def replace_citation_link(match):
        link_text = match.group(1)
        url = match.group(2)
        
        # Extract domain from URL for comparison
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if domain_match:
            domain = domain_match.group(1)
            # If the link text contains the domain name, replace with emoji
            if domain.lower() in link_text.lower():
                return f'[🔗]({url})'
        
        # Otherwise keep the original link
        return match.group(0)
    
    markdown_content = re.sub(
        r'\[([^\]]+)\]\((https?://[^\)]+)\)',
        replace_citation_link,
        markdown_content
    )
    
    return markdown_content


def add_link_tooltips(html_content: str) -> str:
    """
    Adds title attributes to links for tooltip display in PDF readers.
    
    This enhances the user experience by showing the full URL when
    hovering over the 🔗 emoji in PDF readers that support tooltips.
    
    Args:
        html_content: HTML with links.
        
    Returns:
        HTML with title attributes added to external links.
    """
    def add_title(match):
        href = match.group(1)
        # Check if title attribute already exists
        if 'title=' in match.group(0):
            return match.group(0)
        # Add title attribute with the URL
        return f'<a href="{href}" title="{href}"'
    
    # Pattern matches <a href="http..." but not if it already has title
    pattern = r'<a href="(https?://[^"]+)"'
    return re.sub(pattern, add_title, html_content)


def convert_markdown_to_html(markdown_content: str) -> str:
    """
    Converts markdown to HTML with LaTeX math rendered as SVG images.
    
    Process order: clean URLs -> math -> markdown -> link tooltips.
    This preserves equation formatting and creates clean, clickable
    link icons while adding URL tooltips for PDF accessibility.
    
    Args:
        markdown_content: Raw markdown with LaTeX math and links.
        
    Returns:
        Complete HTML document ready for PDF conversion.
    """
    # First, clean up URL-heavy links in markdown
    cleaned_markdown = clean_url_links_in_markdown(markdown_content)
    
    # Process math equations
    processed_content = process_math_in_markdown(cleaned_markdown)
    
    # Convert markdown to HTML
    body_html = mistune.html(processed_content)
    
    # Add title attributes to external links for PDF tooltip support
    body_html = add_link_tooltips(body_html)
    
    html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Report</title>
</head>
<body>
{body_html}
</body>
</html>"""
    
    return html_document


async def write_to_pdf(layout: str, output_path: str = None) -> str:
    """
    Converts markdown to styled PDF with math support.
    
    Args:
        layout: Markdown content with LaTeX math.
        output_path: Optional output path. Auto-generates if None.
        
    Returns:
        URL-encoded path to generated PDF, empty string on failure.
    """
    if output_path is None:
        task_id = uuid.uuid4().hex
        output_dir = ensure_output_directory()
        output_path = f"{output_dir}/{task_id}.pdf"
    
    css_path = get_default_css_path()
    
    try:
        if HTML is None:
            print("Error: WeasyPrint not available. Cannot generate PDF.")
            return ""

        html_content = convert_markdown_to_html(layout)
        css = CSS(filename=css_path)
        
        HTML(string=html_content).write_pdf(output_path, stylesheets=[css])
        
        return urllib.parse.quote(output_path)
    except Exception as e:
        print(f"Error converting to PDF: {e}")
        return ""


async def write_to_doc(layout: str) -> str:
    """
    Converts markdown to DOCX using htmldocx.
    
    Args:
        layout: Markdown content to convert.
        
    Returns:
        URL-encoded path to generated DOCX file, empty string on failure.
    """
    task_id = uuid.uuid4().hex
    output_path = ensure_output_directory()
    file_path = f"{output_path}/{task_id}.docx"
    
    try:
        from htmldocx import HtmlToDocx
        from docx import Document
        
        html = mistune.html(layout)
        doc = Document()
        HtmlToDocx().add_html_to_document(html, doc)
        doc.save(file_path)
        
        return urllib.parse.quote(file_path)
    except Exception as e:
        print(f"Error converting to DOCX: {e}")
        return ""


async def write_to_text(layout: str) -> str:
    """
    Saves markdown content to .md text file.
    
    Args:
        layout: Markdown content to save.
        
    Returns:
        URL-encoded path to saved file, empty string on failure.
    """
    task_id = uuid.uuid4().hex
    output_path = ensure_output_directory()
    file_path = f"{output_path}/{task_id}.md"
    
    try:
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(layout)
        
        return urllib.parse.quote(file_path)
    except Exception as e:
        print(f"Error writing to text file: {e}")
        return ""
