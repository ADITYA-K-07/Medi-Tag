from app.config import Settings


def test_settings_accept_versioned_key_maps() -> None:
    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://example",
        redis_url="redis://example",
        field_encryption_current_version=2,
        field_encryption_keys={1: "old", 2: "current"},
        tag_signing_key_id="pilot-1",
        tag_signing_private_key="private",
        tag_signing_public_keys={"pilot-1": "public"},
    )

    assert settings.field_encryption_current_version == 2
    assert settings.field_encryption_keys[1] == "old"


def test_settings_parse_key_maps_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://example")
    monkeypatch.setenv("REDIS_URL", "redis://example")
    monkeypatch.setenv("FIELD_ENCRYPTION_CURRENT_VERSION", "1")
    monkeypatch.setenv("FIELD_ENCRYPTION_KEYS", '{"1":"encryption-key"}')
    monkeypatch.setenv("TAG_SIGNING_KEY_ID", "pilot-1")
    monkeypatch.setenv("TAG_SIGNING_PRIVATE_KEY", "private")
    monkeypatch.setenv(
        "TAG_SIGNING_PUBLIC_KEYS",
        '{"pilot-1":"public"}',
    )

    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.field_encryption_keys == {1: "encryption-key"}
    assert settings.tag_signing_public_keys == {"pilot-1": "public"}
