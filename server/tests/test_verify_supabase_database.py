import asyncio
import importlib.util
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "verify_supabase_database.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("verify_supabase_database", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_verifier_requires_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    module = _load_module()

    with pytest.raises(RuntimeError, match="DATABASE_URL is required"):
        asyncio.run(module.verify())
