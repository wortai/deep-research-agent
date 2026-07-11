from server.storage.migrations import run_migration


def test_bootstrap_migration_state_creates_wort_before_tracking_table() -> None:
    bootstrap_sql = run_migration.BOOTSTRAP_MIGRATION_STATE

    schema_statement = "CREATE SCHEMA IF NOT EXISTS wort;"
    tracking_table_statement = "CREATE TABLE IF NOT EXISTS wort._migrations"

    assert schema_statement in bootstrap_sql
    assert tracking_table_statement in bootstrap_sql
    assert bootstrap_sql.index(schema_statement) < bootstrap_sql.index(
        tracking_table_statement
    )
