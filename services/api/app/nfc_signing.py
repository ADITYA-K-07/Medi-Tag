import base64
import hashlib
import unicodedata
from datetime import UTC, datetime
from uuid import UUID

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

MESSAGE_PREFIX = b"MTG1\x00"
MAX_COUNTER = (1 << 32) - 1


def base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def normalize_public_text(value: str) -> str:
    """Normalize equivalent text while keeping its visible line structure."""
    normalized_lines = unicodedata.normalize("NFC", value).replace("\r\n", "\n")
    return normalized_lines.replace("\r", "\n")


def canonical_tag_message(
    *,
    tag_uuid: UUID,
    counter: int,
    profile_revision: int,
    issued_at: datetime,
    public_text: str,
) -> bytes:
    if not 0 <= counter <= MAX_COUNTER:
        raise ValueError("counter must fit in an unsigned 32-bit integer")
    if not 1 <= profile_revision <= MAX_COUNTER:
        raise ValueError("profile revision must be between 1 and 2^32 - 1")
    if issued_at.tzinfo is None or issued_at.utcoffset() is None:
        raise ValueError("issued_at must be timezone-aware")

    issued_seconds = int(issued_at.astimezone(UTC).timestamp())
    if issued_seconds < 0:
        raise ValueError("issued_at must be on or after the Unix epoch")

    text_bytes = normalize_public_text(public_text).encode("utf-8")
    text_hash = hashlib.sha256(text_bytes).digest()

    return b"".join(
        (
            MESSAGE_PREFIX,
            tag_uuid.bytes,
            counter.to_bytes(4, "big"),
            profile_revision.to_bytes(4, "big"),
            issued_seconds.to_bytes(8, "big"),
            text_hash,
        )
    )


class TagSigner:
    def __init__(self, key_id: str, private_key: Ed25519PrivateKey) -> None:
        if not key_id or len(key_id) > 40:
            raise ValueError("key_id must contain between 1 and 40 characters")
        self.key_id = key_id
        self._private_key = private_key

    @classmethod
    def from_base64_private_key(cls, key_id: str, value: str) -> "TagSigner":
        private_bytes = base64url_decode(value)
        return cls(key_id, Ed25519PrivateKey.from_private_bytes(private_bytes))

    @property
    def public_key_base64(self) -> str:
        public_bytes = self._private_key.public_key().public_bytes(
            Encoding.Raw,
            PublicFormat.Raw,
        )
        return base64url_encode(public_bytes)

    def sign(self, message: bytes) -> str:
        return base64url_encode(self._private_key.sign(message))


class TagVerifier:
    def __init__(self, public_keys: dict[str, str]) -> None:
        self._public_keys = {
            key_id: Ed25519PublicKey.from_public_bytes(base64url_decode(value))
            for key_id, value in public_keys.items()
        }

    def verify(self, key_id: str, message: bytes, signature: str) -> bool:
        public_key = self._public_keys.get(key_id)
        if public_key is None:
            return False

        try:
            public_key.verify(base64url_decode(signature), message)
        except (InvalidSignature, ValueError):
            return False
        return True
