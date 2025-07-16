"""
LLM client for the Gap Question Generator system.
"""

import os
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from researcher.gap_questions.monitoring import ExecutionMonitor


class GeminiLLMClient:
    """Gemini LLM client with smart model selection and logging"""
    
    def __init__(self, api_key: str = None, monitor: ExecutionMonitor = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.monitor = monitor
        
        if not self.api_key or self.api_key == "your_google_api_key_here":
            raise ValueError("Set GOOGLE_API_KEY in .env file")
        
        self.thinking_model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-thinking-exp",
            google_api_key=self.api_key,
            temperature=0.1
        )
        
        self.analysis_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=self.api_key,
            temperature=0.2
        )
        
        self.generation_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=self.api_key,
            temperature=0.3
        )
    
    def _select_model(self, prompt: str):
        """Select appropriate model based on prompt content"""
        prompt_lower = prompt.lower()
        if any(k in prompt_lower for k in ["analyze", "evaluate", "assess"]):
            return self.thinking_model
        elif any(k in prompt_lower for k in ["can_answer", "missing_info"]):
            return self.analysis_model
        else:
            return self.generation_model
    
    def generate(self, prompt: str, context: str = "general") -> str:
        """Generate response with logging"""
        try:
            model = self._select_model(prompt)
            response = model.invoke([HumanMessage(content=prompt)])
            result = response.content
            
            # Log interaction if monitor available
            if self.monitor:
                self.monitor.log_llm_interaction(prompt, result, context)
            
            return result
        except Exception as e:
            raise Exception(f"Gemini API failed: {str(e)}")