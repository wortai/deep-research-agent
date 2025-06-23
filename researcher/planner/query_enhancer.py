"""
Query enhancement functionality for the Deep Search Planner Agent
"""
from typing import Optional
import google.generativeai as genai
from researcher.planner.prompts import Prompts
from researcher.planner.utils import ResponseParser


class QueryEnhancer:
    """Handles query enhancement using AI models"""
    
    def __init__(self, model: genai.GenerativeModel):
        """
        Initialize the QueryEnhancer
        
        Args:
            model: Configured Gemini model instance
        """
        self.model = model
    
    def enhance_search_query(self, user_query: str) -> str:
        """
        Enhance the user's search query using the specialized prompt
        
        Args:
            user_query: Original user search query
            
        Returns:
            str: Enhanced search query
        """
        # Format the prompt with the user's query
        enhancement_prompt = Prompts.ENHANCE_SEARCH_QUERY.format(user_search_query=user_query)
        
        try:
            response = self.model.generate_content(enhancement_prompt)
            response_text = response.text.strip()
            
            # Extract the Enhanced Query from the response
            enhanced_query = ResponseParser.extract_enhanced_query(response_text)
            
            print(f"🔍 Query enhanced: '{user_query}' → '{enhanced_query}'")
            return enhanced_query
            
        except Exception as e:
            print(f"❌ Error enhancing query: {str(e)}")
            return user_query