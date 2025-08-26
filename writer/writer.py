import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from states import AgentGraphState as AgentState
from states import ReportSectionsResponse, ReportIntroductionResponse, ReportAbstractResponse, ReportConclusionResponse
from prompts_utils.writer_prompts import generate_report_conclusion_prompt , generate_report_outline_prompt , generate_section_prompt
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

           

    async def generate_section_report(self, state: AgentState):
        """Generate structured report sections using Pydantic schema"""
        section_prompt = await generate_section_prompt(state)
        # print("This is the main prompt for section : ")
        # print(section_prompt 
        
        report_section_prompt = f"""

        IMPORTANT INSTRUCTIONS FOR SECTIONS :

                {section_prompt}

        ADDITIONAL INSTRUCTIONS FOR STRUCTURE OF EACH SECTION OF THE REPORT:
-----------------------------------------------------------------------------

            1) Use this prompt very Carefully to design the report section outline that will be use in report directly
            2) Carefully decide which sections will be used in the report.
            3) Choose what will be the name of the section , heading , content , and other fields and details . 
            4) You suppose to design , the structure of each section that will be used in report , 
            5) Structure of report can be anything that will fits best to represent that section of the report . 
            6) Structures of the report can be normal (Headings-->subheadings --> content --> last part) , content can be table , bullet points , comparision points , Different formats that looks GOOD  Experimental Results Formats ,Appendices (for Detailed Data) ,           
            7) There Should be minimum 8 sections in the report with being distinguish to each other and discussing unique thing
            8) All sections aiming or proposing everything differntly and different 

-----------------------------------------------------------------------------

            ------------------------------------------------------
           
             Sections of the report  : 

                 {self.report_section_formatted(state)}
            ------------------------------------------------------

            """

        # Use structured output with Pydantic schema
        model_with_structure = self.google_model.with_structured_output(ReportSectionsResponse)
        structured_response = await model_with_structure.ainvoke(report_section_prompt)
        
        # Convert to dict format for state compatibility
        return [section.model_dump() for section in structured_response.report_sections]

    async def generate_outline_report(self , state: AgentState):
        prompt_for_outline  = await generate_section_prompt(state)
        report_section_part = self.report_section_formatted(state)

        outline_prompt = f""" 
        
            PROMPT FOR THE REPORT  :
                {prompt_for_outline}
            ----------------------------------------------

            AVAILABLE SECTIONS DATA :
                INTRODUCTION of the report :
                 {await self.generate_report_introduction(state)}
                ------------------------------------------------

            REPORT SECTIONS PARTS :
                {self.report_section_report(state)}
                ---------------------------------------------

            CONCLUSION OF THE REPORT :
                {await self.generate_conclusion_report(state)}
                ---------------------------------------------
         -   

        ---------------------------------------------------------------------------------------------------------------

                    OUTPUT GUIDELINES:
                    - Return a JSON object with the following format:
                    {{  "Title_of_report" : "<Title of the report>",
                        "Table of Contents" : [

                            "Methodology " : "<This is the methodology section of the report>"
                            "Abstract ": "<This is the abstract section of the report>",
                            "Introduction": <"<This is the introduction section of the report>",
                            "Chapters ":[
                            "Chapter 1" :[(<section name>, <section small description>) ,(<section name2>, <section small description>) .... so on if more ],
                            "Chapter 2" :[(<section name3>, <section small description>) ,(<section name4>, <section small description>) ,(<section name5>, <section small description>) .....],
                            ... so on if have more chapters 
                            ]
                            ""
                            "Appendices" : "<This is the appendices section of the report>",
                            "Conlcusion" : "<This is the conclusion section of the report>",
                        ]
                    }}
                    
                    ---------------------------------------------------------------------
                """   
        
        report_outline = await self.google_model_pro.ainvoke(outline_prompt)
        return report_outline.content 
     
    
    async def generate_conclusion_report(self , state: AgentState):
        """Generate structured report conclusion using Pydantic schema"""
        prompt_for_report = generate_report_conclusion_prompt(state)
        report_section_part = self.report_section_formatted(state)

        conclusion_prompt = f""" 
            ------------------------

            PROMPT FOR THE REPORT  :
           
             {prompt_for_report}

            1) Using all these sections of the report .
            2) Write a conclusion for the report based on the prompt and the sections of the report 

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


    """
        
        # Use structured output with Pydantic schema
        model_with_structure = self.google_model.with_structured_output(ReportIntroductionResponse)
        structured_response = await model_with_structure.ainvoke(prompt_for_introduction)
        
        return {
            'introduction_heading': structured_response.introduction_heading,
            'introduction_content': structured_response.introduction_content
        }
    



         
    async def run(self, state: AgentState):
        introduction = await self.generate_report_introduction(state)
        sections = await self.generate_section_report(state)
        # outline = await self.generate_outline_report(state)
        # abstract = await self.generate_report_abstract(state)
        # conclusion = await self.generate_conclusion_report(state)
        
        report = {
            "report_introduction": introduction['introduction_content'],
            "report_sections": sections,
            # "report_abstract": abstract['report_abstract'],
            # "report_conclusion": conclusion['report_conclusion'],
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
        # Test the report_section_report method directly with fake data
        result = await writer.generate_section_report(AgentGraphState)
        print("\nResult from report_section_report:")
        print("-" * 40)
        print(result) 
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

