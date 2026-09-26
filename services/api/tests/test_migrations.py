from pathlib import Path


def test_initial_migration_defines_every_model_table() -> None:
    migration = Path("alembic/versions/20260926_01_initial_schema.py").read_text(
        encoding="utf-8"
    )

    for table in (
        "accounts",
        "citizens",
        "doctors",
        "admins",
        "doctor_verification_events",
        "consent_records",
        "emergency_profiles",
        "medical_records",
        "nfc_tags",
        "tag_write_versions",
        "refresh_sessions",
        "one_time_tokens",
        "access_logs",
    ):
        assert f"CREATE TABLE {table}" in migration
        assert f"DROP TABLE IF EXISTS {table}" in migration
