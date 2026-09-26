from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def uuid_column(*, primary_key: bool = False) -> Mapped[UUID]:
    return mapped_column(
        default=uuid4,
        primary_key=primary_key,
        server_default=text("gen_random_uuid()"),
    )


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Account(TimestampMixin, Base):
    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint(
            "role IN ('citizen', 'doctor', 'admin')",
            name="ck_accounts_role",
        ),
    )

    id: Mapped[UUID] = uuid_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    mfa_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    mfa_secret_ciphertext: Mapped[bytes | None] = mapped_column(LargeBinary)
    mfa_key_version: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )


class Citizen(TimestampMixin, Base):
    __tablename__ = "citizens"

    id: Mapped[UUID] = uuid_column(primary_key=True)
    account_id: Mapped[UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date)


class Doctor(TimestampMixin, Base):
    __tablename__ = "doctors"
    __table_args__ = (
        CheckConstraint(
            "verification_status IN "
            "('pending', 'verified', 'rejected', 'suspended')",
            name="ck_doctors_verification_status",
        ),
        UniqueConstraint(
            "medical_council",
            "license_number",
            name="uq_doctors_council_license",
        ),
    )

    id: Mapped[UUID] = uuid_column(primary_key=True)
    account_id: Mapped[UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    medical_council: Mapped[str] = mapped_column(String(120), nullable=False)
    license_number: Mapped[str] = mapped_column(String(80), nullable=False)
    verification_status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        server_default=text("'pending'"),
    )
    verification_document_key: Mapped[str | None] = mapped_column(Text)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Admin(TimestampMixin, Base):
    __tablename__ = "admins"

    id: Mapped[UUID] = uuid_column(primary_key=True)
    account_id: Mapped[UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)


