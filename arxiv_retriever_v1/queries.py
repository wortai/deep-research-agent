import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from typing import List
import re

class QueryVariationGenerator:
    def __init__(self, api_key: str = None):
        """
        Initialize the QueryVariationGenerator with Gemini API.
        
        Args:
            api_key (str): Google API key. If None, will try to get from environment variable GOOGLE_API_KEY
        """
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
        elif not os.environ.get("GOOGLE_API_KEY"):
            raise ValueError("Google API key must be provided either as parameter or GOOGLE_API_KEY environment variable")
        
        # Initialize Gemini model with updated model name
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  # Updated model name
            temperature=0.7,  # Slightly creative but still focused
            max_tokens=1000,
            max_retries=2
        )
    
    def generate_query_variations(self, base_query: str, num_variations: int = 5) -> List[str]:
        """
        Generate multiple variations of a search query using Gemini.
        
        Args:
            base_query (str): The original search query
            num_variations (int): Number of variations to generate
            
        Returns:
            List[str]: List of query variations
        """
        
        # Create a comprehensive prompt template
        prompt_template = PromptTemplate(
            input_variables=["query", "num_variations"],
            template="""
You are an expert search query optimizer. Given a base search query, generate {num_variations} different variations that would help find comprehensive and diverse results on the same topic.

The variations should include:
1. Synonymous terms and alternative phrases
2. More specific technical terms
3. Broader conceptual queries
4. Different perspectives or angles
5. Related subtopics or applications

Base Query: "{query}"

Generate exactly {num_variations} distinct search query variations. Format your response as a numbered list:

1. [First variation]
2. [Second variation]
3. [Third variation]
...and so on.

Make sure each variation is:
- Relevant to the original topic
- Distinct from others
- Optimized for academic/research search
- Clear and concise (preferably 2-8 words)

Do not include explanations, just the numbered list of queries.
"""
        )
        
        try:
            # Format the prompt
            formatted_prompt = prompt_template.format(
                query=base_query,
                num_variations=num_variations
            )
            
            # Generate response using Gemini
            messages = [HumanMessage(content=formatted_prompt)]
            response = self.llm.invoke(messages)
            
            # Extract queries from the response
            variations = self._parse_variations(response.content, num_variations)
            
            # Ensure we have the requested number of variations
            if len(variations) < num_variations:
                # If we didn't get enough, try a simpler approach
                variations.extend(self._generate_simple_variations(base_query, num_variations - len(variations)))
            
            return variations[:num_variations]  # Return exactly the requested number
            
        except Exception as e:
            print(f"Error generating variations: {e}")
            # Fallback: return simple variations
            return self._generate_simple_variations(base_query, num_variations)
    
    def _parse_variations(self, response_text: str, expected_count: int) -> List[str]:
        """
        Parse the LLM response to extract query variations.
        
        Args:
            response_text (str): Raw response from LLM
            expected_count (int): Expected number of variations
            
        Returns:
            List[str]: Extracted query variations
        """
        variations = []
        
        # Look for numbered lists (1. 2. 3. etc.)
        numbered_pattern = r'^\d+\.?\s*(.+)$'
        
        lines = response_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try to match numbered format
            match = re.match(numbered_pattern, line)
            if match:
                query = match.group(1).strip()
                # Clean up the query (remove quotes, extra spaces)
                query = re.sub(r'^["\']|["\']$', '', query).strip()
                if query and len(query) > 2:  # Basic validation
                    variations.append(query)
        
        # If numbered format didn't work, try to split by lines and clean
        if len(variations) < expected_count // 2:
            variations = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith(('Generate', 'Base Query', 'The variations')):
                    # Remove common prefixes and clean
                    line = re.sub(r'^[-•*]\s*', '', line)  # Remove bullet points
                    line = re.sub(r'^\d+\.?\s*', '', line)  # Remove numbers
                    line = re.sub(r'^["\']|["\']$', '', line).strip()  # Remove quotes
                    if line and len(line) > 2:
                        variations.append(line)
        
        return variations
    
    def _generate_simple_variations(self, base_query: str, num_needed: int) -> List[str]:
        """
        Generate simple variations as fallback.
        
        Args:
            base_query (str): Original query
            num_needed (int): Number of variations needed
            
        Returns:
            List[str]: Simple query variations
        """
        simple_variations = [
            f"{base_query} research",
            f"{base_query} applications",
            f"{base_query} methods",
            f"{base_query} algorithms",
            f"{base_query} techniques",
            f"{base_query} analysis",
            f"{base_query} implementation",
            f"{base_query} review",
            f"{base_query} survey",
            f"{base_query} advances"
        ]
        
        return simple_variations[:num_needed]
    
    def generate_with_context(self, base_query: str, context: str, num_variations: int = 5) -> List[str]:
        """
        Generate query variations with additional context.
        
        Args:
            base_query (str): The original search query
            context (str): Additional context or domain specification
            num_variations (int): Number of variations to generate
            
        Returns:
            List[str]: List of query variations with context
        """
        
        prompt_template = PromptTemplate(
            input_variables=["query", "context", "num_variations"],
            template="""
Generate {num_variations} search query variations for the topic "{query}" specifically in the context of {context}.

The variations should be relevant to both the base topic and the specified context. Make them suitable for academic/research databases.

Format as a numbered list:
1. [First variation]
2. [Second variation]
...

Keep queries concise and research-focused.
"""
        )
        
        try:
            formatted_prompt = prompt_template.format(
                query=base_query,
                context=context,
                num_variations=num_variations
            )
            
            messages = [HumanMessage(content=formatted_prompt)]
            response = self.llm.invoke(messages)
            variations = self._parse_variations(response.content, num_variations)
            
            if len(variations) < num_variations:
                # Add context-based simple variations
                context_variations = [f"{base_query} {context}", f"{context} {base_query}"]
                variations.extend(context_variations)
            
            return variations[:num_variations]
            
        except Exception as e:
            print(f"Error generating contextual variations: {e}")
            return [f"{base_query} {context}"] * num_variations


# Example usage and testing
def main():
    """
    Example usage of QueryVariationGenerator
    """
    # Initialize with API key (replace with your actual key)
    # You can also set GOOGLE_API_KEY environment variable instead
    try:
        generator = QueryVariationGenerator(api_key="AIzaSyAguOE8t4H1YON7WjH0HXj6Q-DRKRj49Pk")  # Will use env variable
        
        # Example 1: Basic query variations
        base_query = "large language models"
        variations = generator.generate_query_variations(base_query, num_variations=7)
        
        print(f"Base Query: '{base_query}'")
        print(f"\nGenerated {len(variations)} variations:")
        for i, variation in enumerate(variations, 1):
            print(f"{i}. {variation}")
        
        print("\n" + "="*50 + "\n")
        
        # Example 2: Query with context
        contextual_variations = generator.generate_with_context(
            base_query="neural networks",
            context="healthcare applications",
            num_variations=5
        )
        
        print("Contextual Variations (Neural Networks in Healthcare):")
        for i, variation in enumerate(contextual_variations, 1):
            print(f"{i}. {variation}")
            
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set your Google API key as environment variable GOOGLE_API_KEY")
        print("Or pass it directly to QueryVariationGenerator(api_key='your_key')")


if __name__ == "__main__":
    main()