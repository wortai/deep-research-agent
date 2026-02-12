"""
PDF Report Publisher for Deep Research Agent.

Converts markdown reports from AgentGraphState to professional PDFs
using WeasyPrint, with cover page integration from ReportCover.
"""

import os
import uuid
import urllib.parse
from typing import Dict, Any

from .publisher_utils.utils import (
    write_to_pdf,
    write_to_doc,
    write_to_text,
    ensure_output_directory,
    get_default_css_path,
    convert_markdown_to_html
)
from writer.cover.report_cover import ReportCover
try:
    from weasyprint import HTML, CSS
except OSError:
    # Handle missing system dependencies (e.g. libgobject on mac)
    HTML = None
    CSS = None
    print("Warning: WeasyPrint system dependencies not found. PDF generation disabled.")


class Publisher:
    """
    Publishes research reports in various formats (PDF, DOCX, Markdown).
    
    Primary focus is PDF generation with professional styling and
    cover page from ReportCover integration.
    """
    
    def __init__(self):
        """Initializes Publisher with ReportCover for cover page generation."""
        self.supported_formats = ["pdf", "docx", "markdown"]
        self._cover_generator = ReportCover()
    
    def _create_report_layout(self, state: Dict[str, Any]) -> str:
        """
        Assembles markdown report from AgentGraphState fields.
        
        Combines table_of_contents, abstract, introduction, body, and
        conclusion into a single formatted markdown document with
        proper section dividers and CSS class wrappers for styling.
        
        Args:
            state: AgentGraphState containing report sections.
            
        Returns:
            Complete markdown report string.
        """
        if not state:
            return "# Empty Report\n\nNo data available."
        
        layout_parts = []
        
        # Table of Contents with ToC wrapper for CSS styling
        if state.get('report_table_of_contents'):
            layout_parts.append('<div class="toc">\n')
            layout_parts.append("# Table of Contents\n")
            layout_parts.append(state['report_table_of_contents'])
            layout_parts.append('\n</div>\n')
        
        # Abstract with wrapper - content already has heading
        if state.get('report_abstract'):
            layout_parts.append('<div class="abstract">\n')
            # Check if abstract already has heading
            abstract_content = state['report_abstract']
            if not abstract_content.strip().startswith('#'):
                layout_parts.append("## Abstract\n\n")
            layout_parts.append(abstract_content)
            layout_parts.append('\n</div>\n')
        
        # Introduction - content already has heading
        if state.get('report_introduction'):
            layout_parts.append('<div class="introduction">\n')
            # Check if introduction already has heading
            intro_content = state['report_introduction']
            if not intro_content.strip().startswith('#'):
                layout_parts.append("## Introduction\n\n")
            layout_parts.append(intro_content)
            layout_parts.append('\n</div>\n')
        
        # Methodology (if present) - content already has heading
        if state.get('report_methodology'):
            layout_parts.append('<div class="methodology">\n')
            method_content = state['report_methodology']
            if not method_content.strip().startswith('#'):
                layout_parts.append("## Methodology\n\n")
            layout_parts.append(method_content)
            layout_parts.append('\n</div>\n')
        
        # Report Body (chapters and subchapters) - already has all headings
        if state.get('report_body'):
            layout_parts.append(state['report_body'])
            layout_parts.append("\n")
        
        # Conclusion with wrapper - content already has heading
        if state.get('report_conclusion'):
            layout_parts.append('<div class="conclusion">\n')
            layout_parts.append(state['report_conclusion'])
            layout_parts.append('\n</div>\n')
        
        return "\n".join(layout_parts) if layout_parts else "# Empty Report\n\nNo content available."
    
    async def _generate_report_pdf(self, layout: str, output_path: str) -> str:
        """
        Generates styled PDF from markdown layout using WeasyPrint.
        
        Args:
            layout: Markdown content for the report body.
            output_path: Full path for PDF output file.
            
        Returns:
            Path to generated PDF.
        """
        css_path = get_default_css_path()
        if HTML is None:
            print("Error: WeasyPrint not mapped. Returning empty path.")
            return ""

        html_content = convert_markdown_to_html(layout)
        css = CSS(filename=css_path)
        
        HTML(string=html_content).write_pdf(output_path, stylesheets=[css])
        return output_path
    
    async def publish_pdf_with_cover(self, state: Dict[str, Any]) -> str:
        """
        Generates complete PDF report with cover page.
        
        Workflow:
        1. Creates markdown layout from state
        2. Generates report body PDF with WeasyPrint
        3. Generates cover page PDF with ReportCover
        4. Merges cover + report into final PDF
        
        Args:
            state: AgentGraphState with report content and user_query.
            
        Returns:
            Path to final combined PDF file.
        """
        output_dir = ensure_output_directory()
        task_id = uuid.uuid4().hex
        
        report_pdf_path = os.path.join(output_dir, f"{task_id}_report.pdf")
        cover_pdf_path = os.path.join(output_dir, f"{task_id}_cover.pdf")
        final_pdf_path = os.path.join(output_dir, f"{task_id}_final.pdf")
        
        # Generate report body PDF
        layout = self._create_report_layout(state)
        await self._generate_report_pdf(layout, report_pdf_path)
        
        # Generate cover page PDF
        topic = state.get('user_query', 'Research Report')
        planner_queries = state.get('planner_query', [])
        await self._cover_generator.generate(topic, cover_pdf_path, planner_queries)
        
        # Combine cover + report
        combined_path = self._cover_generator.combine_with_report(
            cover_pdf_path,
            report_pdf_path,
            final_pdf_path
        )
        
        # Cleanup intermediate files
        self._cleanup_temp_files([report_pdf_path, cover_pdf_path])
        
        return combined_path
    
    def _cleanup_temp_files(self, file_paths: list) -> None:
        """Removes temporary intermediate files."""
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError:
                pass
    
    async def run(self, report_type: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for publishing reports.
        
        Generates report in specified format and updates state with
        final_report_path. For PDF format, includes cover page.
        
        Args:
            report_type: Output format - 'pdf', 'docx', or 'markdown'.
            state: AgentGraphState with report content.
            
        Returns:
            Updated state with final_report_path set.
        """
        try:
            file_path = ""
            
            if report_type.lower() == "pdf":
                file_path = await self.publish_pdf_with_cover(state)
            elif report_type.lower() == "docx":
                layout = self._create_report_layout(state)
                file_path = await write_to_doc(layout)
                file_path = urllib.parse.unquote(file_path) if file_path else ""
            elif report_type.lower() == "markdown":
                layout = self._create_report_layout(state)
                file_path = await write_to_text(layout)
                file_path = urllib.parse.unquote(file_path) if file_path else ""
            else:
                layout = self._create_report_layout(state)
                file_path = await write_to_text(layout)
                file_path = urllib.parse.unquote(file_path) if file_path else ""
            
            if file_path:
                state['final_report_path'] = file_path
                
        except Exception as e:
            print(f"Error in publisher run: {e}")
            import traceback
            traceback.print_exc()
        
        return state


async def publisher_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node wrapper for PDF publishing.
    
    Invoked after writer_node to generate final PDF report with
    cover page from the completed report sections.
    
    Args:
        state: AgentGraphState with completed report sections.
        
    Returns:
        State update with final_report_path containing PDF location.
    """
    publisher = Publisher()
    result = await publisher.run("pdf", state)
    
    return {"final_report_path": result.get("final_report_path", "")}
