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

    topic = langgraph_state.get('topic', '')
    task_description = langgraph_state.get('task_description', '')
    raw_research_results = langgraph_state.get('raw_research_results', [])
    processed_findings = langgraph_state.get('processed_findings', [])
    review_feedback = langgraph_state.get('review_feedback', [])
    proposed_research = langgraph_state.get('Proposed_Research', '')


    prompt = f"""You are an expert in prompt engineering and research report writing. Your task is to generate an optimal prompt that will be used to instruct an LLM to create a comprehensive report outline.

AVAILABLE INFORMATION:
- Topic: {topic}
- Task Description: {task_description}
- Raw Search Reulsts :{ raw_research_results}
- Processed Findings these are based on Raw_Research_Results and processed by LLM after it: {processed_findings} analyzed findings


PROMPT ENGINEERING REQUIREMENTS:
Generate a highly effective prompt that will instruct an LLM to create a professional research report outline. The prompt should:

1. Follow best prompting practices (clear instructions, specific requirements, structured format)
2. Address the specific nature of this research topic and task
3. Ensure the outline will be extremely professional and comprehensive
4. Highlight the need for distinct sections without redundancy , atleast should have 7 minimum sections and should be well-structured and easy to follow
5. Make sure you mention what gonna be the Each Section name and what we will discuss about in the sections.
6. Include specific instructions for Each section purposes and descriptive content explanation that will be discussed in content 
7. Very Important Ensure logical flow and hierarchy in the outline structure
8. Address the available research data effectively
9. Include requirements for executive summary, methodology, findings, and conclusion sections but these will be always there sections
10. Emphasize proper academic/professional standards

The prompt you generate should be crafted to produce a high-quality, well-structured outline that will serve as the foundation for an excellent research report. Consider the specific characteristics of this research topic and the available data when crafting your prompt.

Focus on creating a prompt that will result in an outline with clear section definitions, proper academic structure, and comprehensive coverage of the research topic without content overlap between sections.

Generate an optimized prompt that leverages best practices in prompt engineering for this specific report outline generation task."""
    model = LlmsHouse.google_model('gemini-2.5-flash')
    # 1.5 flash is the fastest mdoel but 2.5 flash is slower but better  in output
    response_prompt = await model.ainvoke(prompt) # Await the coroutine
    return response_prompt.content


async def generate_section_prompt(section_data: ResearchReviewData) -> str:
    """Generates prompt asking LLM to create an optimal prompt for section writing."""

    section_heading = section_data.get('section_heading', '')
    section_content = section_data.get('section_content', '')
    section_sources = section_data.get('section_urls', [])



    prompt = f"""You are an expert in prompt engineering and academic writing. Your task is to generate an optimal prompt that will be used to instruct an LLM to write a comprehensive section for a research report.

SECTION INFORMATION AND RESEARCH CONTEXT :
- Section Title: {section_heading}
- Current Content: {section_content}...
- Available Sources: {section_sources} sources


PROMPT ENGINEERING REQUIREMENTS:
Generate a highly effective prompt that will instruct an LLM to write detailed, professional content for this specific section. The prompt should:

1. Apply advanced prompt engineering techniques for optimal results
2. Address the specific nature of this section and its role in the overall report
3. Provide clear instructions for content depth and analysis requirements
4. Specify which aspects of the research data are most relevant for this section
5. Emphasize the need for professional academic writing standards
6. Include guidelines for proper structure, headings, and organization
7. Importantly we put focus on not changing section factual and metric data which is very important
8. Most Important Ensure the section content is focused and doesn't overlap with in the sections and we don't repeat same things again
9. Specify requirements for critical analysis and detailed discussion


The prompt should be tailored to the specific characteristics of this section title and the available research context. Consider what type of content and analysis would be most appropriate for this particular section.

Focus on creating a prompt that will result in comprehensive, well-analyzed content that contributes meaningfully to the overall research report while maintaining professional standards and clear focus.

Generate an optimized prompt that leverages best practices in prompt engineering for this specific section writing task."""
    model = LlmsHouse.google_model('gemini-2.5-flash')
    # 1.5 flash is the fastest mdoel but 2.5 flash is slower but better  in output
    response_prompt = await model.ainvoke(prompt) # Await the coroutine
    return response_prompt.content


async def generate_report_conclusion_prompt(langgraph_state: AgentGraphState) -> str:
    """Generates prompt asking LLM to create an optimal prompt for conclusion writing."""


    report_sections = langgraph_state['report_sections']
    prompt = f"""You are an expert in prompt engineering and research analysis. Your task is to generate an optimal prompt that will be used to instruct an LLM to write a comprehensive conclusion for a research report.

RESEARCH INFORMATION:
--------------
Sections of the report  :
 {report_sections}
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
    m
    
    model = LlmsHouse.google_model('gemini-2.5-flash')
    # 1.5 flash is the fastest mdoel but 2.5 flash is slower but better  in output
    response_prompt = await model.ainvoke(prompt) # Await the coroutine
    return response_prompt.content




# for right now let's leave this method alone 
async def generate_section_structure_prompt(section_data: ResearchReviewData) -> str:
    """Generates prompt asking LLM to create an optimal prompt for section structure determination."""

    section_title = section_data.get('title', '')
    section_content = section_data.get('content', '')
    section_sources = section_data.get('sources', [])
    section_subsections = section_data.get('sub_sections', [])

    topic = context_data.get('topic', '')


    prompt = f"""You are an expert in prompt engineering and information architecture. Your task is to generate an optimal prompt that will be used to instruct an LLM to determine the best structure and format for presenting a specific section in a research report.

