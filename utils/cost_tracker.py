"""
Cost tracking callback for LangChain models.

Tracks token usage across all LLM providers (Google, xAI, DeepSeek, Anthropic, OpenAI)
by reading usage metadata from AIMessage responses and calculating costs from MODEL_PRICING.
"""

import logging
from typing import Any, Dict, List, Optional
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

logger = logging.getLogger(__name__)

MODEL_PRICING = {
    "deepseek-chat": {"input": 0.28, "output": 0.42},
    "deepseek-reasoner": {"input": 0.55, "output": 2.19},

    "grok-4-1-fast": {"input": 0.20, "output": 0.50},
    "grok-4.1-fast": {"input": 0.20, "output": 0.50},
    "grok-4-1-fast-reasoning": {"input": 0.20, "output": 0.50},
    "grok-4.1-fast-reasoning": {"input": 0.20, "output": 0.50},
    "grok-4": {"input": 5.50, "output": 27.50},

    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    "gemini-2.0-flash-001": {"input": 0.10, "output": 0.40},
    "gemini-3-flash": {"input": 0.50, "output": 3.00},
    "gemini-3.1-flash-lite": {"input": 0.25, "output": 1.50},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-2.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-2.5-flash": {"input": 0.15, "output": 0.60},
    "gemini-3.1-pro-preview": {"input": 1.25, "output": 5.00},
}


class CostTracker(BaseCallbackHandler):
    """
    Callback that accumulates token usage and cost across all LLM calls in a session.

    Extracts usage from three possible locations in LLMResult:
    1. llm_output['token_usage'] — OpenAI-style providers
    2. message.usage_metadata — LangChain standard (Google, xAI, Anthropic)
    3. message.response_metadata — provider-specific fallback
    """

    def __init__(self):
        super().__init__()
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_cost = 0.0

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Collect token usage when an LLM finishes generation."""
        try:
            llm_output = response.llm_output or {}
            prompt_tokens = 0
            completion_tokens = 0
            model_name = llm_output.get("model_name", "") or llm_output.get("model", "")

            token_usage = llm_output.get("token_usage", {}) or llm_output.get("usage", {})

            if token_usage:
                prompt_tokens = (
                    token_usage.get("prompt_tokens", 0)
                    or token_usage.get("input_tokens", 0)
                )
                completion_tokens = (
                    token_usage.get("completion_tokens", 0)
                    or token_usage.get("output_tokens", 0)
                )

            if not (prompt_tokens or completion_tokens):
                prompt_tokens, completion_tokens, model_name = (
                    self._extract_from_message(response, model_name)
                )

            if not (prompt_tokens or completion_tokens):
                logger.debug(
                    f"[CostTracker] No token usage found. "
                    f"llm_output keys={list(llm_output.keys())}"
                )
                return

            self.input_tokens += prompt_tokens
            self.output_tokens += completion_tokens

            cost = self._calculate_cost(model_name, prompt_tokens, completion_tokens)
            self.total_cost += cost

            logger.info(
                f"[CostTracker] model={model_name}, "
                f"input={prompt_tokens}, output={completion_tokens}, "
                f"cost=${cost:.6f}, running_total=${self.total_cost:.6f}"
            )

        except Exception as e:
            logger.error(f"[CostTracker] Error extracting usage: {e}")

    @staticmethod
    def _extract_from_message(
        response: LLMResult, fallback_model: str
    ) -> tuple[int, int, str]:
        """
        Reads usage from AIMessage.usage_metadata or response_metadata.

        LangChain chat models (ChatXAI, ChatGoogleGenerativeAI, ChatAnthropic)
        attach usage_metadata with keys 'input_tokens' and 'output_tokens'
        directly on the message object.

        Args:
            response: LLMResult containing generations.
            fallback_model: Model name discovered from llm_output.

        Returns:
            Tuple of (input_tokens, output_tokens, model_name).
        """
        if not response.generations or not response.generations[0]:
            return 0, 0, fallback_model

        message = getattr(response.generations[0][0], "message", None)
        if not message:
            return 0, 0, fallback_model

        model_name = fallback_model
        prompt_tokens = 0
        completion_tokens = 0

        usage_meta = getattr(message, "usage_metadata", None)
        if usage_meta and isinstance(usage_meta, dict):
            prompt_tokens = (
                usage_meta.get("input_tokens", 0)
                or usage_meta.get("prompt_tokens", 0)
            )
            completion_tokens = (
                usage_meta.get("output_tokens", 0)
                or usage_meta.get("completion_tokens", 0)
            )

        resp_meta = getattr(message, "response_metadata", None) or {}

        if not model_name:
            model_name = (
                resp_meta.get("model_name", "")
                or resp_meta.get("model", "")
                or resp_meta.get("model_id", "")
            )

        if not (prompt_tokens or completion_tokens) and resp_meta:
            usage_block = resp_meta.get("usage", {}) or resp_meta.get("token_usage", {})
            if usage_block:
                prompt_tokens = (
                    usage_block.get("input_tokens", 0)
                    or usage_block.get("prompt_tokens", 0)
                )
                completion_tokens = (
                    usage_block.get("output_tokens", 0)
                    or usage_block.get("completion_tokens", 0)
                )

        return prompt_tokens, completion_tokens, model_name

    def _calculate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate USD cost from model name and token counts using MODEL_PRICING."""
        if not model_name:
            return 0.0

        normalized = model_name.lower().strip()

        pricing = MODEL_PRICING.get(normalized)

        if not pricing:
            for key, val in MODEL_PRICING.items():
                if key in normalized or normalized in key:
                    pricing = val
                    break

        if not pricing:
            logger.debug(f"[CostTracker] Unknown model '{model_name}', using default pricing.")
            pricing = {"input": 0.50, "output": 1.50}

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def reset(self):
        """Reset all counters to zero."""
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_cost = 0.0

    def get_summary(self) -> Dict[str, Any]:
        """Returns accumulated usage across all LLM calls in this session."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_cost": self.total_cost,
        }
