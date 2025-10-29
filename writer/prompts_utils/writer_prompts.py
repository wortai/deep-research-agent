"""
Prompt generators for research report creation.
Contains methods to generate prompts that ask LLMs to create better prompts for specific tasks.
"""


import asyncio
from typing import List, Dict, Any
from llms import LlmsHouse
from states import ResearchReviewData , AgentGraphState

async def generate_report_outline_prompt(langgraph_state: Dict[str, Any]) -> str:
    """ Generates prompt asking LLM to create an optimal prompt for report outline generation. """

    report_sections = langgraph_state['report_sections']

    sections=''
    for section in report_sections:
        sections +=f"""
        -----------------------------------------------------------------------------    
          Here's this section starts.
            
            {section}

            Here's this section ends.
        ------------------------------------------------------------------------------
    """


    prompt = f"""You are an expert in prompt engineering and research report writing. Your task is to generate an optimal prompt that will be used to instruct an LLM to create a comprehensive report outline.

AVAILABLE INFORMATION:
- Available Sections: 

    {sections}

 AVAILABLE INFORMATION ENDS HERE.    
-------------------------------------------

PROMPT ENGINEERING REQUIREMENTS:
Generate a highly effective prompt that will instruct an LLM to create a professional research report outline. The prompt should:

1. Follow best prompting practices (clear instructions, specific requirements, structured format).
2. Address the specific nature of this research topic and task.
3. Ensure the outline will be extremely professional and comprehensive.
4. Highlight the need for distinct sections without redundancy , atleast should have 10 minimum sections and should be well-structured and easy to follow.
5. Make sure you mention what going to  be the Each Section name and what we will discuss about in these sections , like important parts , other side information to focus on  .
6. Your prompt should have details of which sections should be combined and be made one , what will be the order of these sections , Order is very Important as report sections should go deep in topic from top to bottom , like intial topics sections should come first and then sections based on previous or in depth analysis of other should be in bottom.
7. Your prompt should contain the details about , what Should be the heading , title , content , and other relevant details of each section ,Include requirements for executive summary, methodology, findings, and conclusion sections etc but these will be always there sections ,should like based on section content and details.
8. Include specific instructions for Each section purposes and descriptive content explanation that will be discussed in content .
9. Very Important Ensure logical flow and hierarchy in the outline structure.
10. Address the available research data effectively , talk about the important sections and how to address those sections in a prompt.


The prompt you generate should be crafted to produce a high-quality, well-structured outline that will serve as the foundation for an excellent research report. Consider the specific characteristics of this research topic and the available data when crafting your prompt.
Focus on creating a prompt that will result in an outline with clear section definitions, proper academic structure, and comprehensive coverage of the research topic without content overlap between sections.
Generate an optimized prompt that leverages best practices in prompt engineering for this specific report outline generation task.

"""
    model = LlmsHouse.google_model('gemini-2.5-flash')
    # 1.5 flash is the fastest mdoel but 2.5 flash is slower but better  in output
    response_prompt = await model.ainvoke(prompt) # Await the coroutine
    return response_prompt.content



async def generate_report_conclusion_prompt(langgraph_state: AgentGraphState) -> str:
    """Generates prompt asking LLM to create an optimal prompt for conclusion writing."""


    
    report_sections = langgraph_state['report_sections']

    sections=''
    for section in report_sections:
        sections +=f"""
        -----------------------------------------------------------------------------    
          Here's this section starts.
            
            {section}

            Here's this section ends.
        ------------------------------------------------------------------------------
    """
    prompt = f"""You are an expert in prompt engineering and research analysis. Your task is to generate an optimal prompt that will be used to instruct an LLM to write a comprehensive conclusion for a research report.

RESEARCH INFORMATION:
--------------
Sections of the report  :
 {sections}
--------------


PROMPT ENGINEERING REQUIREMENTS:
Generate a highly effective prompt that will instruct an LLM to create a professional, comprehensive conclusion for this research report. The prompt should:

1. Utilize advanced prompt engineering strategies for maximum effectiveness
2. Address the specific nature of this research topic and its conclusions
3. Emphasize the need for synthesis rather than mere summarization
4. Include instructions for addressing the original research questions directly
5. Specify requirements for precision and specificity over vague generalizations
6. Address the importance of evidence-based conclusions
7. Include guidelines for discussing implications and significance
8. Specify the need to acknowledge limitations and suggest future research
9. Ensure the conclusion provides actionable insights and recommendations
10. Emphasize professional academic writing standards and tone

The prompt should be crafted considering the specific characteristics of this research topic and the available findings. Focus on creating instructions that will result in a conclusion that definitively answers the research questions and provides valuable insights.

Consider the depth of analysis required for this particular topic and the type of conclusions that would be most valuable for this research. The prompt should guide the LLM to create a conclusion that demonstrates thorough understanding and provides meaningful contributions to the field.

Focus on creating a prompt that will result in a precise, well-supported conclusion that addresses all aspects of the research topic while maintaining high professional standards and providing clear, actionable insights.

Generate an optimized prompt that leverages best practices in prompt engineering for this specific conclusion writing task."""

    model = LlmsHouse.google_model('gemini-2.5-flash')
    # 1.5 flash is the fastest mdoel but 2.5 flash is slower but better  in output
    response_prompt = await model.ainvoke(prompt) # Await the coroutine
    return response_prompt.content



