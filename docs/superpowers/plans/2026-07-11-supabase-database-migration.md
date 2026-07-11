# WORT Supabase Database Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create and verify a new Supabase PostgreSQL database that preserves WORT's application schema and LangGraph checkpoint behavior behind the existing `DATABASE_URL` interface.

**Architecture:** Keep the FastAPI backend's two existing psycopg pools: one for the private `wort` schema and one for LangGraph's `AsyncShallowPostgresSaver`. Add a reproducible base SQL migration for application tables, let LangGraph create its own public checkpoint tables, and connect the persistent Render service through Supabase's SSL session pooler.

**Tech Stack:** PostgreSQL 17, Supabase, psycopg 3, psycopg-pool, LangGraph `AsyncShallowPostgresSaver`, pytest, Render.

## Global Constraints

- Create project `WORT` in Supabase organization `madhvantyagi` (`knrmsfsfichuijrcuzbw`) and region `us-east-1`.
- This is a fresh rebuild; do not attempt to recover or invent old rows.
- Keep Google OAuth, WORT JWTs, FastAPI routes, WebSockets, frontend code, and research-agent behavior unchanged.
- Keep `wort` and LangGraph checkpoint tables unavailable to `anon` and `authenticated` Data API roles.
- Never write a database password or complete `DATABASE_URL` into Git-tracked files or tool output.
- Use Supabase session-pooler port 5432 with `sslmode=require` for the persistent Render backend.
- Let `AsyncShallowPostgresSaver.setup()` own the checkpoint table definitions.

---

## File Map

- Create `server/storage/migrations/000_create_wort_schema.sql`: authoritative, idempotent application schema and backend-only permissions.
- Modify `server/storage/migrations/run_migration.py`: bootstrap the `wort` schema before creating the migration ledger.
- Create `server/tests/test_migration_contract.py`: fast contract tests for migration ordering, required tables, columns, relationships, and permissions.
- Create `server/scripts/verify_supabase_database.py`: credential-safe LangGraph setup and checkpoint round-trip verifier.
- Modify `render.yaml`: declare `DATABASE_URL` as a dashboard-provided secret without storing its value.
- Do not modify `deep-research-agent/memory/short_term.py`: its existing setup call remains the authority for checkpoint DDL.

### Task 1: Bootstrap and define the reproducible WORT schema

**Files:**
- Create: `server/tests/test_migration_contract.py`
- Create: `server/storage/migrations/000_create_wort_schema.sql`
- Modify: `server/storage/migrations/run_migration.py:31-43`

**Interfaces:**
- Consumes: existing migration discovery ordered lexicographically by filename.
- Produces: `BOOTSTRAP_MIGRATION_STATE: str`, a base migration that creates `wort.users`, `wort.sessions`, and `wort.chat_events`, and an unchanged `run_migrations(db_url: str) -> list[str]` API.

- [ ] **Step 1: Write the failing migration-contract tests**

Create `server/tests/test_migration_contract.py`:

```python
from pathlib import Path

from server.storage.migrations import run_migration


MIGRATIONS_DIR = Path(__file__).parents[1] / "storage" / "migrations"
BASE_MIGRATION = MIGRATIONS_DIR / "000_create_wort_schema.sql"


def _normalized_sql() -> str:
    return " ".join(BASE_MIGRATION.read_text(encoding="utf-8").lower().split())


def test_migration_bootstrap_creates_schema_before_ledger() -> None:
    sql = " ".join(run_migration.BOOTSTRAP_MIGRATION_STATE.lower().split())
    assert sql.index("create schema if not exists wort") < sql.index(
        "create table if not exists wort._migrations"
    )


def test_base_migration_sorts_before_oauth_migration() -> None:
    names = sorted(path.name for path in MIGRATIONS_DIR.glob("*.sql"))
    assert names[:2] == ["000_create_wort_schema.sql", "001_add_oauth_fields.sql"]


def test_base_migration_defines_application_contract() -> None:
    sql = _normalized_sql()
    for table in ("wort.users", "wort.sessions", "wort.chat_events"):
        assert f"create table if not exists {table}" in sql

    for required_column in (
        "google_id",
        "provider",
        "credits",
        "last_login",
        "search_mode",
        "intent_type",
        "has_report",
        "input_tokens",
        "output_tokens",
        "total_cost",
        "event_order",
        "event_type",
        "metadata",
    ):
        assert required_column in sql

    assert "references wort.users (user_id) on delete cascade" in sql
    assert "references wort.sessions (session_id) on delete cascade" in sql
    assert "unique (session_id, event_order)" in sql


def test_base_migration_keeps_browser_roles_out() -> None:
    sql = _normalized_sql()
    assert "revoke all on schema wort from public, anon, authenticated" in sql
    assert "revoke all on all tables in schema wort from public, anon, authenticated" in sql
    assert "in schema public revoke all on tables from public, anon, authenticated" in sql
```

