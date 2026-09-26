import json
from dataclasses import dataclass
from typing import Any

from cryptography.fernet import Fernet, InvalidToken


class DecryptionError(ValueError):
    """Raised when encrypted application data cannot be authenticated."""


@dataclass(frozen=True)
class EncryptedField:
    ciphertext: bytes
    key_version: int


class FieldEncryptor:
    """Encrypt sensitive fields while retaining explicit key-version metadata."""

    def __init__(self, keys: dict[int, str], current_version: int) -> None:
        if current_version not in keys:
            raise ValueError("current encryption key version is not configured")
        if any(version < 1 for version in keys):
            raise ValueError("encryption key versions must be positive")

        self._keys = {
            version: Fernet(key.encode("ascii")) for version, key in keys.items()
        }
        self.current_version = current_version

    def encrypt_text(self, value: str) -> EncryptedField:
        ciphertext = self._keys[self.current_version].encrypt(value.encode("utf-8"))
        return EncryptedField(ciphertext, self.current_version)

    def decrypt_text(self, value: EncryptedField) -> str:
        key = self._keys.get(value.key_version)
        if key is None:
            raise DecryptionError(
                f"unknown encryption key version: {value.key_version}"
            )

        try:
            return key.decrypt(value.ciphertext).decode("utf-8")
        except (InvalidToken, UnicodeDecodeError) as error:
            raise DecryptionError(
                "encrypted value could not be authenticated"
            ) from error

    def encrypt_json(self, value: Any) -> EncryptedField:
        serialized = json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        return self.encrypt_text(serialized)

    def decrypt_json(self, value: EncryptedField) -> Any:
        try:
            return json.loads(self.decrypt_text(value))
        except json.JSONDecodeError as error:
            raise DecryptionError("decrypted value is not valid JSON") from error