async def generate_section_prompt_batch(langgraph_state: AgentGraphState, batch_sections: List[Dict[str, Any]]) -> str:
    """Generate an optimal prompt to instruct an LLM to write/refine ONLY the given batch (2–3) of sections."""
    def fmt(sec: Dict[str, Any]) -> str:
        return f"Heading: {sec.get('section_heading','')}.\nCurrent Content: {sec.get('section_content','')}\nURLs: {sec.get('section_urls', [])}"

    sections_block = "\n\n".join(
        [
            f"----- SECTION {i+1} START -----\n{fmt(s)}\n----- SECTION {i+1} END -----"
            for i, s in enumerate(batch_sections)
        ]
    )

 

    prompt = f"""
You are an expert in prompt engineering and academic writing. Your task is to craft an optimal prompt that will instruct an LLM to write or refine high-quality report sections for ONLY the selected sections below.

AVAILABLE SECTIONS (use as the sole target for writing/refinement):
{sections_block}

PROMPT ENGINEERING REQUIREMENTS:
- Your prompt should also include instruction about hyperlink url to the content in markdown format .
- Content should contain hyperlinked URLS for which the content belong too.
- Maintain fidelity to facts, metrics, and given URLs; never invent citations.
- Remove redundancy between these sections; ensure each is distinct and focused.
- Specify which part of the secions have best research data and most relevant to focus on 
- Provide clear instructions for depth, analysis, structure (headings/subheadings), and use of lists/tables where appropriate.
- Emphasize professional tone, specificity over generalities, and logical connections between these sections.
- The prompt you produce must instruct the LLM to output well-structured sections ready for direct inclusion in the report.
- Make sure Section Content should be in MARKDOWN FORMAT . 

Generate the optimized prompt text only.
"""

    model = LlmsHouse.google_model('gemini-2.5-flash')
    response_prompt = await model.ainvoke(prompt)
    return response_prompt.content




async def main():
    # Example usage of generate_report_outline_prompt

    # print("Generating prompt for report outline...")
    # outline_prompt = await generate_report_outline_prompt(sample_state) # Await the async function
    # print("\n--- Generated Outline Prompt ---")
    # print(outline_prompt)
    # print("------------------------------")

    # Example usage of generate_section_prompt (requires sample data)
    # sample_section_data = {
    #     'title': 'Introduction',
    #     'content': 'Initial draft content...',
    #     'conclusion': 'Initial draft conclusion...',
    #     'sources': ['source_id_1', 'source_id_2']
    # }
    # sample_context_data = {
    #     'topic': 'The Impact of AI on Climate Change Research',
    #     # Add other relevant context data if needed by the function
    # }
    # print("\nGenerating prompt for section writing...")
    # section_prompt = generate_section_prompt(sample_section_data, sample_context_data)
    # print("\n--- Generated Section Prompt ---")
    # print(section_prompt)
    # print("------------------------------")

    # Example usage of generate_report_conclusion_prompt (requires sample data)
    print("\nGenerating prompt for report conclusion...")
    conclusion_prompt = await generate_report_conclusion_prompt(sample_state) # Reusing sample_state
    print("\n--- Generated Conclusion Prompt ---")
    print(conclusion_prompt)
    # print("------------------------------")

    # Example usage of generate_section_structure_prompt (requires sample data)
    # sample_section_structure_data = {
    #     'title': 'Methodology',
    #     'content': 'Details about research methods...',
    #     'sources': ['source_id_3'],
    #     'sub_sections': ['Data Collection', 'Analysis Techniques']
    # }
    # sample_structure_context_data = {
    #     'topic': 'The Impact of AI on Climate Change Research',
    #     # Add other relevant context data if needed by the function
    # }
    # print("\nGenerating prompt for section structure...")
    # structure_prompt = generate_section_structure_prompt(sample_section_structure_data, sample_structure_context_data)
    # print("\n--- Generated Section Structure Prompt ---")
    # print(structure_prompt)
    # print("------------------------------")


if __name__ == "__main__":
    asyncio.run(main()) # Run the async main function
