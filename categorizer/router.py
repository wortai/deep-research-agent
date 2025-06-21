import sys
import os

print("Current working directory:", os.getcwd())
print("sys.path:")
for p in sys.path:
    print(f"- {p}")


"""
Categorizes research queries using LangChain and Pydantic for intelligent routing
"""
from typing import Dict, List, Optional, Any




import os
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field, field_validator






# Import the detailed prompt template function
from Prompts import Prompt_Club as PromptCreator
from categories import ResearchCategory , CategorizationResponse
from dotenv import load_dotenv
load_dotenv()



class ResearchRouter:
    """Production-level research categorization router using LangChain and Pydantic"""

    def __init__(self, api_key: str = None):
        """Initialize the router with LLM and structured chain"""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is required")

        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=self.api_key,
            temperature=0.1
        )

        # Create the prompt template using the detailed version from Prompts/Prompt.py
        detailed_template_string = PromptCreator.create_detailed_categorization_prompt_template()
        self.categorization_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert AI system designed to categorize research queries and associated planner prompts.
    Your primary goal is to accurately assign a predefined research category to the provided content.
    Analyze the user messages and the planner prompt carefully to understand the core topic and intent.
    Based on your analysis, select the single best-fitting category from the allowed list.
    Provide a confidence score (0.0 to 1.0) reflecting your certainty in the chosen category.
    Include a concise yet detailed reasoning explaining *why* you selected that specific category based on the input content.
    Your output MUST strictly adhere to the specified JSON schema for the CategorizationResponse model.
    Do not include any conversational text or explanations outside the structured output."""),
            ("human", detailed_template_string)
        ])

        # Create the structured output chain using Pydantic model
        self.categorization_chain = self.categorization_prompt | self.llm.with_structured_output(CategorizationResponse)


    def categorize_query(
        self,
        user_messages: List[str] = None,
        planner_prompt: str = "",
    ) -> Dict[str, Any]:

        
        # Combine content for the LLM
        content_parts = []
        if planner_prompt:
            content_parts.append(f"Planner Prompt: {planner_prompt}")
        if user_messages:
            content_parts.append(f"User Messages: {' '.join(user_messages)}")

        combined_content = " ".join(content_parts)

        # Handle empty content case
        if not combined_content.strip():
            return {
                "category": ResearchCategory.GENERAL.value,
                "confidence_score": 0.1, # Lower confidence for empty input
                "reasoning": "No content provided, defaulting to general category",
                "processed_at": datetime.now().isoformat()
            }

        # Invoke the structured output chain with the combined content
        # Any exception during the LLM call or parsing will be raised
        response: CategorizationResponse = self.categorization_chain.invoke({"content": combined_content})

        # Return the result in the desired dictionary format
        return {
            "category": response.category.value,
            "confidence_score": response.confidence_score,
            "reasoning": response.reasoning,
       
        }


# Example usage and testing
if __name__ == "__main__":
    try:
        # Initialize router
        router = ResearchRouter()
        
        # Test cases
        test_cases = [
            {
                "name": "Coding Query",
                "user_messages": ["How to implement a REST API in Python?"],
                "planner_prompt": "Research Python web frameworks and API development"
            },
            {
                "name": "Finance Query",
                "user_messages": ["What are the current stock market trends?"],
                "planner_prompt": "Analyze financial markets and investment opportunities"
            },
            {
                "name": "News Query",
                "user_messages": ["Latest breaking news about technology"],
                "planner_prompt": "Find recent technology news and developments"
            },
            {
                "name": "History Query",
                "user_messages": ["Tell me about ancient Roman civilization"],
                "planner_prompt": "Research historical aspects of Roman Empire"
            },
            {
                "name": "Current Events Query",
                "user_messages": ["What's happening today in the world?"],
                "planner_prompt": "Find today's most important global events"
            },
             {
                "name": "General Query",
                "user_messages": ["Tell me a fun fact about sloths."],
                "planner_prompt": "Find interesting facts about animals"
            },
             {
                "name": "Empty Query",
                "user_messages": [],
                "planner_prompt": ""
            }
        ]

        print("🔄 Testing Research Router (LangChain + Pydantic)")
        print("=" * 50)

        for test_case in test_cases:
            print(f"\n📋 Test: {test_case['name']}")
            try:
                result = router.categorize_query(
                    user_messages=test_case.get("user_messages"),
                    planner_prompt=test_case.get("planner_prompt", "")
                )

                print(f"   Category: {result['category']}")
                print(f"   Confidence: {result['confidence_score']:.2f}")
                print(f"   Reasoning: {result['reasoning']}")
    
            except Exception as e:
                 print(f"   ❌ LLM Categorization Failed: {e}")


        print(f"\n✅ Router testing completed successfully!")

    except Exception as e:
        print(f"❌ Error initializing router: {e}")

