
from states import AgentState
from prompts_utils.writer_prompts import generate_report_conclusion_prompt , generate_report_outline_prompt , generate_section_prompt
from llms import LlmsHouse




class Writer:

    def __init__(self):
        self.google_model = LlmsHouse().google_model('gemini-2.5-flash')
        self.google_model_pro= LlmsHouse().google_model('gemini-2.5-pro')
        self.deepseek_model = LlmsHouse().deepseek_model('deepseek-001')


    async def report_section_report(self, state: AgentState):
        
            report_section_prompt = f"""

    IMPORTANT INSTRUCTIONS FOR SECTIONS :

                {await generate_section_prompt(state)}

                

    ADDITIONAL INSTRUCTIONS FOR STRUCTURE OF EACH SECTION OF THE REPORT:
-----------------------------------------------------------------------------------------------------------------------------------------
            
            1) Use this prompt very Carefully to design the report section outline that will be use in report directly
            2) Carefully decide which sections will be used in the report.
            3) Choose what will be the name of the section , heading , content , and other fields and details . 
            4) You suppose to design , the structure of each section that will be used in report , 
            5) Structure of report can be anything that will fits best to represent that section of the report . 
            6) Structures of the report can be normal (Headings-->subheadings --> content --> last part) , content can be table , bullet points , comparision points , Different formats that looks GOOD  Experimental Results Formats ,Appendices (for Detailed Data) ,           

-----------------------------------------------------------------------------------------------------------------------------------------



            ------------------------------------------------------
           
             Sections of the report  : 

                 {self.report_section_fromatted(state)}
            -----------------------------------------------------

            OUTPUT GUIDELINESS :

            - Return a JSON object with the following format:
         {{
                        "report_sections": [
                            {{
                                "section_name": "<Section name>",
                                "section_heading": "<Section heading>",
                                "section_content": "<Section content, This will contain the whole detail section>",
                                // more section fields as per that section
                            }},
                            {{
                                "section_name": "<Section name>",
                                "section_heading": "<Section heading>",
                                "section_content": "<Section content, This will contain the whole detail section can be anytype>",
                                // more section fields as per that section
                            }},
                            ...
                        ]
                    }}

            """


            report_sections = await self.google_model.ainvoke(report_section_prompt)
            return report_sections.content


    async def generate_outline_report(self , state: AgentState):
        prompt_for_outline  = await generate_section_prompt(state)
        report_section_part = self.report_section_fromatted(state)

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
        prompt_for_report = generate_report_conclusion_prompt(state)
        report_section_part = self.report_section_fromatted(state)

        conclusion_prompt = f""" 
            ------------------------
            PROMPT FOR THE REPORT  :
            {prompt_for_report}


            1) Using all these sections of the report .
            2) Write a conclusion for the report based on the prompt and the sections of the report 


            ------------------------
            REPORT SECTIONS PARTS  :
            {report_section_part}
   
            OUTPUT GUIDELINES:
            - Return a JSON object with the following format:
            {{
                "report_conclusion": "<Your conclusion text here>"
            }}
            
            --------------------------------------
        """   
        report_conclusion = await self.google_model.ainvoke(conclusion_prompt)
        return report_conclusion
                    


    async def generate_report_abstract(self, state: AgentState):
        report_sections = self.report_section_fromatted(state)
        prompt_for_abstract = f"""
        You are tasked with writing a professional, concise, and insightful abstract for a research report.

        GUIDELINES FOR WRITING THE ABSTRACT:
        1) Carefully review and synthesize the provided report sections to understand the overall purpose, key findings, methodology, and significance of the report.
        2) The abstract should provide a clear summary of the report's objectives, main results, and conclusions, without unnecessary details.
        3) Use clear, precise, and accessible language suitable for a broad audience, avoiding jargon where possible.
        4) Ensure the abstract is self-contained, does not reference figures/tables, and can stand alone as a summary of the report.
        5) Write in a professional and academic tone, following best practices for research abstracts.
        6) Keep the abstract concise (typically 150-250 words), focusing on clarity and informativeness.

        REPORT SECTIONS TO BASE THE ABSTRACT ON:
        {self.report_section_report(state)}

        OUTPUT GUIDELINES:
        - Return a JSON object with the following format:
        {{
            "report_abstract": "<Your abstract text here>"
        }}
        """
        abstract = await self.google_model.ainvoke(prompt_for_abstract)
        return abstract.content
    
    async def generate_report_introduction(self, state: AgentState):
            """
            Generates a professional, insightful introduction for the report,
            deeply understanding the report sections and tailoring the introduction
            to the type of content (e.g., science, political, historical, finance, news, entertainment, research, etc.).
            Uses best prompting practices for clarity, depth, and professional standards.
            """
            report_sections = await self.report_section_report(state)
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

    OUTPUT GUIDELINES:
    - Return a JSON object with the following format:
    {{
        "introduction_heading": "<A professional heading for the introduction>",
        "introduction_content": "<A concise, insightful, and well-structured introduction based on the report sections>"
    }}
    """
            introduction = await self.google_model.ainvoke(prompt_for_introduction)
            return introduction.content

    async def run(self, state: AgentState):
        introduction = await self.generate_report_introduction(state)
        sections = await self.report_section_report(state)
        outline = await self.generate_outline_report(state)
        abstract = await self.generate_report_abstract(state)
        conclusion = await self.generate_conclusion_report(state)
        
        report = {
            "introduction": introduction,
            "sections": sections,
            "outline": outline,
            "abstract": abstract,
            "conclusion": conclusion
        }
        
        return report