- [ ] **Step 2: Run the tests and verify the expected failure**

Run:

```bash
python -m pytest server/tests/test_migration_contract.py -q
```

Expected: collection or assertion failure because `BOOTSTRAP_MIGRATION_STATE` and `000_create_wort_schema.sql` do not exist.

- [ ] **Step 3: Fix migration-ledger bootstrapping**

Replace `CREATE_MIGRATIONS_TABLE` in `server/storage/migrations/run_migration.py` with:

```python
BOOTSTRAP_MIGRATION_STATE = """
CREATE SCHEMA IF NOT EXISTS wort;

CREATE TABLE IF NOT EXISTS wort._migrations (
    id         SERIAL PRIMARY KEY,
    filename   VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
"""
```

Update the bootstrap execution inside `run_migrations`:

```python
with conn.cursor() as cur:
    cur.execute(BOOTSTRAP_MIGRATION_STATE)
    conn.commit()
    logger.info("Migration schema and tracking table ensured")
```

- [ ] **Step 4: Add the complete base migration**

Create `server/storage/migrations/000_create_wort_schema.sql`:

```sql
BEGIN;

CREATE SCHEMA IF NOT EXISTS wort;

CREATE TABLE IF NOT EXISTS wort.users (
    user_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) NOT NULL UNIQUE,
    username      VARCHAR(100) UNIQUE,
    password_hash TEXT,
    google_id     VARCHAR(255) UNIQUE,
    provider      VARCHAR(50) NOT NULL DEFAULT 'local',
    full_name     VARCHAR(255),
    avatar_url    TEXT,
    credits       NUMERIC(12, 4) NOT NULL DEFAULT 100.0,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login    TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS wort.sessions (
    session_id    UUID PRIMARY KEY,
    user_id       UUID NOT NULL
                  REFERENCES wort.users (user_id) ON DELETE CASCADE,
    title         TEXT NOT NULL,
    search_mode   VARCHAR(50) NOT NULL DEFAULT 'deepsearch',
    intent_type   VARCHAR(50),
    has_report    BOOLEAN NOT NULL DEFAULT FALSE,
    status        VARCHAR(20) NOT NULL DEFAULT 'active',
    input_tokens  BIGINT NOT NULL DEFAULT 0,
    output_tokens BIGINT NOT NULL DEFAULT 0,
    total_cost    NUMERIC(14, 6) NOT NULL DEFAULT 0,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS wort.chat_events (
    event_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  UUID NOT NULL
                REFERENCES wort.sessions (session_id) ON DELETE CASCADE,
    event_order INTEGER NOT NULL CHECK (event_order > 0),
    event_type  VARCHAR(50) NOT NULL,
    content     TEXT,
    metadata    JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (session_id, event_order)
);

CREATE OR REPLACE FUNCTION wort.set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = ''
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS users_set_updated_at ON wort.users;
CREATE TRIGGER users_set_updated_at
BEFORE UPDATE ON wort.users
FOR EACH ROW EXECUTE FUNCTION wort.set_updated_at();

DROP TRIGGER IF EXISTS sessions_set_updated_at ON wort.sessions;
CREATE TRIGGER sessions_set_updated_at
BEFORE UPDATE ON wort.sessions
FOR EACH ROW EXECUTE FUNCTION wort.set_updated_at();

CREATE INDEX IF NOT EXISTS idx_users_provider_google_id
    ON wort.users (provider, google_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_created_at
    ON wort.sessions (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_events_session_order
    ON wort.chat_events (session_id, event_order);

REVOKE ALL ON SCHEMA wort FROM PUBLIC, anon, authenticated;
REVOKE ALL ON ALL TABLES IN SCHEMA wort FROM PUBLIC, anon, authenticated;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA wort FROM PUBLIC, anon, authenticated;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA wort FROM PUBLIC, anon, authenticated;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA wort
    REVOKE ALL ON TABLES FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA wort
    REVOKE ALL ON SEQUENCES FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA wort
    REVOKE ALL ON FUNCTIONS FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    REVOKE ALL ON TABLES FROM PUBLIC, anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    REVOKE ALL ON SEQUENCES FROM PUBLIC, anon, authenticated;

COMMIT;
```