class DoctorVerificationEvent(Base):
    __tablename__ = "doctor_verification_events"
    __table_args__ = (
        CheckConstraint(
            "decision IN ('submitted', 'registry_match', 'approved', 'rejected')",
            name="ck_doctor_verification_events_decision",
        ),
        Index(
            "ix_doctor_verification_events_doctor_created",
            "doctor_id",
            "created_at",
        ),
    )

    id: Mapped[UUID] = uuid_column(primary_key=True)
    doctor_id: Mapped[UUID] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False,
    )
    reviewer_account_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("accounts.id", ondelete="SET NULL")
    )
    decision: Mapped[str] = mapped_column(String(24), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    registry_details: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class ConsentRecord(Base):
    __tablename__ = "consent_records"
    __table_args__ = (
        Index("ix_consent_records_account_recorded", "account_id", "recorded_at"),
    )

    id: Mapped[UUID] = uuid_column(primary_key=True)
    account_id: Mapped[UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    purpose: Mapped[str] = mapped_column(String(80), nullable=False)
    notice_version: Mapped[str] = mapped_column(String(32), nullable=False)
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class EmergencyProfile(Base):
    __tablename__ = "emergency_profiles"
    __table_args__ = (
        CheckConstraint("profile_revision >= 1", name="ck_emergency_profile_revision"),
        CheckConstraint("key_version >= 1", name="ck_emergency_profile_key_version"),
    )

    citizen_id: Mapped[UUID] = mapped_column(
        ForeignKey("citizens.id", ondelete="CASCADE"),
        primary_key=True,
    )
    encrypted_payload: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    key_version: Mapped[int] = mapped_column(Integer, nullable=False)
    profile_revision: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class MedicalRecord(Base):
    __tablename__ = "medical_records"
    __table_args__ = (
        CheckConstraint("key_version >= 1", name="ck_medical_records_key_version"),
        Index("ix_medical_records_citizen_created", "citizen_id", "created_at"),
    )

    id: Mapped[UUID] = uuid_column(primary_key=True)
    citizen_id: Mapped[UUID] = mapped_column(
        ForeignKey("citizens.id", ondelete="CASCADE"),
        nullable=False,
    )
    record_type: Mapped[str] = mapped_column(String(40), nullable=False)
    encrypted_payload: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    key_version: Mapped[int] = mapped_column(Integer, nullable=False)
    recorded_by_doctor_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("doctors.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class NfcTag(TimestampMixin, Base):
    __tablename__ = "nfc_tags"
    __table_args__ = (
        CheckConstraint(
            "status IN "
            "('pending_write', 'active', 'lost', 'tampered', 'deactivated')",
            name="ck_nfc_tags_status",
        ),
        CheckConstraint("write_counter >= 0", name="ck_nfc_tags_write_counter"),
        Index("ix_nfc_tags_citizen_status", "citizen_id", "status"),
    )

    id: Mapped[UUID] = uuid_column(primary_key=True)
    tag_uuid: Mapped[UUID] = mapped_column(
        default=uuid4,
        unique=True,
        nullable=False,
        server_default=text("gen_random_uuid()"),
    )
    citizen_id: Mapped[UUID] = mapped_column(
        ForeignKey("citizens.id", ondelete="CASCADE"),
        nullable=False,
    )
    label: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'pending_write'"),
    )
    write_counter: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )
    last_profile_revision: Mapped[int | None] = mapped_column(Integer)


class TagWriteVersion(Base):
    __tablename__ = "tag_write_versions"
    __table_args__ = (
        CheckConstraint("counter >= 0", name="ck_tag_write_versions_counter"),
        CheckConstraint(
            "profile_revision >= 1",
            name="ck_tag_write_versions_profile_revision",
        ),
        UniqueConstraint(
            "tag_id",
            "counter",
            name="uq_tag_write_versions_tag_counter",
        ),
    )

    id: Mapped[UUID] = uuid_column(primary_key=True)
    tag_id: Mapped[UUID] = mapped_column(
        ForeignKey("nfc_tags.id", ondelete="CASCADE"),
        nullable=False,
    )
    counter: Mapped[int] = mapped_column(Integer, nullable=False)
    profile_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    public_text: Mapped[str] = mapped_column(Text, nullable=False)
    text_sha256: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    signing_key_id: Mapped[str] = mapped_column(String(40), nullable=False)
    signature: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RefreshSession(Base):
    __tablename__ = "refresh_sessions"
    __table_args__ = (
        Index("ix_refresh_sessions_account_expires", "account_id", "expires_at"),
    )

    id: Mapped[UUID] = uuid_column(primary_key=True)
    account_id: Mapped[UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    token_hash: Mapped[bytes] = mapped_column(LargeBinary, unique=True, nullable=False)
    device_name: Mapped[str | None] = mapped_column(String(160))
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class OneTimeToken(Base):
    __tablename__ = "one_time_tokens"
    __table_args__ = (
        CheckConstraint(
            "purpose IN ('verify_email', 'reset_password')",
            name="ck_one_time_tokens_purpose",
        ),
        Index("ix_one_time_tokens_account_purpose", "account_id", "purpose"),
    )

    id: Mapped[UUID] = uuid_column(primary_key=True)
    account_id: Mapped[UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    purpose: Mapped[str] = mapped_column(String(24), nullable=False)
    token_hash: Mapped[bytes] = mapped_column(LargeBinary, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class AccessLog(Base):
    __tablename__ = "access_logs"
    __table_args__ = (
        CheckConstraint(
            "actor_type IN ('bystander', 'citizen', 'doctor', 'admin')",
            name="ck_access_logs_actor_type",
        ),
        CheckConstraint(
            "result IN ('allowed', 'denied', 'invalid', 'offline_synced')",
            name="ck_access_logs_result",
        ),
        Index("ix_access_logs_citizen_accessed", "citizen_id", "accessed_at"),
    )

    id: Mapped[UUID] = uuid_column(primary_key=True)
    citizen_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("citizens.id", ondelete="SET NULL")
    )
    tag_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("nfc_tags.id", ondelete="SET NULL")
    )
    actor_account_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("accounts.id", ondelete="SET NULL")
    )
    actor_type: Mapped[str] = mapped_column(String(16), nullable=False)
    access_kind: Mapped[str] = mapped_column(String(40), nullable=False)
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(Text)
    request_id: Mapped[str] = mapped_column(String(64), nullable=False)
    client_event_id: Mapped[str | None] = mapped_column(String(64), unique=True)
    accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    event_metadata: Mapped[dict | None] = mapped_column(JSONB)
