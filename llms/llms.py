
"""LLM Management System - LlmsHouse
Provides unified interface for various LLM providers.

MODEL RECOMMENDATIONS BY USE CASE:

CODING MODELS:
- claude-3-5-sonnet-20241022 (Anthropic) - Best for complex coding tasks
- deepseek-coder (DeepSeek) - Cost-effective coding
- deepseek-chat (DeepSeek) - General coding and chat
- gpt-4o (OpenAI) - Advanced coding tasks
- gpt-4-turbo (OpenAI) - Complex coding projects
- gemini-2.0-flash-001 (Google) - Fast coding assistance

MATH MODELS:
- gemini-2.5-pro (Google) - Best for mathematical reasoning
- qwq-32b-preview (QwQ) - Specialized mathematical reasoning
- gpt-4o (OpenAI) - Advanced mathematical problems
- o1-preview (OpenAI) - Complex mathematical proofs

GENERAL MODELS:
- gemini-2.0-flash-001 (Google) - Fast, cost-effective general use
- gpt-4o (OpenAI) - High-quality general tasks
- deepseek-chat (DeepSeek) - Budget-friendly general chat
- mistral-large-latest (Mistral) - Balanced performance and cost

SEARCH/RESEARCH MODELS:
- llama-3.1-sonar-small-128k-online (Perplexity) - Web search and research
- llama-3.1-sonar-large-128k-online (Perplexity) - Advanced research tasks
"""

import os
import getpass
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_deepseek import ChatDeepSeek
from langchain_qwq import ChatQwQ
from langchain_mistralai import ChatMistralAI
from langchain_community.chat_models import ChatPerplexity
from langchain_anthropic import ChatAnthropic  

# To install these libraries, run the following commands:

from dotenv import load_dotenv
load_dotenv()