- [ ] **Step 5: Run focused tests and static validation**

Run:

```bash
python -m pytest server/tests/test_migration_contract.py -q
python -m py_compile server/storage/migrations/run_migration.py
git diff --check
```

Expected: all migration-contract tests pass, Python compilation succeeds silently, and `git diff --check` emits no output.

- [ ] **Step 6: Commit the reproducible schema work**

```bash
git add server/storage/migrations/000_create_wort_schema.sql \
  server/storage/migrations/run_migration.py \
  server/tests/test_migration_contract.py
git commit -m "feat: add reproducible WORT database schema"
```

### Task 2: Create the Supabase project and apply the application schema

**Files:**
- No repository files changed.

**Interfaces:**
- Consumes: organization ID `knrmsfsfichuijrcuzbw` and the SQL from `000_create_wort_schema.sql` plus `001_add_oauth_fields.sql`.
- Produces: an active Supabase project ID and a verified `wort` schema.

- [ ] **Step 1: Obtain and confirm the project cost**

Call Supabase `get_cost` with organization `knrmsfsfichuijrcuzbw` and type `project`. Report the exact amount and recurrence to the user, obtain the connector's cost-confirmation ID, and pass only that ID into project creation.

Expected: a confirmation ID valid for creating one project at the stated cost.

- [ ] **Step 2: Create the project**

Call Supabase `create_project` with:

```text
name: WORT
organization_id: knrmsfsfichuijrcuzbw
region: us-east-1
confirm_cost_id: the exact ID returned by the immediately preceding cost-confirmation call
```

Poll `get_project` using the returned project ID until status is active. Do not create a second project if initialization is merely pending.

- [ ] **Step 3: Apply repository migrations in order**

Apply `server/storage/migrations/000_create_wort_schema.sql` as migration name `create_wort_schema`, followed by `server/storage/migrations/001_add_oauth_fields.sql` as `add_oauth_fields`.

Expected: both migrations are recorded successfully. The second migration remains a no-op for already-present OAuth columns but verifies backward compatibility.

- [ ] **Step 4: Verify exact columns and relationships**

Use Supabase `execute_sql` with:

```sql
SELECT table_name, column_name, data_type, udt_name, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'wort'
  AND table_name IN ('users', 'sessions', 'chat_events')
ORDER BY table_name, ordinal_position;

SELECT tc.table_name, tc.constraint_name, tc.constraint_type,
       kcu.column_name, ccu.table_name AS foreign_table_name,
       ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.key_column_usage kcu
  ON tc.constraint_schema = kcu.constraint_schema
 AND tc.constraint_name = kcu.constraint_name
LEFT JOIN information_schema.constraint_column_usage ccu
  ON tc.constraint_schema = ccu.constraint_schema
 AND tc.constraint_name = ccu.constraint_name
WHERE tc.table_schema = 'wort'
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name, kcu.ordinal_position;
```

Expected: all three tables, their primary keys, unique constraints, and both cascading foreign keys are present.

- [ ] **Step 5: Exercise the storage contract without retaining test data**

Use Supabase `execute_sql` with a transaction that always rolls back:

```sql
BEGIN;

INSERT INTO wort.users
    (user_id, google_id, email, full_name, avatar_url, username, provider, credits)
VALUES
    ('00000000-0000-0000-0000-000000000101', 'test-google-id',
     'schema-test@example.invalid', 'Schema Test', NULL, 'schema_test', 'google', 100.0);

INSERT INTO wort.sessions
    (session_id, user_id, title, search_mode)
VALUES
    ('00000000-0000-0000-0000-000000000201',
     '00000000-0000-0000-0000-000000000101',
     'Schema verification', 'deepsearch');

INSERT INTO wort.chat_events
    (event_id, session_id, event_order, event_type, content, metadata)
VALUES
    ('00000000-0000-0000-0000-000000000301',
     '00000000-0000-0000-0000-000000000201',
     1, 'user_query', 'verification', '{"search_mode":"deepsearch"}'::jsonb);

UPDATE wort.sessions
SET has_report = TRUE,
    input_tokens = input_tokens + 10,
    output_tokens = output_tokens + 20,
    total_cost = total_cost + 0.001
WHERE session_id = '00000000-0000-0000-0000-000000000201';

SELECT s.session_id, s.has_report, s.input_tokens, s.output_tokens, s.total_cost,
       e.event_order, e.event_type, e.metadata
FROM wort.sessions s
JOIN wort.chat_events e USING (session_id)
WHERE s.session_id = '00000000-0000-0000-0000-000000000201';

ROLLBACK;
```

