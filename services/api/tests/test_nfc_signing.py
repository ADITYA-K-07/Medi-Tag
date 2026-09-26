from datetime import UTC, datetime
from uuid import UUID

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.nfc_signing import (
    TagSigner,
    TagVerifier,
    base64url_encode,
    canonical_tag_message,
)

PRIVATE_KEY = "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8"
PUBLIC_KEY = "A6EHv_POEL4dcN0Y50vAmWfk1jCbpQ1fHdyGZBJVMbg"
EXPECTED_MESSAGE_HEX = (
    "4d5447310001890f4782a87c9eb94af47d7c645abc0000000700000003"
    "00000000677485806f29c16f78f4c54d25284058f8b2bdb5efe15238f47d0551"
    "09bf92ebb3992e8d"
)
EXPECTED_SIGNATURE = (
    "7CW9k7dHJJtyzyMDvbPSBnLwVjwc0jQ5EEmtNiJqSkfuShjcqX4bJOh3VeDXlLUi"
    "hq1qh3KtHDmtgSXs_c26BA"
)
PUBLIC_TEXT = "Anita Sharma\n+919876543210\nO+\nPenicillin\nEpilepsy"


def message(public_text: str = PUBLIC_TEXT) -> bytes:
    return canonical_tag_message(
        tag_uuid=UUID("01890f47-82a8-7c9e-b94a-f47d7c645abc"),
        counter=7,
        profile_revision=3,
        issued_at=datetime(2025, 1, 1, tzinfo=UTC),
        public_text=public_text,
    )


def test_fixed_signing_vector() -> None:
    signer = TagSigner.from_base64_private_key("pilot-1", PRIVATE_KEY)

    assert signer.public_key_base64 == PUBLIC_KEY
    assert message().hex() == EXPECTED_MESSAGE_HEX
    assert signer.sign(message()) == EXPECTED_SIGNATURE


def test_verifier_accepts_authentic_and_rejects_changed_text() -> None:
    verifier = TagVerifier({"pilot-1": PUBLIC_KEY})

    assert verifier.verify("pilot-1", message(), EXPECTED_SIGNATURE)
    assert not verifier.verify(
        "pilot-1",
        message("Anita Sharma\n+919876543210\nA+\nPenicillin\nEpilepsy"),
        EXPECTED_SIGNATURE,
    )
    assert not verifier.verify("unknown-key", message(), EXPECTED_SIGNATURE)


def test_equivalent_unicode_and_newlines_have_one_signature_input() -> None:
    composed = message("José\r\n+919876543210\r\nO+\r\n-\r\n-")
    decomposed = message("Jose\u0301\n+919876543210\nO+\n-\n-")

    assert composed == decomposed


def test_test_private_key_constant_is_raw_ed25519_seed() -> None:
    expected = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    expected_public = expected.public_key()

    assert base64url_encode(bytes(range(32))) == PRIVATE_KEY
    assert expected_public is not None
