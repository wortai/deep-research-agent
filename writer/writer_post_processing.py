import re
import urllib.parse
import base64
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    """
    # Fix backticks around equations LLMs frequently add
    markdown_content = markdown_content.replace('`$$', '$$').replace('$$`', '$$')
    markdown_content = re.sub(r'`\$(.*?)\$`', r'$\1$', markdown_content)

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

def post_process_section(content: str) -> str:
    """
    Applies all formatting corrections to a report section.
    """
    return process_math_in_markdown(content)
