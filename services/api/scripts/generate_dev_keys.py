"""Print fresh local encryption and signing keys without writing them to disk."""

import json

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from app.nfc_signing import base64url_encode


def main() -> None:
    private_key = Ed25519PrivateKey.generate()
    private_bytes = private_key.private_bytes(
        Encoding.Raw,
        PrivateFormat.Raw,
        NoEncryption(),
    )
    public_bytes = private_key.public_key().public_bytes(
        Encoding.Raw,
        PublicFormat.Raw,
    )

    encryption_keys = {"1": Fernet.generate_key().decode("ascii")}
    public_keys = {"pilot-1": base64url_encode(public_bytes)}

    print("FIELD_ENCRYPTION_CURRENT_VERSION=1")
    print(f"FIELD_ENCRYPTION_KEYS={json.dumps(encryption_keys)}")
    print("TAG_SIGNING_KEY_ID=pilot-1")
    print(f"TAG_SIGNING_PRIVATE_KEY={base64url_encode(private_bytes)}")
    print(f"TAG_SIGNING_PUBLIC_KEYS={json.dumps(public_keys)}")


if __name__ == "__main__":
    main()
