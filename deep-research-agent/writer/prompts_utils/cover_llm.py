"""
LLM prompt generator for aesthetic research report cover generation.

Produces HTML + CSS + Canvas JavaScript code for visually appealing covers
based on research topic and planner queries.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any
from llms import LlmsHouse
from pydantic import BaseModel, Field


class CoverCodeResponse(BaseModel):
    """LLM response containing complete HTML cover code."""
    code: str = Field(description="Complete HTML document with embedded CSS and JavaScript for the cover")


async def generate_cover_code(
    topic: str,
    planner_queries: List[Dict[str, Any]] = None
) -> str:
    """
    Generates HTML/CSS/Canvas code for aesthetic cover.
    
    Uses LLM to produce complete HTML document with styling and canvas-based
    graphics tailored to the research topic. Includes "by Wort" branding
    and current date.
    
    Args:
        topic: Main research topic/title for the cover
        planner_queries: Optional list of planner query dicts for context
        
    Returns:
        Complete HTML document string ready for Playwright rendering
    """
    current_date = datetime.now().strftime("%B %d, %Y")
    
    context_info = ""
    if planner_queries:
        queries = [pq.get('query', '') for pq in planner_queries[:5]]
        context_info = f"\nTopics covered:\n- " + "\n- ".join(queries)
    
    prompt = f"""Create a code drawing an Aesthetic book cover for a research report about: "{topic}"
{context_info}

REQUIREMENTS:
1. **LAYOUT & DIMENSIONS**: 
   - The design MUST be exactly 8.5 x 11 inches (Portrait).
   - **DO NOT** create a centered container on a gray background.
   - The `body` must be the cover itself. Set `margin: 0; padding: 0; width: 8.5in; height: 11in;`.
   - The design must fill the entire viewport.
   - Use absolute positioning or CSS Grid to place elements precisely.
   - **NOTHING SHOULD OVERLAP** text elements. Ensure high contrast and readability.

2. **AESTHETICS (Use HTML + CSS + Canvas)**:
   - **Scientific/Math**: use relevant symbols, formulas, geometric patterns and aesthetic colors and design and minimalistic
   - **Technical**: use modern, clean tech-inspired visuals
   - **Historical/Social**: use elegant, old-money aesthetic colors
   - **Finance**: use modern, clean tech-inspired visuals
   - **Political**: use aesthetic, old-money aesthetic colors and Design should minamilistic and explanatory
   - **General**: use aesthetic design with sophisticated color palette

3. **Technical Specs**:
   - Use Google Fonts (e.g., Cormorant Garamond, Montserrat, Playfair Display).
   - Use Canvas API for background patterns/drawings (behind text).
   - `z-index` management is crucial: Text must be on top of Canvas.

MANDATORY ELEMENTS:
- Title: "{topic}" prominently displayed
- "by Wort" at the bottom (this is the brand)
- Date: "{current_date}"

FORBIDDEN:
- No author names other than "Wort"
- No external dependencies except Google Fonts
- No placeholder images or external image URLs

OUTPUT: A single complete HTML document with all CSS in <style> and JS in <script> tags.
The document should be sized for 8.5x11 inches (letter size) print.

Example structure:
```html
<!DOCTYPE html>
<html>
<head>
  <link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">
  <style>/* all styling here */</style>
</head>
<body>
  <canvas id="cover"></canvas>
  <div class="content">...</div>
  <script>/* canvas drawing code here */</script>
</body>
</html>
```

Generate only the HTML code, no explanations."""

    model = LlmsHouse().google_model('gemini-3-pro-preview')
    model_structured = model.with_structured_output(CoverCodeResponse)
    
    response = await model_structured.ainvoke(prompt)
    return response.code


async def main():
    code = await generate_cover_code("Sepration of India 1947")
    print(code[:500])


if __name__ == "__main__":
    asyncio.run(main())