Expected: the select returns one joined row with `has_report=true`, token counts `10` and `20`, cost `0.001`, and the JSONB metadata; no test rows remain after rollback.

- [ ] **Step 6: Run Supabase advisors**

Run both security and performance advisors for the new project. Fix only findings caused by WORT migrations. Record any Supabase-managed or informational findings separately without changing managed schemas.

### Task 3: Wire deployment configuration and verify LangGraph checkpoints

**Files:**
- Create: `server/scripts/verify_supabase_database.py`
- Modify: `render.yaml`

**Interfaces:**
- Consumes: the active project ID and its session-pooler connection string, supplied as a Render secret.
- Produces: a backend deployment using one Supabase `DATABASE_URL` for both application storage and LangGraph checkpoints.

- [ ] **Step 1: Add a secret placeholder to the Render blueprint**

Add this entry under `envVars` in `render.yaml`:

```yaml
      - key: DATABASE_URL
        sync: false
```

Do not include a value. In Render, set the secret to the Supabase session-pooler URL from the project's Connect dialog, ending with `?sslmode=require` (or `&sslmode=require` if the URL already has query parameters).

- [ ] **Step 2: Validate the deployment file and secret hygiene**

Run:

```bash
rg -n "DATABASE_URL|supabase\.co|pooler\.supabase\.com" . \
  --glob '!docs/superpowers/**' --glob '!.git/**'
git diff --check
```

Expected: tracked code contains only variable names or documented placeholder examples; no connection string containing a password appears.

- [ ] **Step 3: Add a credential-safe checkpoint verifier**

Create `server/scripts/verify_supabase_database.py`:

```python
#!/usr/bin/env python3
"""Verify Supabase connectivity and a LangGraph checkpoint round-trip."""

import asyncio
import os
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
AGENT_ROOT = PROJECT_ROOT / "deep-research-agent"
sys.path.insert(0, str(AGENT_ROOT))

from langgraph.checkpoint.base import empty_checkpoint
from memory.short_term import ShortTermMemory


async def verify() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

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
```

- [ ] **Step 4: Initialize LangGraph and run the checkpoint round-trip**

With `DATABASE_URL` present only in the process environment, run:

```bash
python server/scripts/verify_supabase_database.py
```

Expected final output: `Supabase checkpoint verification passed`. The async pool must open, `AsyncShallowPostgresSaver.setup()` must complete, and no `MemorySaver` fallback may occur.

- [ ] **Step 5: Verify LangGraph-created tables and Data API isolation**

Use Supabase `execute_sql`:

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
      'checkpoints', 'checkpoint_blobs', 'checkpoint_writes',
      'checkpoint_migrations'
  )
ORDER BY table_name;

SELECT table_name, grantee, privilege_type
FROM information_schema.role_table_grants
WHERE table_schema IN ('public', 'wort')
  AND table_name IN (
      'users', 'sessions', 'chat_events', 'checkpoints',
      'checkpoint_blobs', 'checkpoint_writes', 'checkpoint_migrations'
  )
  AND grantee IN ('anon', 'authenticated')
ORDER BY table_schema, table_name, grantee, privilege_type;
```

Expected: all LangGraph tables exist, and the grants query returns zero rows.

- [ ] **Step 6: Run final local and Supabase verification**

Run:

```bash
python -m pytest server/tests/test_migration_contract.py -q
python -m py_compile server/storage/migrations/run_migration.py \
  server/storage/database_pool.py server/scripts/verify_supabase_database.py \
  deep-research-agent/memory/short_term.py
git diff --check
git status --short
```

Then rerun Supabase security and performance advisors.

Expected: local checks pass, the Git diff contains no secret, and no unresolved advisor finding is caused by WORT-owned objects.

- [ ] **Step 7: Commit deployment configuration and verifier**

```bash
git add render.yaml server/scripts/verify_supabase_database.py
git commit -m "chore: configure Supabase database secret"
```

## Completion Evidence

The migration is complete only when all of the following are available:

- Active Supabase `WORT` project ID and `us-east-1` region confirmation.
- Recorded `create_wort_schema` and `add_oauth_fields` migrations.
- Verified `wort` columns, constraints, indexes, CRUD transaction, and browser-role isolation.
- Verified LangGraph table creation and checkpoint round-trip using the real Supabase database.
- Passing focused local tests and static checks.
- Render `DATABASE_URL` secret placeholder committed with no credential value.
- Exact disclosure of any manual Render secret step that could not be completed through available tools.
