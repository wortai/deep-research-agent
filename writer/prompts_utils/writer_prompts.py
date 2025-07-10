"""
Prompt generators for research report creation.
Contains methods to generate prompts that ask LLMs to create better prompts for specific tasks.
"""

from typing import List, Dict, Any


def generate_report_outline_prompt(langgraph_state: Dict[str, Any]) -> str:
    """Generates prompt asking LLM to create an optimal prompt for report outline generation."""
    
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
- Proposed Research: {proposed_research}
- Raw Research Results: {len(raw_research_results)} sources available
- Processed Findings: {len(processed_findings)} analyzed findings
- Review Feedback: {len(review_feedback)} feedback points

PROMPT ENGINEERING REQUIREMENTS:
Generate a highly effective prompt that will instruct an LLM to create a professional research report outline. The prompt should:

1. Follow best prompting practices (clear instructions, specific requirements, structured format)
2. Address the specific nature of this research topic and task
3. Ensure the outline will be extremely professional and comprehensive
4. Highlight the need for distinct sections without redundancy
5. Emphasize proper academic/professional standards
6. Include specific instructions for section purposes and content guidelines
7. Ensure logical flow and hierarchy in the outline structure
8. Address the available research data effectively
9. Include requirements for executive summary, methodology, findings, and conclusion sections
10. Specify the need for appropriate headings and subheadings framework

The prompt you generate should be crafted to produce a high-quality, well-structured outline that will serve as the foundation for an excellent research report. Consider the specific characteristics of this research topic and the available data when crafting your prompt.

Focus on creating a prompt that will result in an outline with clear section definitions, proper academic structure, and comprehensive coverage of the research topic without content overlap between sections.

Generate an optimized prompt that leverages best practices in prompt engineering for this specific report outline generation task."""
    
    return prompt.strip()


def generate_section_prompt(section_data: Dict[str, Any], context_data: Dict[str, Any]) -> str:
    """Generates prompt asking LLM to create an optimal prompt for section writing."""
    
    section_title = section_data.get('title', '')
    section_content = section_data.get('content', '')
    section_conclusion = section_data.get('conclusion', '')
    section_sources = section_data.get('sources', [])
    section_subsections = section_data.get('sub_sections', [])
    
    topic = context_data.get('topic', '')
    task_description = context_data.get('task_description', '')
    raw_research_results = context_data.get('raw_research_results', [])
    processed_findings = context_data.get('processed_findings', [])
    
    prompt = f"""You are an expert in prompt engineering and academic writing. Your task is to generate an optimal prompt that will be used to instruct an LLM to write a comprehensive section for a research report.

SECTION INFORMATION:
- Section Title: {section_title}
- Current Content: {section_content[:200] if section_content else 'None'}...
- Current Conclusion: {section_conclusion[:100] if section_conclusion else 'None'}...
- Available Sources: {len(section_sources)} sources
- Sub-sections: {len(section_subsections)} subsections

RESEARCH CONTEXT:
- Overall Topic: {topic}
- Task Description: {task_description}
- Available Research Sources: {len(raw_research_results)} sources
- Processed Findings: {len(processed_findings)} findings

PROMPT ENGINEERING REQUIREMENTS:
Generate a highly effective prompt that will instruct an LLM to write detailed, professional content for this specific section. The prompt should:

1. Apply advanced prompt engineering techniques for optimal results
2. Address the specific nature of this section and its role in the overall report
3. Provide clear instructions for content depth and analysis requirements
4. Specify which aspects of the research data are most relevant for this section
5. Emphasize the need for professional academic writing standards
6. Include guidelines for proper structure, headings, and organization
7. Address the importance of supporting evidence and citations
8. Ensure the section content is focused and doesn't overlap with other sections
9. Specify requirements for critical analysis and detailed discussion
10. Include instructions for maintaining relevance and avoiding tangential content

The prompt should be tailored to the specific characteristics of this section title and the available research context. Consider what type of content and analysis would be most appropriate for this particular section.

Focus on creating a prompt that will result in comprehensive, well-analyzed content that contributes meaningfully to the overall research report while maintaining professional standards and clear focus.

Generate an optimized prompt that leverages best practices in prompt engineering for this specific section writing task."""
    
    return prompt.strip()


def generate_report_conclusion_prompt(langgraph_state: Dict[str, Any]) -> str:
    """Generates prompt asking LLM to create an optimal prompt for conclusion writing."""
    
    topic = langgraph_state.get('topic', '')
    task_description = langgraph_state.get('task_description', '')
    processed_findings = langgraph_state.get('processed_findings', [])
    review_feedback = langgraph_state.get('review_feedback', [])
    proposed_research = langgraph_state.get('Proposed_Research', '')
    
    prompt = f"""You are an expert in prompt engineering and research analysis. Your task is to generate an optimal prompt that will be used to instruct an LLM to write a comprehensive conclusion for a research report.

RESEARCH INFORMATION:
- Research Topic: {topic}
- Task Description: {task_description}
- Proposed Research: {proposed_research}
- Processed Findings: {len(processed_findings)} key findings analyzed
- Review Feedback: {len(review_feedback)} feedback points

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
    
    return prompt.strip()


def generate_section_structure_prompt(section_data: Dict[str, Any], context_data: Dict[str, Any]) -> str:
    """Generates prompt asking LLM to create an optimal prompt for section structure determination."""
    
    section_title = section_data.get('title', '')
    section_content = section_data.get('content', '')
    section_sources = section_data.get('sources', [])
    section_subsections = section_data.get('sub_sections', [])
    
    topic = context_data.get('topic', '')
    content_type = _analyze_content_type(section_content)
    
    prompt = f"""You are an expert in prompt engineering and information architecture. Your task is to generate an optimal prompt that will be used to instruct an LLM to determine the best structure and format for presenting a specific section in a research report.

SECTION INFORMATION:
- Section Title: {section_title}
- Content Type: {content_type}
- Content Length: {len(section_content.split()) if section_content else 0} words
- Has Sub-sections: {len(section_subsections) > 0}
- Number of Sources: {len(section_sources)}
- Overall Topic: {topic}

PROMPT ENGINEERING REQUIREMENTS:
Generate a highly effective prompt that will instruct an LLM to analyze this section and recommend the optimal structure and presentation format. The prompt should:

1. Apply sophisticated prompt engineering techniques for comprehensive analysis
2. Address the specific characteristics of this section and its content type
3. Include instructions for evaluating multiple structural options
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
    
    return prompt.strip()


