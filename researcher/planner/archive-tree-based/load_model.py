import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.language_models.base import BaseLanguageModel

# Load environment variables from .env file
load_dotenv()


def load_gemini_model(model_name: str = "gemini-1.5-flash", api_key: Optional[str] = None,
 temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs: Any) -> BaseLanguageModel:
    """
    Load and configure a Gemini model using LangChain.
    
    Returns:
        BaseLanguageModel: Configured Gemini model instance
    
    Raises:
        ValueError: If API key is not provided or found in environment
        Exception: If model initialization fails
    """
    try:
        # Get API key from parameter or environment
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
            
        if not api_key:
            raise ValueError(
                "Google API key is required. Provide it as a parameter or set GOOGLE_API_KEY environment variable."
            )
        
        # Configure model parameters
        model_config = {
            "model": model_name,
            "google_api_key": api_key,
            "temperature": temperature,
            **kwargs
        }
        
        # Add max_tokens if specified
        if max_tokens is not None:
            model_config["max_tokens"] = max_tokens
        
        # Initialize the model
        model = init_chat_model(**model_config, model_provider="google_genai")
        
        print(f"Successfully loaded Gemini model: {model_name}")
        return model
        
    except Exception as e:
        print(f"Error loading Gemini model: {str(e)}")
        raise
