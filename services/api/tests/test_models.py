from sqlalchemy import create_mock_engine

from app.models import Base

EXPECTED_TABLES = {
    "access_logs",
    "accounts",
    "admins",
    "citizens",
    "consent_records",
    "doctor_verification_events",
    "doctors",
    "emergency_profiles",
    "medical_records",
    "nfc_tags",
    "one_time_tokens",
    "refresh_sessions",
    "tag_write_versions",
}


def test_metadata_contains_the_initial_schema() -> None:
    assert set(Base.metadata.tables) == EXPECTED_TABLES


def test_schema_compiles_for_postgresql() -> None:
    statements: list[str] = []

    def capture(sql, *args, **kwargs) -> None:
        statements.append(str(sql.compile(dialect=engine.dialect)))

    engine = create_mock_engine("postgresql+psycopg://", capture)

    Base.metadata.create_all(engine)

    assert any("CREATE TABLE accounts" in statement for statement in statements)
    assert any("CREATE TABLE nfc_tags" in statement for statement in statements)
    assert any("CREATE TABLE access_logs" in statement for statement in statements)
