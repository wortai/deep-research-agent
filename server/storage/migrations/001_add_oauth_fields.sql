-- Migration: 001_add_oauth_fields
-- Adds Google OAuth support columns to wort.users.
-- Backward-compatible: only adds columns and relaxes constraints.
-- Safe to re-run: uses IF NOT EXISTS / conditional DO blocks.

BEGIN;

-- 1. Add OAuth-related columns
ALTER TABLE wort.users ADD COLUMN IF NOT EXISTS google_id   VARCHAR(255);
ALTER TABLE wort.users ADD COLUMN IF NOT EXISTS avatar_url  TEXT;
ALTER TABLE wort.users ADD COLUMN IF NOT EXISTS full_name   VARCHAR(255);

-- provider column with default 'local' for existing rows and future local-auth users
ALTER TABLE wort.users ADD COLUMN IF NOT EXISTS provider    VARCHAR(50) NOT NULL DEFAULT 'local';

-- 2. Make password_hash nullable (Google-authenticated users have no password)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'wort'
          AND table_name   = 'users'
          AND column_name  = 'password_hash'
          AND is_nullable  = 'NO'
    ) THEN
        ALTER TABLE wort.users ALTER COLUMN password_hash DROP NOT NULL;
    END IF;
END $$;

-- 3. Make username nullable (Google users may not have a traditional username;
--    it will be derived from email at account-creation time)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'wort'
          AND table_name   = 'users'
          AND column_name  = 'username'
          AND is_nullable  = 'NO'
    ) THEN
        ALTER TABLE wort.users ALTER COLUMN username DROP NOT NULL;
    END IF;
END $$;

-- 4. Unique constraint on google_id (Google's sub claim — unique per Google user)
--    Skip if constraint already exists.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'users_google_id_key'
          AND conrelid = 'wort.users'::regclass
    ) THEN
        ALTER TABLE wort.users
            ADD CONSTRAINT users_google_id_key UNIQUE (google_id);
    END IF;
END $$;

-- 5. Composite index for fast OAuth lookups: find user by (provider, google_id)
CREATE INDEX IF NOT EXISTS idx_users_provider_google_id
    ON wort.users (provider, google_id);

COMMIT;
