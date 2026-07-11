#!/usr/bin/env python3
"""Verify Supabase connectivity and a LangGraph checkpoint round-trip."""

import asyncio
import os
import sys
import uuid
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
AGENT_ROOT = PROJECT_ROOT / "deep-research-agent"


async def verify() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    sys.path.insert(0, str(AGENT_ROOT))
    from langgraph.checkpoint.base import empty_checkpoint
    from memory.short_term import ShortTermMemory

    thread_id = f"supabase-verification-{uuid.uuid4()}"
    config = {
        "configurable": {
            "thread_id": thread_id,
            "checkpoint_ns": "",
        }
    }
    memory = ShortTermMemory(database_url)

    try:
        await memory.initialize()
        if not memory._is_async:
            raise RuntimeError("Postgres initialization fell back to MemorySaver")

        checkpoint = empty_checkpoint()
        checkpoint["channel_values"] = {"verification": "supabase"}
        checkpoint["channel_versions"] = {"verification": "1"}
        checkpoint["versions_seen"] = {}

        saved_config = await memory.checkpointer.aput(
            config,
            checkpoint,
            {"source": "input", "step": 0, "parents": {}},
            {"verification": "1"},
        )
        saved = await memory.checkpointer.aget_tuple(saved_config)
        if saved is None:
            raise RuntimeError("Checkpoint was not returned")
        if saved.checkpoint["channel_values"].get("verification") != "supabase":
            raise RuntimeError("Checkpoint payload did not round-trip")

        await memory.checkpointer.adelete_thread(thread_id)
        print("Supabase checkpoint verification passed")
    finally:
        await memory.shutdown()


if __name__ == "__main__":
    asyncio.run(verify())
