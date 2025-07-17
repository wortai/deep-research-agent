from typing import Dict, Any
from .publisher_utils.utils import write_to_pdf, write_to_doc, write_to_text


class Publisher:
    """Handles report publishing in various formats (PDF, DOCX, Markdown)."""
    
    def __init__(self):
        self.supported_formats = ["pdf", "docx", "markdown"]
    
    def create_report_layout(self, state: Dict[str, Any]) -> str:
        """Creates markdown formatted report layout from AgentGraphState."""
        if not state:
            return "# Empty Report\n\nNo data available."
        
        layout_parts = []
        
        # Title
        try:
            query = state.get('research_review', {}).get('query', 'Research Report')
            layout_parts.append(f"# {query}\n")
        except:
            layout_parts.append("# Research Report\n")
        
        # Abstract
        if state.get('report_abstract'):
            layout_parts.append("## Abstract\n")
            layout_parts.append(f"{state['report_abstract']}\n")
        
        # Introduction
        if state.get('report_introduction'):
            layout_parts.append("## Introduction\n")
            layout_parts.append(f"{state['report_introduction']}\n")
        
        # Methodology
        if state.get('report_methodology'):
            layout_parts.append("## Methodology\n")
            layout_parts.append(f"{state['report_methodology']}\n")
        
        # Research Sections
        if state.get('report_sections'):
            try:
                for section in state['report_sections']:
                    if section.get('section_heading') and section.get('section_content'):
                        layout_parts.append(f"## {section['section_heading']}\n")
                        layout_parts.append(f"{section['section_content']}\n")
            except:
                layout_parts.append("## Research Sections\n")
                layout_parts.append("Error processing research sections.\n")
        
        # Updated sections from writer
        if state.get('updated_report_sections'):
            layout_parts.append("## Updated Analysis\n")
            layout_parts.append(f"{state['updated_report_sections']}\n")
        
        # Conclusion
        if state.get('report_conclusion'):
            layout_parts.append("## Conclusion\n")
            layout_parts.append(f"{state['report_conclusion']}\n")
        
        return "\n".join(layout_parts) if layout_parts else "# Empty Report\n\nNo content available."
    
    async def write_to_pdf(self, layout: str) -> str:
        """Writes markdown layout to PDF format."""
        try:
            return await write_to_pdf(layout)
        except Exception as e:
            print(f"PDF writing failed: {e}")
            return ""
    
    async def write_to_doc(self, layout: str) -> str:
        """Writes markdown layout to DOCX format."""
        try:
            return await write_to_doc(layout)
        except Exception as e:
            print(f"DOCX writing failed: {e}")
            return ""
    
    async def write_to_text(self, layout: str) -> str:
        """Writes markdown layout to text file."""
        try:
            return await write_to_text(layout)
        except Exception as e:
            print(f"Text writing failed: {e}")
            return ""
    
    async def run(self, report_type: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Main method that acts as LangGraph node for publishing reports."""
        try:
            layout = self.create_report_layout(state)
            
            if not layout:
                print("No layout generated, skipping file creation")
                return state
            
            file_path = ""
            
            if report_type.lower() == "pdf":
                file_path = await self.write_to_pdf(layout)
            elif report_type.lower() == "docx":
                file_path = await self.write_to_doc(layout)
            elif report_type.lower() == "markdown":
                file_path = await self.write_to_text(layout)
            else:
                print(f"Unsupported report type: {report_type}, defaulting to markdown")
                file_path = await self.write_to_text(layout)
            
            # Update state with final report path
            if file_path:
                state['final_report_path'] = file_path
                print(f"Report published successfully: {file_path}")
            else:
                print("Failed to create report file")
                
        except Exception as e:
            print(f"Error in publisher run: {e}")
        
        return state
