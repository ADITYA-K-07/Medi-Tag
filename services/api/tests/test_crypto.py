import pytest
from cryptography.fernet import Fernet

from app.crypto import DecryptionError, EncryptedField, FieldEncryptor


def key() -> str:
    return Fernet.generate_key().decode("ascii")


def test_encrypts_and_decrypts_unicode_json() -> None:
    encryptor = FieldEncryptor({1: key()}, current_version=1)
    original = {
        "allergies": ["Penicillin", "Pollen"],
        "name": "Anita शर्मा",
    }

    encrypted = encryptor.encrypt_json(original)

    assert encrypted.key_version == 1
    assert b"Anita" not in encrypted.ciphertext
    assert encryptor.decrypt_json(encrypted) == original


def test_old_values_remain_readable_after_key_rotation() -> None:
    old_key = key()
    old_encryptor = FieldEncryptor({1: old_key}, current_version=1)
    encrypted = old_encryptor.encrypt_text("medical detail")

    rotated = FieldEncryptor({1: old_key, 2: key()}, current_version=2)

    assert rotated.decrypt_text(encrypted) == "medical detail"
    assert rotated.encrypt_text("new detail").key_version == 2


def test_rejects_tampered_ciphertext() -> None:
    encryptor = FieldEncryptor({1: key()}, current_version=1)
    encrypted = encryptor.encrypt_text("sensitive")
    tampered = EncryptedField(encrypted.ciphertext[:-1] + b"x", 1)

    with pytest.raises(DecryptionError):
        encryptor.decrypt_text(tampered)


def test_rejects_unknown_key_version() -> None:
    encryptor = FieldEncryptor({1: key()}, current_version=1)

    with pytest.raises(DecryptionError, match="unknown encryption key version"):
        encryptor.decrypt_text(EncryptedField(b"not-used", 9))
