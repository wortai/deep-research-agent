# utils.py - Complete working solution

import re
import base64
import urllib.parse
import requests
import mistune
import os
from weasyprint import HTML, CSS


def render_math_to_svg(latex: str, display: bool = False) -> str:
    """
    Convert LaTeX equation to SVG using MathJax online service.
    This creates an IMAGE that WeasyPrint can render perfectly.
    """
    latex = latex.strip()
    
    # Clean up the latex
    latex = latex.replace('\\', '\\\\')  # Escape backslashes for URL
    
    encoded = urllib.parse.quote(latex)
    color = "black"
    bg = "transparent"
    
    # MathJax SVG renderer endpoint
    url = f"https://math.vercel.app/?from={encoded}&color={color}&bg={bg}"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            svg_bytes = response.content
            # Convert to base64 data URI
            b64 = base64.b64encode(svg_bytes).decode('utf-8')
            
            if display:
                # Centered, block-level for $$...$$
                return f'''
                <div class="math-display" style="text-align: center; margin: 1.5em 0;">
                    <img src="data:image/svg+xml;base64,{b64}" 
                         style="max-width: 100%; height: auto;" 
                         alt="Equation: {latex[:50]}..." />
                </div>
                '''
            else:
                # Inline for $...$
                return f'''
                <span class="math-inline" style="display: inline-block; vertical-align: middle;">
                    <img src="data:image/svg+xml;base64,{b64}" 
                         style="height: 1.2em; width: auto;" 
                         alt="{latex[:30]}..." />
                </span>
                '''
    except Exception as e:
        print(f"Math rendering failed for '{latex[:30]}...': {e}")
    
    # Fallback: render as monospace text
    style = "display: block; text-align: center; margin: 1em 0; font-family: monospace;" if display else "font-family: monospace;"
    tag = "div" if display else "span"
    return f'<{tag} style="{style}">${latex}$</{tag}>'


def process_math_in_markdown(markdown_content: str) -> str:
    """
    Find all $...$ and $$...$$ blocks and replace with SVG images.
    """
    
    # Pattern for display math: $$...$$
    # Use non-greedy match and handle multiline
    display_pattern = r'\$\$(.*?)\$\$'
    
    # Pattern for inline math: $...$ (not preceded by $)
    inline_pattern = r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)'
    
    def replace_display(match):
        latex = match.group(1).strip()
        print(f"Rendering display math: {latex[:60]}...")
        return render_math_to_svg(latex, display=True)
    
    def replace_inline(match):
        latex = match.group(1).strip()
        # Skip empty matches
        if not latex:
            return match.group(0)
        print(f"Rendering inline math: {latex[:40]}...")
        return render_math_to_svg(latex, display=False)
    
    # Process display math first (more specific)
    text = re.sub(display_pattern, replace_display, markdown_content, flags=re.DOTALL)
    
    # Then process inline math
    text = re.sub(inline_pattern, replace_inline, text)
    
    return text


def convert_markdown_to_html(markdown_content: str) -> str:
    """
    Converts markdown to HTML with LaTeX math rendered as SVG images.
    This ensures perfect rendering in WeasyPrint PDFs.
    """
    # Step 1: Convert math to SVG images
    processed_content = process_math_in_markdown(markdown_content)
    
    # Step 2: Convert markdown to HTML
    body_html = mistune.html(processed_content)
    
    # Step 3: Wrap in proper HTML document
    html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Report</title>
    <style>
        body {{
            font-family: "Times New Roman", Times, serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
        }}
        .math-display {{
            margin: 20px 0;
        }}
        .math-inline {{
            vertical-align: middle;
        }}
        /* Ensure images don't overflow */
        img {{
            max-width: 100%;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #2c5282;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
    </style>
</head>
<body>
{body_html}
</body>
</html>"""
    
    return html_document


# Keep your existing functions...
def get_default_css_path() -> str:
    """Returns absolute path to default_style.css for PDF styling."""
    return os.path.join(os.path.dirname(__file__), "default_style.css")


def ensure_output_directory() -> str:
    """Creates output directory if not exists, returns its path."""
    output_dir = os.path.join(os.path.dirname(__file__), "../output")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


async def write_to_pdf(layout: str, output_path: str = None) -> str:
    """
    Converts markdown to styled PDF using WeasyPrint with math support.
    """
    if output_path is None:
        task_id = __import__('uuid').uuid4().hex
        output_dir = ensure_output_directory()
        output_path = f"{output_dir}/{task_id}.pdf"
    
    css_path = get_default_css_path()
    
    try:
        html_content = convert_markdown_to_html(layout)
        
        # Debug: save HTML for inspection
        debug_html_path = output_path.replace('.pdf', '_debug.html')
        with open(debug_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Debug HTML saved to: {debug_html_path}")
        
        css = CSS(filename=css_path) if os.path.exists(css_path) else None
        
        if css:
            HTML(string=html_content).write_pdf(output_path, stylesheets=[css])
        else:
            HTML(string=html_content).write_pdf(output_path)
        
        return __import__('urllib').parse.quote(output_path)
    except Exception as e:
        print(f"Error converting to PDF: {e}")
        import traceback
        traceback.print_exc()
        return ""