-- Migration: 002_enable_wort_rls
-- Defense in depth for the private WORT application schema.
-- The backend connects as the database owner; browser-facing roles retain no grants.

BEGIN;

ALTER TABLE wort.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE wort.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE wort.chat_events ENABLE ROW LEVEL SECURITY;

COMMIT;
