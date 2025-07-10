
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



class LlmsHouse:
    """
    Main LLM management class providing unified access to various LLM providers.
    """
    
    def __init__(self):
        self.fallback_model = "gemini-2.0-flash-001"
    
    def openai_model(self, model_name: str, temperature: float = 1.25, **kwargs) -> ChatOpenAI:
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

    def google_model(self, model_name: str, temperature: float = 0.95, **kwargs) -> ChatGoogleGenerativeAI:
        """
        Google Gemini models - Excellent for multimodal tasks and reasoning.
        Supports: gemini-2.5-pro, gemini-2.0-flash-001, gemini-1.5-pro, etc.
        """
        self._ensure_api_key("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_tokens=kwargs.get('max_tokens', None),
            timeout=kwargs.get('timeout', None),
            max_retries=kwargs.get('max_retries', 2),
        )
    
    def anthropic_model(self, model_name: str, temperature: float = 0.7, **kwargs) -> ChatAnthropic:
        """
        Anthropic Claude models - Excellent for coding and reasoning.
        Supports: claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude 4 sonnet and others etc.
        """
        self._ensure_api_key("ANTHROPIC_API_KEY")
        return ChatAnthropic(
            model=model_name,
            temperature=temperature,
            max_tokens=kwargs.get('max_tokens', None),
            timeout=kwargs.get('timeout', None),
            max_retries=kwargs.get('max_retries', 2),
        )
    
    def deepseek_model(self, model_name: str, temperature: float = 0.7, **kwargs) -> ChatDeepSeek:
        """
        DeepSeek models - Very cost-effective, excellent for coding.
        Supports: deepseek-chat, deepseek-coder, deepseek-v3, etc.
        """
        return ChatDeepSeek(
            model=model_name,
            temperature=temperature,
            max_tokens=kwargs.get('max_tokens', None),
            timeout=kwargs.get('timeout', None),
            max_retries=kwargs.get('max_retries', 2),
        )
    
    def qwq_model(self, model_name: str, **kwargs) -> ChatQwQ:
        """
        QwQ models - Specialized for mathematical reasoning and complex logic.
        Supports: qwq-32b-preview, etc.
        """
        self._ensure_api_key("DASHSCOPE_API_KEY")
        return ChatQwQ(
            model=model_name,
            max_tokens=kwargs.get('max_tokens', 3000),
            timeout=kwargs.get('timeout', None),
            max_retries=kwargs.get('max_retries', 2),
        )
    
    def mistral_model(self, model_name: str, temperature: float = 0.7, **kwargs) -> ChatMistralAI:
        """
        Mistral models - Good balance of performance and cost.
        Supports: mistral-large-latest, mistral-medium, etc.
        """
        self._ensure_api_key("MISTRAL_API_KEY")
        return ChatMistralAI(
            model=model_name,
            temperature=temperature,
            max_retries=kwargs.get('max_retries', 2),
        )
    
    def perplexity_model(self, model_name: str, temperature: float = 0.7, **kwargs) -> ChatPerplexity:
        """
        Perplexity models - Excellent for search and research tasks.
        Supports: llama-3.1-sonar-small-128k-online, llama-3.1-sonar-large-128k-online, etc.
        """
        return ChatPerplexity(
            model=model_name,
            temperature=temperature,
            pplx_api_key=kwargs.get('pplx_api_key', os.getenv('PERPLEXITY_API_KEY')),
        )

    def coding_model(self, **kwargs):
        """
        Get best coding model: Claude Sonnet 4 (hardcoded as best for coding tasks)
        """
        return self.anthropic_model("claude-sonnet-4-20250514", temperature=0.1, **kwargs)
    
    def math_model(self, **kwargs):
        """
        Get best math model: Gemini 2.5 Pro (hardcoded as best for mathematical reasoning)
        """
        return self.google_model("gemini-2.5-pro", temperature=0, **kwargs)
    
    def get_fallback_model(self, **kwargs):
        """Get fallback model when primary model fails."""
        try:
            return self.google_model(self.fallback_model, **kwargs)
        except Exception as e:
            print(f"Fallback model failed: {e}")
            return None
    
    def _ensure_api_key(self, key_name: str):
        """Ensure API key is set."""
        if not os.getenv(key_name):
            os.environ[key_name] = getpass.getpass(f"Enter your {key_name}: ")


# Usage Examples
if __name__ == "__main__":
    # Initialize the LLM house
    llm_house = LlmsHouse()
    
    # Example usage - Company-specific models
    # openai_model = llm_house.openai_model("gpt-4o")
    # google_model = llm_house.google_model("gemini-2.0-flash-001")
    # anthropic_model = llm_house.anthropic_model("claude-3-5-sonnet-20241022")
    # deepseek_model = llm_house.deepseek_model("deepseek-coder")
    
    # Example usage - Task-specific models (hardcoded best)
    # coding_model = llm_house.coding_model()  # Uses Claude 3.5 Sonnet
    # math_model = llm_house.math_model()      # Uses Gemini 2.5 Pro
    # msg = google_model.invoke("What is the meaning of life?")
    # print(msg)

    print("LlmsHouse initialized successfully!")