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
    
    # Convert markdown to HTML (math is already generated to SVGs in report_writer)
    body_html = mistune.html(cleaned_markdown)
    
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
