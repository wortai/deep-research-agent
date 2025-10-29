import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from states import AgentGraphState as AgentState
from states import ReportSectionsResponse, ReportIntroductionResponse, ReportAbstractResponse, ReportConclusionResponse
from prompts_utils.writer_prompts import generate_report_conclusion_prompt , generate_report_outline_prompt , generate_section_prompt_batch
from llms import LlmsHouse




class Writer:

    def __init__(self):
        self.google_model = LlmsHouse().google_model('gemini-2.5-flash')
        self.google_model_pro= LlmsHouse().google_model('gemini-2.5-pro')
        self.deepseek_model = LlmsHouse().deepseek_model('deepseek-001')

    def report_section_formatted(self, state: AgentState):
        """Format report sections for display"""
        formatted_report_sections = ""
        for i , section in enumerate(state['report_sections']):
            formatted_report_sections += (
                
                f" Section {i}\n"
                f"Heading: {section['section_heading']},\n"
                f"Content: {section['section_content']}\n" 
                "------------------------------------------------\n" 
    
            )
        return formatted_report_sections

           

    async def generate_section_report(self, state: AgentState, group_size: int = 2, allow_merge: bool = True):
        """Generate structured report sections in small batches using batch-specific prompts"""
        original_sections = state.get('report_sections', []) or []
        if not original_sections:
            return []

        all_out = []
        model_with_structure = self.google_model.with_structured_output(ReportSectionsResponse)

        for i in range(0, len(original_sections), group_size):
            batch = original_sections[i:i+group_size] # this is the part we deciding how many sections to take 



            # need better algorithms to improve what sections to choose . 

            # Generate a prompt specifically for this batch
            section_prompt = await generate_section_prompt_batch(state, batch)

            # Format only the batch sections for the final writing call
            formatted_batch = ""
            for idx, section in enumerate(batch):
                formatted_batch += (
                    f" Section {i+idx}\n"
                    f"Heading: {section['section_heading']},\n"
                    f"Content: {section['section_content']}\n"
                    "------------------------------------------------\n"
                )

            report_section_prompt = f"""

    IMPORTANT INSTRUCTIONS FOR SECTIONS :

                {section_prompt}

    ADDITIONAL INSTRUCTIONS FOR STRUCTURE OF EACH SECTION OF THE REPORT:
-----------------------------------------------------------------------------
            1) Use this prompt very carefully to design the section(s) that will be used in the report directly.
            2) Decide which of these batch sections should be kept separate or merged.
            3) Choose appropriate section names, headings, and content for each final section in this batch.
            4) Design the structure of each section (headings → subheadings → content → closing).
            5) Structures can include tables, bullet points, comparisons, and other formats that improve clarity.
            6) Ensure sections in this batch do not overlap or repeat content.
            7) For this batch, produce {len(batch)} well-formed section(s); merge only when it clearly improves quality.
            8) Preserve factual details and metrics from the provided content.
            # Ensure that every section's 'section_content' , 'section_heading' is output in fully valid Markdown.
            
            # The content should MARKDOWN RULES :
            #     1. Start with a main heading using '#' for the section title.
            #     2. Include subheadings (using '##' or '###') for detailed parts or summaries.
            #     3. Incorporate bullet lists (using '-' or '*') or numbered lists where helpful.
            #     4. Emphasize key points with bold or italicized text.
            #     5. Format code blocks, quotes, or tables appropriately if needed.
            #     6. Maintain consistency and clarity in spacing and layout.
            # This instruction ensures a visually appealing and properly styled Markdown format.
-----------------------------------------------------------------------------

            ------------------------------------------------------
           
             Sections of the report (this batch only):

                 {formatted_batch}
            ------------------------------------------------------

            """

            structured_response = await model_with_structure.ainvoke(report_section_prompt)
            all_out.extend([section.model_dump() for section in structured_response.report_sections])

        return all_out

    # async def generate_outline_report(self , state: AgentState):
    #     prompt_for_outline  = await generate_report_outline_prompt(state)
    #     report_section_part = self.report_section_formatted(state)

    #     outline_prompt = f""" 
        
    #         PROMPT FOR THE REPORT  :
    #             {prompt_for_outline}
    #         ----------------------------------------------

    #         AVAILABLE SECTIONS DATA :
    #             INTRODUCTION of the report :
    #              {await self.generate_report_introduction(state)}
    #             ------------------------------------------------

    #         REPORT SECTIONS PARTS :
    #             {self.report_section_formatted(state)}
    #             ---------------------------------------------

    #         CONCLUSION OF THE REPORT :
    #             {await self.generate_conclusion_report(state)}
    #             ---------------------------------------------
    #      -   

    #     ---------------------------------------------------------------------------------------------------------------

    #                 OUTPUT GUIDELINES:
    #                 - Return a JSON object with the following format:
    #                 {{  "Title_of_report" : "<Title of the report>",
    #                     "Table of Contents" : [

    #                         "Methodology " : "<This is the methodology section of the report>"
    #                         "Abstract ": "<This is the abstract section of the report>",
    #                         "Introduction": <"<This is the introduction section of the report>",
    #                         "Chapters ":[
    #                         "Chapter 1" :[(<section name>, <section small description>) ,(<section name2>, <section small description>) .... so on if more ],
    #                         "Chapter 2" :[(<section name3>, <section small description>) ,(<section name4>, <section small description>) ,(<section name5>, <section small description>) .....],
    #                         ... so on if have more chapters 
    #                         ]
    #                         ""
    #                         "Appendices" : "<This is the appendices section of the report>",
    #                         "Conlcusion" : "<This is the conclusion section of the report>",
    #                     ]
    #                 }}
                    
    #                 ---------------------------------------------------------------------
    #             """   
        
    #     report_outline = await self.google_model_pro.ainvoke(outline_prompt)
    #     return report_outline.content 
     
   
    async def generate_conclusion_report(self , state: AgentState):
        """Generate structured report conclusion using Pydantic schema"""
        prompt_for_report = await generate_report_conclusion_prompt(state)
        report_section_part = self.report_section_formatted(state)

        conclusion_prompt = f""" 
            ------------------------

            PROMPT FOR THE REPORT  :
           
             {prompt_for_report}

            1) Using all these sections of the report .
            2) Write a conclusion for the report based on the prompt and the sections of the report 
            Please ensure that the final output is entirely formatted in Markdown.
            Specifically:
            - Start the output with a main title using '#' (e.g., "# Conclusion").
            - Include subheadings (using '##', '###', etc.) where appropriate.
            - Use proper Markdown syntax for bullet points, numbered lists, and line breaks.
            - Adhere strictly to valid Markdown formatting throughout the response.
            ------------------------
            REPORT SECTIONS PARTS  :
           
             {report_section_part}

            --------------------------------------
        """   
        
        # Use structured output with Pydantic schema
        model_with_structure = self.google_model.with_structured_output(ReportConclusionResponse)
        structured_response = await model_with_structure.ainvoke(conclusion_prompt)
        
        return structured_response.report_conclusion
                    

    async def generate_report_abstract(self, state: AgentState):
        """Generate structured report abstract using Pydantic schema"""
        report_sections = self.report_section_formatted(state)
        prompt_for_abstract = f"""
        You are tasked with writing a professional, concise, and insightful abstract for a research report.

        GUIDELINES FOR WRITING THE ABSTRACT:
        1) Carefully review and synthesize the provided report sections to understand the overall purpose, key findings, methodology, and significance of the report.
        2) The abstract should provide a clear summary of the report's objectives, main results, and conclusions, without unnecessary details.
        3) Use clear, precise, and accessible language suitable for a broad audience, avoiding jargon where possible.
        4) Ensure the abstract is self-contained, does not reference figures/tables, and can stand alone as a summary of the report.
        5) Write in a professional and academic tone, following best practices for research abstracts.
        6) Keep the abstract concise (typically 150-250 words), focusing on clarity and informativeness.
        Please ensure that the abstract is written entirely in Markdown format. Start with a level-1 heading for the title, use level-2 headings for any subsections, and apply bullet points or numbered lists where appropriate. The output should follow valid Markdown syntax, including proper spacing and line breaks. Be concise, clear, and maintain a professional tone throughout the abstract.
        REPORT SECTIONS ON WHICH ABSTRACT SUPPOSE TO BE ON:
        {report_sections}
        """
        
        # Use structured output with Pydantic schema
        model_with_structure = self.google_model.with_structured_output(ReportAbstractResponse)
        structured_response = await model_with_structure.ainvoke(prompt_for_abstract)
        
        return structured_response.report_abstract
    
    async def generate_report_introduction(self, state: AgentState):
        """
        Generates a professional, insightful introduction for the report,
        deeply understanding the report sections and tailoring the introduction
        to the type of content (e.g., science, political, historical, finance, news, entertainment, research, etc.).
        Uses best prompting practices for clarity, depth, and professional standards.
        """
        # Use generate_section_report to get structured sections data
        report_sections = await self.generate_section_report(state)
        
        prompt_for_introduction = f"""
    
     You are an expert report writer. Your task is to craft a professional, precise, and insightful introduction for a report, based on the following sections:
    REPORT SECTIONS (analyze deeply to understand the report's scope, themes, and type):
    
    {report_sections}

    GUIDELINES FOR WRITING THE INTRODUCTION:
    1. Carefully analyze the provided sections to understand the report's subject, context, and objectives.
    2. Identify the type of report (e.g., scientific, political, historical, financial, news, entertainment, research, etc.) and tailor the introduction's tone, style, and focus accordingly.
    3. Write a compelling heading for the introduction that fits the report's domain and purpose.
    4. Clearly state the report's background, significance, and main objectives, referencing the nature and structure of the included sections.
    5. Highlight any unique aspects or approaches in the report, based on the section types and content.
    6. Ensure the introduction is concise, engaging, and meets professional report standards.
    7. Use evidence-based prompting techniques: be specific, context-aware, and ensure the introduction is deeply informed by the report's sections.
    "Please generate the report introduction in Markdown format. The output must begin with a main heading (using '#' for the title) and include clear subheadings (using '##' or '###') as needed. Ensure that all text, bullet-point lists, and numbered lists follow standard Markdown syntax, so the final output is fully valid Markdown."

    """
        
        # Use structured output with Pydantic schema
        model_with_structure = self.google_model.with_structured_output(ReportIntroductionResponse)
        structured_response = await model_with_structure.ainvoke(prompt_for_introduction)
        
        return {
            'introduction_heading': structured_response.introduction_heading,
            'introduction_content': structured_response.introduction_content
        }
    
    async def generate_markdown_report_file(self, state: AgentState, file_path: str = "report.md") -> None:
        result = await self.run(state)

        md_lines = []

        # Report Introduction
        md_lines.append("# REPORT INTRODUCTION")
        md_lines.append("-" * 40)
        md_lines.append("")
        md_lines.append(result.get("report_introduction", "No Introduction"))
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

        # Report Sections
        md_lines.append("# REPORT SECTIONS")
        md_lines.append("-" * 40)
        for section in result.get("report_sections", []):
            md_lines.append(f"## {section.get('section_heading', 'No Heading')}")
            md_lines.append("")
            md_lines.append(f"{section.get('section_content', 'No Content')}")
            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")

        # Report Abstract
        md_lines.append("# REPORT ABSTRACT")
        md_lines.append("-" * 40)
        md_lines.append("")
        md_lines.append(result.get("report_abstract", "No Abstract"))
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

        # Report Conclusion
        md_lines.append("# REPORT CONCLUSION")
        md_lines.append("-" * 40)
        md_lines.append("")
        md_lines.append(result.get("report_conclusion", "No Conclusion"))
        md_lines.append("")

        # Write to a Markdown file
        markdown_content = "\n".join(md_lines)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            print(f"Markdown report successfully written to {file_path}")
        except Exception as e:
            print(f"Failed to write markdown report: {e}")
    



         
    async def run(self, state: AgentState):
        sections = await self.generate_section_report(state)
        # Update state for downstream steps
        state['report_sections'] = sections
        introduction = await self.generate_report_introduction(state)
        # outline = await self.generate_outline_report(state)
        abstract = await self.generate_report_abstract(state)
        conclusion = await self.generate_conclusion_report(state)
        
        report = {
            "report_introduction": introduction['introduction_content'],
            "report_sections": sections,
            "report_abstract": abstract,
            "report_conclusion": conclusion,
            # "report_outline ": outline
        }
        
        return report




# Main method for testing
async def main():
    """Test the report_section_report method using fake data"""
    
    from fake_data.fakedata import AgentGraphState
    # print(AgentGraphState)
    # Initialize Writer
    writer = Writer()
    
    print("Testing report_section_report method with fake data...")
    print("=" * 60)
    
    try:
        # Generate the Markdown report file
        await writer.generate_markdown_report_file(AgentGraphState)
        
        # Run full report generation and print result to console for viewing
        report = await writer.run(AgentGraphState)
        print("Generated Report Data:")
        print(report)
     
            
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

