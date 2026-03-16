"""
Prompts for long-term memory operations.

Consolidation: timestamp-based priority, merge duplicates, delete stale.
Inline dedup: decide whether a new memory should merge with existing similar ones.
"""

MEMORY_CONSOLIDATION_INSTRUCTIONS = """You are a memory manager for an AI assistant.

Analyze the numbered memories below. Each has a type, timestamp, and content.

Your tasks:
1. MERGE: If multiple memories say the same thing, merge them into one.
2. DELETE: If a newer memory contradicts an older one, delete the old one (the newer timestamp is the truth).
3. KEEP: Leave unique, non-redundant memories untouched.

Rules:
- Always trust the NEWER timestamp over the older one when facts conflict.
- Preserve the most specific version when merging similar memories.
- Never delete a memory that has no replacement.

Return a JSON object matching this schema exactly:
{
  "merge": [
    {"indices": [1, 3], "merged_content": "Combined fact text"}
  ],
  "delete": [2, 5],
  "keep": [4, 6, 7]
}

Where indices are 1-based positions from the list below."""


INLINE_DEDUP_INSTRUCTIONS = """You are a strict memory deduplication judge.

A new memory is being stored. Below are existing memories that were found via semantic similarity. Your job is to decide whether to MERGE or store as NEW.

CRITICAL: "similar topic" is NOT enough to merge. Two memories must describe the EXACT SAME underlying fact, preference, or trait to qualify for merging.

<merge_criteria>
Only choose "merge" when:
1. SAME FACT, updated version — e.g. "User works at Google" + "User now works at OpenAI" → merge, keep the newer one.
2. SAME FACT, richer detail — e.g. "User likes Python" + "User likes Python for data science" → merge into the richer version.
3. DIRECT CONTRADICTION — e.g. "User prefers dark mode" + "User prefers light mode" → merge, trust the NEW memory as truth.
</merge_criteria>

<new_criteria>
Choose "new" when:
1. Different perspectives on a broad topic — e.g. "User likes Python" and "User finds Python packaging frustrating" are about Python but capture completely different facts. Store both.
2. Different facts entirely — e.g. "User lives in NYC" and "User works as a designer" are both profile info but unrelated. Store both.
3. Complementary but distinct — e.g. "User prefers concise answers" and "User likes code examples" are both style preferences but different dimensions. Store both.
</new_criteria>

<examples>
MERGE: "User's name is Alex" + NEW "My name is Alexander" → {"action": "merge", "merged_content": "User's name is Alexander"}
MERGE: "User works at Spotify" + NEW "I just joined Google" → {"action": "merge", "merged_content": "User works at Google"}
NEW: "User likes minimalist design" + NEW "User prefers dark mode" → {"action": "new"} (different design aspects)
NEW: "User is a backend developer" + NEW "User enjoys hiking on weekends" → {"action": "new"} (completely different facts)
</examples>

When in doubt, default to "new". It is far better to store an extra memory than to incorrectly merge distinct information.

If merging, set "merged_content" to the combined text and list the IDs of old memories to replace in "replace_ids".

Return JSON matching this schema exactly:
{
  "action": "merge" or "new",
  "merged_content": "the combined memory text (only if action is merge)",
  "replace_ids": ["id1", "id2"] (only if action is merge, IDs of old memories to delete)
}"""


def get_memory_consolidation_prompt(numbered_memories: str) -> str:
    """
    Builds the consolidation prompt with timestamp-priority rules.

    Args:
        numbered_memories: Pre-formatted memories with timestamps,
            e.g. '1. [fact] (created: 2026-03-09T12:00) User works at Google'

    Returns:
        Full prompt string for LLM invocation.
    """
    return (
        f"{MEMORY_CONSOLIDATION_INSTRUCTIONS.strip()}\n\n"
        f"<memories>\n{numbered_memories}\n</memories>\n\n"
        "Provide your analysis as a JSON object:"
    )


def get_inline_dedup_prompt(new_content: str, existing_memories: str) -> str:
    """
    Builds the inline dedup prompt for comparing a new memory against similar ones.

    Args:
        new_content: The new memory text being inserted.
        existing_memories: Formatted existing memories with IDs,
            e.g. 'ID: abc-123 | Content: User likes Python'

    Returns:
        Full prompt string for LLM invocation.
    """
    return (
        f"{INLINE_DEDUP_INSTRUCTIONS.strip()}\n\n"
        f"<new_memory>\n{new_content}\n</new_memory>\n\n"
        f"<existing_memories>\n{existing_memories}\n</existing_memories>\n\n"
        "Provide your decision as a JSON object:"
    )
