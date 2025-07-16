
from states import AgentState
from prompts_utils.writer_prompts import generate_report_conclusion_prompt , generate_report_outline_prompt , generate_section_prompt
from llms import LlmsHouse




class Writer:

    def __init__(self):
        self.google_model = LlmsHouse().google_model('gemini-2.5-flash')
        self.deepseek_model = LlmsHouse().deepseek_model('deepseek-001')


    async def report_section_fromatted(self, state: AgentState):
        
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
            return report_sections



    async def generate_outline_report(self , state: AgentState):
        prompt_for_outline = await generate_section_prompt(state)
        report_section_part =self.report_section_fromatted(state)

        outline_prompt = f""" 
                    ------------------------
                    PROMPT FOR THE REPORT  :
                    {prompt_for_outline}
         ------------------------------------------------------------------        

            AVAILABLE SECTIONS DATA :

            {self.report_section_fromatted(state)}


         ------------------------------------------------------------------     


        -----------------------------------------------------------------------------------------------------------------------------------------

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
                           "Appendices" : <This part will contain the appendices section of the report>
                           "Conclusion" : <This part will contain the conclusion section of the report>
                          
                    }}
                    
                    -----------------------------------------------------------------
                """   
        
        report_outline = await self.google_model.ainvoke(outline_prompt)
        return report_outline
   
          
                   
           
    
    async def generate_conclusion_report(self , state: AgentState):
                    }}
                    
                    -----------------------------------------------------------------
                """   
        
        report_outline = await self.google_model.ainvoke(outline_prompt)
        return report_outline
   
          
                   
           
    
    async def generate_conclusion_report(self , state: AgentState):

                        ]
                    }}
                    
                    -----------------------------------------------------------------
                """   
        
        report_outline = await self.google_model.ainvoke(outline_prompt)
        return report_outline
   
          
                   
           
    
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
                    


    async def generate_section_report(self , state: AgentState):
        

        return 
    
    async def generate_report_introduction(self, state:AgentState):


    
    async def run(self, state: AgentState):

        return
        


