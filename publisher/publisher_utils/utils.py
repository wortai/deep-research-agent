import aiofiles
import urllib.parse
import uuid
import mistune
import os
from md2pdf.core import md2pdf


def get_default_css_path() -> str:
    """Returns the default CSS file path for styling."""
    return os.path.join(os.path.dirname(__file__), "default_style.css")


def ensure_output_directory() -> str:
    """Creates and returns the output directory path."""
    output_dir = os.path.join(os.path.dirname(__file__), "../output")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


async def write_to_pdf(layout: str) -> str:
    """Converts markdown layout to PDF and returns file path."""
    task_id = uuid.uuid4().hex
    output_path = ensure_output_directory()
    file_path = f"{output_path}/{task_id}.pdf"
    css_path = get_default_css_path()
    
    try:
        md2pdf(
            file_path,
            md_content=layout,
            css_file_path=css_path,
            base_url=None
        )
        print(f"PDF report written to {file_path}")
        return urllib.parse.quote(file_path)
    except Exception as e:
        print(f"Error converting to PDF: {e}")
        return ""


async def write_to_doc(layout: str) -> str:
    """Converts markdown layout to DOCX and returns file path."""
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
        
        print(f"DOCX report written to {file_path}")
        return urllib.parse.quote(file_path)
    except Exception as e:
        print(f"Error converting to DOCX: {e}")
        return ""


async def write_to_text(layout: str) -> str:
    """Writes markdown layout to text file and returns file path."""
    task_id = uuid.uuid4().hex
    output_path = ensure_output_directory()
    file_path = f"{output_path}/{task_id}.md"
    
    try:
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(layout)
        
        print(f"Markdown report written to {file_path}")
        return urllib.parse.quote(file_path)
    except Exception as e:
        print(f"Error writing to text file: {e}")
        return ""
