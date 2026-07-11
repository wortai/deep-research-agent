# WORT Supabase Database Migration Design

## Goal

Replace the unavailable Google Cloud PostgreSQL database with a new Supabase PostgreSQL project named `WORT` in organization `madhvantyagi`, region `us-east-1`, without changing WORT's application-facing storage behavior.

This is a fresh database rebuild. No old rows or checkpoints will be copied because the former database is no longer accessible.

## Boundaries

WORT has two database-owned areas:

1. The private `wort` schema stores users, research sessions, and replayable frontend chat events.
2. LangGraph owns its checkpoint tables and creates them through `AsyncShallowPostgresSaver.setup()`.

The frontend will continue using FastAPI and WebSockets. It will not connect directly to Supabase. Google OAuth and WORT-issued JWT behavior will not change.

## Connection Architecture

The backend will retain its existing `DATABASE_URL` contract, `psycopg` drivers, and async connection pools. Runtime configuration will use Supabase's session pooler on port 5432 with SSL required. Session mode is appropriate for the persistent Render backend and supports IPv4 networks and normal PostgreSQL session behavior.

No Supabase client SDK is required.

## Application Schema

Create a versioned base migration that defines:

### `wort.users`

- UUID primary key
- Email and username identity fields with uniqueness where required by current authentication queries
- Nullable password hash for Google-authenticated users
- Google ID, provider, full name, and avatar URL fields
- Credit balance
- Creation, update, and last-login timestamps
- Unique Google ID and provider/Google ID lookup index

### `wort.sessions`

- UUID primary key equal to the LangGraph `thread_id`
- UUID foreign key to `wort.users`
- Title, search mode, intent type, report flag, and lifecycle status
- Input-token, output-token, and total-cost accounting fields
- Creation and update timestamps
- Index supporting newest-first session listing by user

### `wort.chat_events`

- UUID primary key
- UUID foreign key to `wort.sessions`, deleted with its session
- Per-session event order
- Event type, nullable text content, and JSONB metadata
- Creation timestamp
- Unique constraint on `(session_id, event_order)` and chronological lookup index

An update trigger will maintain `updated_at` where the application expects it. The migration will be idempotent and suitable for both the Supabase project and repository migration runner.

## LangGraph Checkpoints

Do not hand-maintain LangGraph table definitions. After the application receives the Supabase `DATABASE_URL`, `AsyncShallowPostgresSaver.setup()` will create and manage its expected checkpoint tables, including checkpoints, blobs, writes, and migration metadata.

The verification will confirm a checkpoint can be written and retrieved using a thread UUID. Application session IDs and LangGraph thread IDs remain identical.

## Security

- Keep `wort` outside the exposed Data API schemas.
- Revoke `anon` and `authenticated` access to `wort`.
- Ensure future application and LangGraph tables are not automatically granted to browser-facing roles.
- Keep database credentials exclusively in backend environment configuration.
- Do not add a publishable key or service-role key to the frontend.
- Run Supabase security and performance advisors after DDL changes.

The backend connects with a privileged PostgreSQL connection and remains responsible for authenticating users and enforcing ownership in its existing parameterized SQL queries.

## Repository Changes

Limit implementation changes to database-related files:

- Add the missing base migration under `server/storage/migrations/`.
- Preserve the existing OAuth migration, adjusting ordering or idempotency only if the new base migration makes that necessary.
- Add safe deployment configuration/documentation for the Supabase `DATABASE_URL` without storing credentials.
- Add focused schema and storage tests if the existing test layout supports them.

No frontend components, agent prompts, graph nodes, or research logic will be changed.

## Verification

1. Confirm the Supabase project reaches an active state.
2. Apply the base application-schema migration.
3. Inspect columns, types, defaults, constraints, foreign keys, and indexes.
4. Exercise user, session, and chat-event create/read/update/delete behavior inside a rollback-safe test transaction.
5. Run LangGraph setup and verify checkpoint persistence and retrieval.
6. Run Supabase security and performance advisors and address migration-related findings.
7. Run relevant local tests and static checks.
8. Confirm no secrets are present in Git changes.

## Rollout and Failure Handling

The existing application will not be pointed at Supabase until schema checks pass. If project creation or migration fails, no Google Cloud state is affected because it is already unavailable, and the repository retains an idempotent migration that can be safely reapplied after correction.

The final deployment handoff will identify the exact backend environment variable that must be set and any step that cannot be completed automatically.
