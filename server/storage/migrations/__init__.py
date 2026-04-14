"""
Database migration runner for the wort schema.

Executes SQL files from the migrations directory in sorted order,
tracking applied migrations in wort._migrations to guarantee idempotency.

Usage:
    python -m server.storage.migrations.run_migration
"""
