"""
Query Validator for Research Plans.

Enforces the hard system limit of MAX 10 queries per plan.
When a plan exceeds the limit it uses LLM regeneration (up to 2 attempts)
to produce a compliant plan before falling back to a hard trim.
"""

import logging
from typing import List
from pydantic import BaseModel, Field

from llms.llms import LlmsHouse

logger = logging.getLogger(__name__)

MAX_PLAN_QUERIES = 10
MAX_REGEN_ATTEMPTS = 2


class _CompressedPlanResult(BaseModel):
    plan: List[str] = Field(
        description=(
            f"A consolidated list of at most {MAX_PLAN_QUERIES} research queries. "
            "Merge or drop overlapping queries so the list has 10 or fewer items. "
            "Each query must be between 30 and 120 words."
        )
    )


class QueryValidator:
    """
    Validates that a research plan does not exceed MAX_PLAN_QUERIES.

    When the limit is exceeded the validator asks the LLM to consolidate
    the plan into a shorter, coherent set of queries.  If the LLM still
    produces an over-limit plan after MAX_REGEN_ATTEMPTS the list is
    hard-trimmed to the first MAX_PLAN_QUERIES entries.
    """

    def __init__(self):
        self._llm = LlmsHouse.grok_model("grok-4-1-fast-reasoning", temperature=0.7)
        self._fallback_llm = LlmsHouse.get_fallback_model(temperature=0.7)

    def is_valid(self, plan: List[str]) -> bool:
        return len(plan) <= MAX_PLAN_QUERIES

    def validate_and_fix(self, plan: List[str], original_query: str) -> List[str]:
        """
        Return a plan that satisfies the MAX_PLAN_QUERIES constraint.

        Args:
            plan:           The raw list of query strings from the planner.
            original_query: The user's original research question (context for LLM).

        Returns:
            A list with at most MAX_PLAN_QUERIES queries.
        """
        if self.is_valid(plan):
            return plan

        logger.warning(
            f"[QueryValidator] Plan has {len(plan)} queries — exceeds limit of "
            f"{MAX_PLAN_QUERIES}. Attempting LLM consolidation."
        )

        for attempt in range(1, MAX_REGEN_ATTEMPTS + 1):
            fixed = self._consolidate_with_llm(plan, original_query, attempt)
            if fixed is not None and self.is_valid(fixed):
                logger.info(
                    f"[QueryValidator] LLM consolidation succeeded on attempt {attempt} "
                    f"({len(fixed)} queries)."
                )
                return fixed
            logger.warning(
                f"[QueryValidator] Attempt {attempt} still over limit "
                f"({len(fixed) if fixed else 'error'} queries)."
            )

        trimmed = plan[:MAX_PLAN_QUERIES]
        logger.error(
            f"[QueryValidator] LLM consolidation failed after {MAX_REGEN_ATTEMPTS} "
            f"attempts. Hard-trimming to first {MAX_PLAN_QUERIES} queries."
        )
        return trimmed

    def _consolidate_with_llm(
        self, plan: List[str], original_query: str, attempt: int
    ) -> List[str] | None:
        numbered = "\n".join(f"{i+1}. {q}" for i, q in enumerate(plan))
        prompt = (
            f"The following research plan has {len(plan)} queries, but the system "
            f"hard limit is {MAX_PLAN_QUERIES}. This is attempt {attempt} of "
            f"{MAX_REGEN_ATTEMPTS} to fix it.\n\n"
            f"Original user query:\n\"{original_query}\"\n\n"
            f"Current plan ({len(plan)} queries):\n{numbered}\n\n"
            f"TASK: Consolidate this plan into at most {MAX_PLAN_QUERIES} queries "
            f"by merging or removing overlapping queries. "
            f"Preserve the most important coverage. "
            f"Every query must be 30-120 words. "
            f"Return ONLY the consolidated list — no extra text."
        )
        try:
            structured = self._llm.with_structured_output(_CompressedPlanResult)
            result = structured.invoke(prompt)
            return result.plan
        except Exception as primary_err:
            logger.warning(f"[QueryValidator] Primary LLM failed: {primary_err}")
            if self._fallback_llm:
                try:
                    structured = self._fallback_llm.with_structured_output(
                        _CompressedPlanResult
                    )
                    result = structured.invoke(prompt)
                    return result.plan
                except Exception as fallback_err:
                    logger.error(
                        f"[QueryValidator] Fallback LLM also failed: {fallback_err}"
                    )
        return None
