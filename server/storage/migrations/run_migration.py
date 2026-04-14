#!/usr/bin/env python3
"""
Migration runner for the wort schema.

Executes SQL migration files from the migrations directory in sorted order,
tracking which migrations have been applied in wort._migrations.

Uses psycopg (v3) in synchronous mode — no async ceremony needed for
a one-time schema migration script.

Usage:
    # From the WORT project root:
    python -m server.storage.migrations.run_migration

Environment:
    DATABASE_URL — PostgreSQL connection string (required).
                   Falls back to deep-research-agent/.env if not in env.
"""

import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).resolve().parent

CREATE_MIGRATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS wort._migrations (
    id         SERIAL PRIMARY KEY,
    filename   VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
"""


def _resolve_database_url() -> str:
    """Resolve DATABASE_URL from env or .env file."""
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    # Try loading from deep-research-agent/.env
    project_root = Path(__file__).resolve().parents[3]  # WORT/
    env_path = project_root / "deep-research-agent" / ".env"
    if env_path.exists():
        from dotenv import load_dotenv

        load_dotenv(env_path, override=False)
        db_url = os.getenv("DATABASE_URL")

    if not db_url:
        logger.error(
            "DATABASE_URL not found. Set it in env or deep-research-agent/.env"
        )
        sys.exit(1)

    return db_url


def _discover_migrations() -> list[Path]:
    """Return sorted list of .sql migration files in the migrations directory."""
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    return files


def _get_applied(cur: psycopg.Cursor) -> set[str]:
    """Return the set of already-applied migration filenames."""
    cur.execute("SELECT filename FROM wort._migrations")
    return {row[0] for row in cur.fetchall()}


def run_migrations(db_url: str) -> list[str]:
    """
    Execute all pending migrations in order.

    Returns:
        List of filenames that were applied in this run.
    """
    migrations = _discover_migrations()
    if not migrations:
        logger.info("No migration files found in %s", MIGRATIONS_DIR)
        return []

    applied_names: list[str] = []

    with psycopg.connect(db_url) as conn:
        # Ensure the tracking table exists
        with conn.cursor() as cur:
            cur.execute(CREATE_MIGRATIONS_TABLE)
            conn.commit()
            logger.info("Migration tracking table ensured")

        # Check which migrations are already applied
        with conn.cursor() as cur:
            already_applied = _get_applied(cur)
        logger.info(
            "Already applied: %s", already_applied if already_applied else "(none)"
        )

        # Execute pending migrations
        for migration_path in migrations:
            filename = migration_path.name

            if filename in already_applied:
                logger.info("Skipping (already applied): %s", filename)
                continue

            sql = migration_path.read_text(encoding="utf-8")
            logger.info("Applying migration: %s", filename)

            with conn.cursor() as cur:
                try:
                    cur.execute(sql)
                    # The SQL file contains its own BEGIN/COMMIT, but psycopg
                    # auto-starts a transaction. Record the migration after
                    # successful execution.
                    cur.execute(
                        "INSERT INTO wort._migrations (filename) VALUES (%s)",
                        (filename,),
                    )
                    conn.commit()
                    applied_names.append(filename)
                    logger.info("Successfully applied: %s", filename)
                except Exception:
                    conn.rollback()
                    logger.exception("Failed to apply migration: %s", filename)
                    raise

    return applied_names


def main() -> None:
    """Entry point for standalone execution."""
    db_url = _resolve_database_url()
    logger.info("Connecting to database...")

    applied = run_migrations(db_url)

    if applied:
        logger.info("Applied %d migration(s): %s", len(applied), applied)
    else:
        logger.info("No new migrations to apply")

    # Quick verification: show current wort.users columns
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT column_name, data_type, is_nullable, column_default,
                       character_maximum_length
                FROM information_schema.columns
                WHERE table_schema = 'wort' AND table_name = 'users'
                ORDER BY ordinal_position
                """
            )
            logger.info("Current wort.users schema:")
            for row in cur.fetchall():
                logger.info(
                    "  %-20s %-25s nullable=%-3s default=%s",
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                )


if __name__ == "__main__":
    main()
