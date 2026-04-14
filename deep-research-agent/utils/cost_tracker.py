"""
Cost tracking callback for LangChain models.

Tracks token usage across all LLM providers (Google, xAI, DeepSeek, Anthropic, OpenAI)
by reading usage metadata from AIMessage responses and calculating costs from MODEL_PRICING.

Provides per-call records, per-model aggregation, and a formatted ASCII summary table.
"""

import logging
import threading
from datetime import datetime, timezone
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
    "qwen/qwen3-235b-a22b": {"input": 0.20, "output": 0.60},
    "qwen3-235b-a22b": {"input": 0.20, "output": 0.60},
}

# ---------------------------------------------------------------------------
# Formatted table constants (fixed-width columns for alignment)
# ---------------------------------------------------------------------------
# Column widths: Model=25, Calls=5, Input=8, Output=8, Cost=$+5
# Total inner content between ║ borders = 65 characters

_TABLE_TOP = "╔═════════════════════════════════════════════════════════════════╗"
_TABLE_BOT = "╚═════════════════════════════════════════════════════════════════╝"
_TABLE_TITLE = "║                    LLM COST SUMMARY                             ║"
_TABLE_HEADER_SEP = (
    "╠═════════════════════════════════════════════════════════════════╣"
)
_TABLE_ROW_SEP = "╠──────────────────────────┼───────┼──────────┼──────────┼────────╣"
_DATA_ROW_FMT = "║ {:<25}│ {:>5} │ {:>8,} │ {:>8,} │ ${:>5.3f} ║"
_HEADER_ROW_FMT = "║ {:<25}│ {:>5} │ {:>8} │ {:>8} │ {:>6} ║"


class CostTracker(BaseCallbackHandler):
    """
    Callback that accumulates token usage and cost across all LLM calls in a session.

    Extracts usage from three possible locations in LLMResult:
    1. llm_output['token_usage'] — OpenAI-style providers
    2. message.usage_metadata — LangChain standard (Google, xAI, Anthropic)
    3. message.response_metadata — provider-specific fallback

    Thread-safe: all mutable state is protected by an internal lock.
    """

    def __init__(self):
        super().__init__()
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_cost = 0.0
        self._call_records: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Callback entry point
    # ------------------------------------------------------------------

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Collect token usage when an LLM finishes generation."""
        try:
            llm_output = response.llm_output or {}
            prompt_tokens = 0
            completion_tokens = 0
            model_name = llm_output.get("model_name", "") or llm_output.get("model", "")

            token_usage = llm_output.get("token_usage", {}) or llm_output.get(
                "usage", {}
            )

            if token_usage:
                prompt_tokens = token_usage.get("prompt_tokens", 0) or token_usage.get(
                    "input_tokens", 0
                )
                completion_tokens = token_usage.get(
                    "completion_tokens", 0
                ) or token_usage.get("output_tokens", 0)

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

            cost = self._calculate_cost(model_name, prompt_tokens, completion_tokens)
            timestamp = datetime.now(timezone.utc).isoformat()

            with self._lock:
                self.input_tokens += prompt_tokens
                self.output_tokens += completion_tokens
                self.total_cost += cost
                self._call_records.append(
                    {
                        "model": model_name or "unknown",
                        "input_tokens": prompt_tokens,
                        "output_tokens": completion_tokens,
                        "cost": cost,
                        "timestamp": timestamp,
                    }
                )

            logger.info(
                f"[CostTracker] model={model_name}, "
                f"input={prompt_tokens}, output={completion_tokens}, "
                f"cost=${cost:.6f}, running_total=${self.total_cost:.6f}"
            )

        except Exception as e:
            logger.error(f"[CostTracker] Error extracting usage: {e}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

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
            prompt_tokens = usage_meta.get("input_tokens", 0) or usage_meta.get(
                "prompt_tokens", 0
            )
            completion_tokens = usage_meta.get("output_tokens", 0) or usage_meta.get(
                "completion_tokens", 0
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
                prompt_tokens = usage_block.get("input_tokens", 0) or usage_block.get(
                    "prompt_tokens", 0
                )
                completion_tokens = usage_block.get(
                    "output_tokens", 0
                ) or usage_block.get("completion_tokens", 0)

        return prompt_tokens, completion_tokens, model_name

    def _calculate_cost(
        self, model_name: str, input_tokens: int, output_tokens: int
    ) -> float:
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
            logger.debug(
                f"[CostTracker] Unknown model '{model_name}', using default pricing."
            )
            pricing = {"input": 0.50, "output": 1.50}

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    @staticmethod
    def _compute_breakdown(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Pure function: groups call records by model and computes subtotals."""
        breakdown: Dict[str, Dict[str, Any]] = {}

        for record in records:
            model = record["model"]
            if model not in breakdown:
                breakdown[model] = {
                    "calls": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost": 0.0,
                }
            entry = breakdown[model]
            entry["calls"] += 1
            entry["input_tokens"] += record["input_tokens"]
            entry["output_tokens"] += record["output_tokens"]
            entry["cost"] += record["cost"]

        for entry in breakdown.values():
            entry["cost"] = round(entry["cost"], 6)

        return breakdown

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_model_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """Groups all call records by model and returns per-model subtotals.

        Returns:
            Dict mapping model name to {
                "calls": int,
                "input_tokens": int,
                "output_tokens": int,
                "cost": float,
            }
        """
        with self._lock:
            records = list(self._call_records)
        return self._compute_breakdown(records)

    def get_summary(self) -> Dict[str, Any]:
        """Returns accumulated usage across all LLM calls in this session.

        Backward compatible: retains input_tokens, output_tokens, total_cost keys.
        Also includes per-call list and per-model breakdown.
        """
        with self._lock:
            calls_snapshot = list(self._call_records)
            total_input = self.input_tokens
            total_output = self.output_tokens
            total_cost = self.total_cost

        return {
            "input_tokens": total_input,
            "output_tokens": total_output,
            "total_cost": total_cost,
            "total_calls": len(calls_snapshot),
            "calls": calls_snapshot,
            "by_model": self._compute_breakdown(calls_snapshot),
        }

    def format_summary(self) -> str:
        """Returns a formatted ASCII table showing per-model cost breakdown.

        Models are sorted by cost descending. Model names longer than 25
        characters are truncated to fit the column width.
        """
        breakdown = self.get_model_breakdown()
        if not breakdown:
            return "No LLM calls recorded."

        total_calls = sum(s["calls"] for s in breakdown.values())

        lines = [
            _TABLE_TOP,
            _TABLE_TITLE,
            _TABLE_HEADER_SEP,
            _HEADER_ROW_FMT.format("Model", "Calls", "Input", "Output", "Cost"),
            _TABLE_ROW_SEP,
        ]

        for model, stats in sorted(
            breakdown.items(), key=lambda x: x[1]["cost"], reverse=True
        ):
            lines.append(
                _DATA_ROW_FMT.format(
                    model[:25],
                    stats["calls"],
                    stats["input_tokens"],
                    stats["output_tokens"],
                    stats["cost"],
                )
            )

        lines.append(_TABLE_ROW_SEP)
        lines.append(
            _DATA_ROW_FMT.format(
                "TOTAL",
                total_calls,
                self.input_tokens,
                self.output_tokens,
                self.total_cost,
            )
        )
        lines.append(_TABLE_BOT)

        return "\n".join(lines)

    def reset(self):
        """Reset all counters and call records to zero."""
        with self._lock:
            self.input_tokens = 0
            self.output_tokens = 0
            self.total_cost = 0.0
            self._call_records.clear()
