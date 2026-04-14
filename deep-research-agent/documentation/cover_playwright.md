# Install required packages
# pip install playwright pypdf --break-system-packages
# playwright install chromium

from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter
import os

def html_cover_to_pdf(html_content, css_content, output_path, 
                       width_inches=8.5, height_inches=11):
    """
    Convert HTML/CSS cover to PDF with exact dimensions
    
    Args:
        html_content: Your HTML as string
        css_content: Your CSS as string
        output_path: Where to save cover PDF
        width_inches, height_inches: Page dimensions (default: US Letter)
    """
    # Combine HTML and CSS
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            {css_content}
            body {{
                margin: 0;
                padding: 0;
                width: {width_inches}in;
                height: {height_inches}in;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Set viewport to match PDF dimensions (96 DPI)
        page.set_content(full_html)
        
        # Generate PDF with exact dimensions
        page.pdf(
            path=output_path,
            width=f"{width_inches}in",
            height=f"{height_inches}in",
            print_background=True,
            margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
        )
        
        browser.close()

def combine_cover_with_report(cover_pdf_path, report_pdf_path, 
                                output_path):
    """
    Merge cover PDF with main report PDF
    """
    writer = PdfWriter()
    
    # Add cover page
    cover = PdfReader(cover_pdf_path)
    writer.add_page(cover.pages[0])
    
    # Add report pages
    report = PdfReader(report_pdf_path)
    for page in report.pages:
        writer.add_page(page)
    
    # Save combined PDF
    with open(output_path, "wb") as output:
        writer.write(output)
    
    print(f"✅ Combined PDF saved to: {output_path}")

# Usage Example
def create_research_report_with_cover(html, css, report_pdf):
    """
    Complete workflow for your LangGraph node
    """
    # Step 1: Generate cover PDF from HTML/CSS
    cover_path = "/tmp/cover.pdf"
    html_cover_to_pdf(html, css, cover_path)
    
    # Step 2: Combine with report
    final_path = "/home/claude/final_report.pdf"
    combine_cover_with_report(cover_path, report_pdf, final_path)
    
    return final_path

    ------------------------------------------------------------------------

    from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter
import time

def create_canvas_cover_and_merge(html_with_js, report_pdf, output_pdf):
    """For your political book cover with canvas"""
    
    # Save HTML to file
    with open('/tmp/cover.html', 'w') as f:
        f.write(html_with_js)
    
    # Convert to PDF with Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('file:///tmp/cover.html')
        
        # CRITICAL: Wait for canvas rendering + fonts
        page.wait_for_load_state('networkidle')
        time.sleep(1.5)  # Extra time for canvas drawing
        
        page.pdf(
            path='/tmp/cover.pdf',
            width='8.5in',
            height='11in',
            print_background=True,
            margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'}
        )
        browser.close()
    
    # Merge with report
    writer = PdfWriter()
    writer.add_page(PdfReader('/tmp/cover.pdf').pages[0])
    for page in PdfReader(report_pdf).pages:
        writer.add_page(page)
    
    with open(output_pdf, 'wb') as f:
        writer.write(f)
    
    return output_pdf