"""Create the initial MediTag schema.

Revision ID: 20260926_01
Revises: None
Create Date: 2026-09-26
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260926_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def execute_statements(sql: str) -> None:
    """Execute readable SQL one statement at a time for psycopg compatibility."""
    for statement in sql.split(";"):
        if statement.strip():
            op.execute(statement)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    execute_statements(
        """
        CREATE TABLE accounts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(320) NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role VARCHAR(16) NOT NULL,
            email_verified_at TIMESTAMPTZ,
            mfa_enabled BOOLEAN NOT NULL DEFAULT false,
            mfa_secret_ciphertext BYTEA,
            mfa_key_version INTEGER,
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_accounts_role
                CHECK (role IN ('citizen', 'doctor', 'admin'))
        );

        CREATE TABLE citizens (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            account_id UUID NOT NULL UNIQUE
                REFERENCES accounts(id) ON DELETE CASCADE,
            full_name VARCHAR(160) NOT NULL,
            date_of_birth DATE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE doctors (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            account_id UUID NOT NULL UNIQUE
                REFERENCES accounts(id) ON DELETE CASCADE,
            full_name VARCHAR(160) NOT NULL,
            medical_council VARCHAR(120) NOT NULL,
            license_number VARCHAR(80) NOT NULL,
            verification_status VARCHAR(16) NOT NULL DEFAULT 'pending',
            verification_document_key TEXT,
            verified_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_doctors_verification_status CHECK (
                verification_status IN ('pending', 'verified', 'rejected', 'suspended')
            ),
            CONSTRAINT uq_doctors_council_license
                UNIQUE (medical_council, license_number)
        );

        CREATE TABLE admins (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            account_id UUID NOT NULL UNIQUE
                REFERENCES accounts(id) ON DELETE CASCADE,
            display_name VARCHAR(160) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE doctor_verification_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            doctor_id UUID NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
            reviewer_account_id UUID REFERENCES accounts(id) ON DELETE SET NULL,
            decision VARCHAR(24) NOT NULL,
            reason TEXT,
            registry_details JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_doctor_verification_events_decision CHECK (
                decision IN ('submitted', 'registry_match', 'approved', 'rejected')
            )
        );
        CREATE INDEX ix_doctor_verification_events_doctor_created
            ON doctor_verification_events (doctor_id, created_at);

        CREATE TABLE consent_records (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            purpose VARCHAR(80) NOT NULL,
            notice_version VARCHAR(32) NOT NULL,
            granted BOOLEAN NOT NULL,
            recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            withdrawn_at TIMESTAMPTZ
        );
        CREATE INDEX ix_consent_records_account_recorded
            ON consent_records (account_id, recorded_at);

        CREATE TABLE emergency_profiles (
            citizen_id UUID PRIMARY KEY REFERENCES citizens(id) ON DELETE CASCADE,
            encrypted_payload BYTEA NOT NULL,
            key_version INTEGER NOT NULL,
            profile_revision INTEGER NOT NULL DEFAULT 1,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_emergency_profile_revision CHECK (profile_revision >= 1),
            CONSTRAINT ck_emergency_profile_key_version CHECK (key_version >= 1)
        );

        CREATE TABLE medical_records (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            citizen_id UUID NOT NULL REFERENCES citizens(id) ON DELETE CASCADE,
            record_type VARCHAR(40) NOT NULL,
            encrypted_payload BYTEA NOT NULL,
            key_version INTEGER NOT NULL,
            recorded_by_doctor_id UUID REFERENCES doctors(id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_medical_records_key_version CHECK (key_version >= 1)
        );
        CREATE INDEX ix_medical_records_citizen_created
            ON medical_records (citizen_id, created_at);

        CREATE TABLE nfc_tags (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tag_uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
            citizen_id UUID NOT NULL REFERENCES citizens(id) ON DELETE CASCADE,
            label VARCHAR(80) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending_write',
            write_counter INTEGER NOT NULL DEFAULT 0,
            last_profile_revision INTEGER,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_nfc_tags_status CHECK (
                status IN ('pending_write', 'active', 'lost', 'tampered', 'deactivated')
            ),
            CONSTRAINT ck_nfc_tags_write_counter CHECK (write_counter >= 0)
        );
        CREATE INDEX ix_nfc_tags_citizen_status
            ON nfc_tags (citizen_id, status);

        CREATE TABLE tag_write_versions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tag_id UUID NOT NULL REFERENCES nfc_tags(id) ON DELETE CASCADE,
            counter INTEGER NOT NULL,
            profile_revision INTEGER NOT NULL,
            public_text TEXT NOT NULL,
            text_sha256 BYTEA NOT NULL,
            signing_key_id VARCHAR(40) NOT NULL,
            signature BYTEA NOT NULL,
            issued_at TIMESTAMPTZ NOT NULL,
            expires_at TIMESTAMPTZ NOT NULL,
            confirmed_at TIMESTAMPTZ,
            CONSTRAINT ck_tag_write_versions_counter CHECK (counter >= 0),
            CONSTRAINT ck_tag_write_versions_profile_revision
                CHECK (profile_revision >= 1),
            CONSTRAINT uq_tag_write_versions_tag_counter UNIQUE (tag_id, counter)
        );

        CREATE TABLE refresh_sessions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            token_hash BYTEA NOT NULL UNIQUE,
            device_name VARCHAR(160),
            expires_at TIMESTAMPTZ NOT NULL,
            revoked_at TIMESTAMPTZ,
            last_used_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX ix_refresh_sessions_account_expires
            ON refresh_sessions (account_id, expires_at);

        CREATE TABLE one_time_tokens (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            purpose VARCHAR(24) NOT NULL,
            token_hash BYTEA NOT NULL UNIQUE,
            expires_at TIMESTAMPTZ NOT NULL,
            consumed_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_one_time_tokens_purpose
                CHECK (purpose IN ('verify_email', 'reset_password'))
        );
        CREATE INDEX ix_one_time_tokens_account_purpose
            ON one_time_tokens (account_id, purpose);

        CREATE TABLE access_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            citizen_id UUID REFERENCES citizens(id) ON DELETE SET NULL,
            tag_id UUID REFERENCES nfc_tags(id) ON DELETE SET NULL,
            actor_account_id UUID REFERENCES accounts(id) ON DELETE SET NULL,
            actor_type VARCHAR(16) NOT NULL,
            access_kind VARCHAR(40) NOT NULL,
            result VARCHAR(20) NOT NULL,
            ip_address VARCHAR(45),
            user_agent TEXT,
            request_id VARCHAR(64) NOT NULL,
            client_event_id VARCHAR(64) UNIQUE,
            accessed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            event_metadata JSONB,
            CONSTRAINT ck_access_logs_actor_type CHECK (
                actor_type IN ('bystander', 'citizen', 'doctor', 'admin')
            ),
            CONSTRAINT ck_access_logs_result CHECK (
                result IN ('allowed', 'denied', 'invalid', 'offline_synced')
            )
        );
        CREATE INDEX ix_access_logs_citizen_accessed
            ON access_logs (citizen_id, accessed_at);
        """
    )


def downgrade() -> None:
    execute_statements(
        """
        DROP TABLE IF EXISTS access_logs;
        DROP TABLE IF EXISTS one_time_tokens;
        DROP TABLE IF EXISTS refresh_sessions;
        DROP TABLE IF EXISTS tag_write_versions;
        DROP TABLE IF EXISTS nfc_tags;
        DROP TABLE IF EXISTS medical_records;
        DROP TABLE IF EXISTS emergency_profiles;
        DROP TABLE IF EXISTS consent_records;
        DROP TABLE IF EXISTS doctor_verification_events;
        DROP TABLE IF EXISTS admins;
        DROP TABLE IF EXISTS doctors;
        DROP TABLE IF EXISTS citizens;
        DROP TABLE IF EXISTS accounts;
        """
    )