SECTION INFORMATION:
- Section Title: {section_title}
- Content  : {section_content}
- Has Sub-sections: {len(section_subsections) > 0}
- Number of Sources: {section_sources}
- Overall Topic: {topic}

PROMPT ENGINEERING REQUIREMENTS:
Generate a highly effective prompt that will instruct an LLM to analyze this section and recommend the optimal structure and presentation format. The prompt should:

1. Apply sophisticated prompt engineering techniques for comprehensive analysis
2. Address the specific characteristics of this section and its content type
3. Include instructions for evaluating best suitable structural options as per the given Content
4. Specify criteria for assessing readability and professional presentation
5. Address the relationship between content type and optimal structure
6. Include guidelines for considering reader comprehension and engagement
7. Specify requirements for professional academic presentation standards
8. Address the importance of information hierarchy and logical flow
9. Include instructions for recommending specific formatting elements
10. Ensure the recommendations maximize both clarity and professional appearance

The prompt should be tailored to the specific nature of this section title and content type. Consider what structural approaches would be most effective for this particular type of information and how readers would best interact with this content.

Focus on creating a prompt that will result in thoughtful analysis of structural options and clear recommendations for the most effective presentation format. The prompt should guide the LLM to consider both the content characteristics and the reader's needs.

Consider the complexity of the information, the professional standards required, and the most effective ways to present this specific type of content in an academic/professional context.

Generate an optimized prompt that leverages best practices in prompt engineering for this specific section structure analysis task."""

    model = LlmsHouse.google_model('gemini-2.5-flash')
    # 1.5 flash is the fastest mdoel but 2.5 flash is slower but better  in output
    response_prompt = await model.ainvoke(prompt) # Await the coroutine
    return response_prompt.content


async def main():
    # Example usage of generate_report_outline_prompt
    sample_state = {
        'topic': 'The Impact of AI on Climate Change Research',
        'task_description': 'Write a comprehensive research report on the topic.',
        'raw_research_results': [
            "Document 1: A study on using machine learning for predicting extreme weather events.",
            "Document 2: Analysis of satellite imagery using deep learning for deforestation monitoring.",
            "Document 3: Review of ethical implications of AI deployment in environmental science.",
            "Document 4: Paper on the computational resources required for large-scale climate simulations with AI integration."
        ],
        'processed_findings': """Based on the analysis of various research documents, several key findings emerge regarding the impact of AI on climate change research. Firstly, AI, particularly machine learning and deep learning techniques, significantly enhances the speed and accuracy of data processing and analysis in climate science. This includes improved prediction models for weather patterns, more efficient analysis of complex climate datasets, and automated identification of environmental changes from remote sensing data. Secondly, AI facilitates the development of more sophisticated climate models, allowing for higher resolution simulations and better understanding of intricate climate feedback loops. However, the integration of AI also presents challenges, such as the substantial computational power and energy consumption required for training large models, which itself has an environmental footprint. Furthermore, ethical considerations surrounding data privacy, bias in algorithms, and equitable access to AI technologies in global climate research are critical. The findings suggest that while AI offers powerful tools to accelerate climate research and mitigation efforts, its implementation must be carefully managed to maximize benefits while addressing its own environmental and societal impacts. Future research should focus on developing energy-efficient AI algorithms and ensuring responsible, inclusive deployment of these technologies in the fight against climate change.""",
        'review_feedback': [], # Keeping this empty as per original example
        'Proposed_Research': """## Proposed Research Report: The Transformative Impact of Artificial Intelligence on Climate Change Research and Mitigation

**Executive Summary:**
This report explores the multifaceted impact of Artificial Intelligence (AI) on the field of climate change research and mitigation. It examines how AI technologies, including machine learning, deep learning, and natural language processing, are revolutionizing data analysis, climate modeling, and the development of mitigation strategies. The report synthesizes current findings on AI applications in areas such as extreme weather prediction, deforestation monitoring, renewable energy optimization, and carbon capture technologies. It also critically assesses the challenges and ethical considerations associated with AI deployment in this domain, including computational resource demands, data bias, and equitable access. The aim is to provide a comprehensive overview of AI's potential to accelerate climate action while highlighting the necessary steps for responsible and effective integration.

**1. Introduction:**
Climate change poses an existential threat, requiring rapid advancements in scientific understanding and technological solutions. Artificial Intelligence has emerged as a powerful tool with the potential to significantly enhance our ability to research, monitor, and combat climate change. This section introduces the scope of the report and the growing intersection between AI and climate science.

**2. AI Applications in Climate Change Research:**
This section details specific applications of AI in climate research, including:
- Improved climate modeling and prediction
- Analysis of satellite and sensor data
- Understanding complex climate systems
- Predicting extreme weather events

**3. AI Applications in Climate Change Mitigation:**
This section focuses on how AI is being used to develop and optimize mitigation strategies:
- Renewable energy forecasting and grid management
- Optimization of energy efficiency
- Development of carbon capture technologies
- Sustainable agriculture and land use

**4. Challenges and Ethical Considerations:**
This section addresses the significant challenges and ethical issues:
- Computational cost and energy consumption of AI
- Data availability, quality, and bias
- Ethical implications of AI decision-making in environmental policy
- Ensuring equitable access and benefits globally

**5. Future Directions and Recommendations:**
This section outlines potential future research avenues and provides recommendations for the responsible integration of AI in climate action:
- Development of energy-efficient AI algorithms
- International collaboration and data sharing
- Policy recommendations for ethical AI deployment
- Investing in interdisciplinary training

**6. Conclusion:**
Summarizes the key findings and reiterates the transformative potential of AI in addressing climate change, emphasizing the need for a balanced approach that leverages its power while mitigating its risks.

**References:**
[List of dummy references would go here]

**Appendices:**
[Any supplementary data or figures]
"""
    }
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