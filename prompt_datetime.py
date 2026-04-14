"""UTC 'now' string for LLM prompts (recency, search queries, routing)."""

from datetime import datetime, timezone


def now_utc_for_prompt() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
