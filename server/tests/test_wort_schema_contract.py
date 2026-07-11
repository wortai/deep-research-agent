from pathlib import Path


MIGRATIONS_DIR = Path(__file__).parents[1] / "storage" / "migrations"
BASE_MIGRATION = MIGRATIONS_DIR / "000_create_wort_schema.sql"


def _normalized_sql() -> str:
    return " ".join(BASE_MIGRATION.read_text(encoding="utf-8").lower().split())


def test_base_migration_precedes_oauth_migration() -> None:
    names = sorted(path.name for path in MIGRATIONS_DIR.glob("*.sql"))
    assert names[:2] == ["000_create_wort_schema.sql", "001_add_oauth_fields.sql"]


def test_base_migration_defines_wort_storage_contract() -> None:
    sql = _normalized_sql()

    for table in ("wort.users", "wort.sessions", "wort.chat_events"):
        assert f"create table if not exists {table}" in sql

    for column in (
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
        assert column in sql

    assert "references wort.users (user_id) on delete cascade" in sql
    assert "references wort.sessions (session_id) on delete cascade" in sql
    assert "unique (session_id, event_order)" in sql


def test_base_migration_keeps_browser_roles_out() -> None:
    sql = _normalized_sql()
    assert "alter table wort.users enable row level security" in sql
    assert "alter table wort.sessions enable row level security" in sql
    assert "alter table wort.chat_events enable row level security" in sql
    assert "revoke all on schema wort from public, anon, authenticated" in sql
    assert "revoke all on all tables in schema wort from public, anon, authenticated" in sql
    assert "in schema public revoke all on tables from public, anon, authenticated" in sql