class LlmsHouse:
    """
    Main LLM management class providing unified access to various LLM providers.
    """
    
    def __init__(self):
        self.fallback_model = "gemini-2.0-flash"

    @staticmethod
    def openai_model(model_name: str, temperature: float = 1.25, **kwargs) -> ChatOpenAI:
        """
        OpenAI models - High quality, versatile for most tasks.
        Supports: gpt-4o, gpt-4-turbo, gpt-3.5-turbo, o1-preview, etc.
        """
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=kwargs.get('max_tokens', None),
            timeout=kwargs.get('timeout', None),
            max_retries=kwargs.get('max_retries', 2),
            api_key=kwargs.get('api_key', None),
            base_url=kwargs.get('base_url', None),
            organization=kwargs.get('organization', None),
        )

    @staticmethod
    def google_model(model_name: str ='gemini-3.0-flash', temperature: float = 0.95, **kwargs) -> ChatGoogleGenerativeAI:
        """
            Google Gemini models - Excellent for multimodal tasks and reasoning.
            Supports: gemini-2.0-flash (default), gemini-1.5-flash-latest, gemini-1.5-pro-latest, gemini-2.5-pro, etc.
            """
        LlmsHouse._ensure_api_key("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_tokens=kwargs.get('max_tokens', None),
            timeout=kwargs.get('timeout', None),
            max_retries=kwargs.get('max_retries', 2),
        )


    @staticmethod
    def anthropic_model(model_name: str, temperature: float = 0.7, **kwargs) -> ChatAnthropic:
        """
        Anthropic Claude models - Excellent for coding and reasoning.
        Supports: claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude 4 sonnet and others etc.
        """
        LlmsHouse._ensure_api_key("ANTHROPIC_API_KEY")
        return ChatAnthropic(
            model=model_name,
            temperature=temperature,
            max_tokens=kwargs.get('max_tokens', None),
            timeout=kwargs.get('timeout', None),
            max_retries=kwargs.get('max_retries', 2),
        )

    @staticmethod
    def deepseek_model(model_name: str, temperature: float = 0.7, **kwargs) -> ChatDeepSeek:
        """
        DeepSeek models - Very cost-effective, excellent for coding.
        Supports: deepseek-chat, deepseek-coder, deepseek-v3, etc.
        """
        LlmsHouse._ensure_api_key("DEEPSEEK_API_KEY")
        return ChatDeepSeek(
                    model=model_name,
                    temperature=temperature,
                    max_tokens=kwargs.get('max_tokens', None),
                    timeout=kwargs.get('timeout', None),
                    max_retries=kwargs.get('max_retries', 2),
                )

    @staticmethod
    def qwq_model(model_name: str, **kwargs) -> ChatQwQ:
        """
        QwQ models - Specialized for mathematical reasoning and complex logic.
        Supports: qwq-32b-preview, etc.
        """
        LlmsHouse._ensure_api_key("DASHSCOPE_API_KEY")
        return ChatQwQ(
                    model=model_name,
                    max_tokens=kwargs.get('max_tokens', 3000),
                    timeout=kwargs.get('timeout', None),
                    max_retries=kwargs.get('max_retries', 2),
                )
            
    @staticmethod
    def mistral_model(model_name: str, temperature: float = 0.7, **kwargs) -> ChatMistralAI:
        """
        Mistral models - Good balance of performance and cost.
        Supports: mistral-large-latest, mistral-medium, etc.
        """
        LlmsHouse._ensure_api_key("MISTRAL_API_KEY")
        return ChatMistralAI(
            model=model_name,
            temperature=temperature,
            max_retries=kwargs.get('max_retries', 2),
        )

    @staticmethod
    def perplexity_model(model_name: str, temperature: float = 0.7, **kwargs) -> ChatPerplexity:
        """
        Perplexity models - Excellent for search and research tasks.
        Supports: llama-3.1-sonar-small-128k-online, llama-3.1-sonar-large-128k-online, etc.
        """
        LlmsHouse._ensure_api_key("PERPLEXITY_API_KEY")
        return ChatPerplexity(
            model=model_name,
            temperature=temperature,
            pplx_api_key=kwargs.get('pplx_api_key', os.getenv('PERPLEXITY_API_KEY')),
        )


    @staticmethod
    def coding_model(**kwargs):
        """
        Get best coding model: Claude Sonnet 4 (hardcoded as best for coding tasks)
        """
        return LlmsHouse.anthropic_model("claude-sonnet-4-20250514", temperature=0.1, **kwargs)

    @staticmethod
    def math_model(**kwargs):
        """
        Get best math model: Gemini 2.5 Pro (hardcoded as best for mathematical reasoning)
        """
        return LlmsHouse.google_model("gemini-2.5-pro", temperature=0, **kwargs)

    @staticmethod
    def get_fallback_model(**kwargs):
        """Get fallback model when primary model fails."""
        # Access fallback_model as a class attribute
        fallback_model_name = "gemini-2.0-flash" # Hardcoded or make LlmsHouse.fallback_model a class attribute
        try:
            return LlmsHouse.google_model(fallback_model_name, **kwargs)
        except Exception as e:
            # Fallback model error logged silently (no stdout print)
            return None
    @staticmethod
    def _ensure_api_key(key_name: str):
        """Ensure API key is set."""
        if not os.getenv(key_name):
            os.environ[key_name] = getpass.getpass(f"Enter your {key_name}: ")


# Usage Examples
if __name__ == "__main__":
    # Initialize the LLM house
    # llm_house = LlmsHouse()
    
    # Example usage - Company-specific models
    # openai_model = llm_house.openai_model("gpt-4o")
    # google_model = llm_house.google_model("gemini-2.0-flash-001")
    # anthropic_model = llm_house.anthropic_model("claude-3-5-sonnet-20241022")
    # deepseek_model = llm_house.deepseek_model("deepseek-coder")
    
    # Example usage - Task-specific models (hardcoded best)
    # coding_model = llm_house.coding_model()  # Uses Claude 3.5 Sonnet
    # math_model = llm_house.math_model()      # Uses Gemini 2.5 Pro'

    model = LlmsHouse.google_model()
    msg = model.invoke("What is the capital of France?")

    print(msg.content)

    print("LlmsHouse initialized successfully!")