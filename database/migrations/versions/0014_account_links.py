"""Store one-time workspace invitation and password recovery token hashes."""

from alembic import op

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE identity.workspace_invitations (
            org_id uuid NOT NULL REFERENCES organisations(id),
            email text NOT NULL,
            role text NOT NULL CHECK (role IN ('operator', 'viewer')),
            token_hash bytea NOT NULL UNIQUE CHECK (octet_length(token_hash) = 32),
            expires_at timestamptz NOT NULL,
            PRIMARY KEY (org_id, email)
        )
    """)
    op.execute("""
        CREATE TABLE identity.password_resets (
            user_id uuid PRIMARY KEY REFERENCES identity.password_credentials(user_id),
            token_hash bytea NOT NULL UNIQUE CHECK (octet_length(token_hash) = 32),
            expires_at timestamptz NOT NULL
        )
    """)


def downgrade():
    op.drop_table("password_resets", schema="identity")
    op.drop_table("workspace_invitations", schema="identity")
