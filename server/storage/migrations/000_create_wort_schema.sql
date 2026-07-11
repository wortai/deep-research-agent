-- Migration: 000_create_wort_schema
-- Rebuilds WORT's application-owned storage on a fresh PostgreSQL database.
-- LangGraph owns its checkpoint tables and creates them during application setup.

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

ALTER TABLE wort.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE wort.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE wort.chat_events ENABLE ROW LEVEL SECURITY;

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
