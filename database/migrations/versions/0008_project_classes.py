"""Persist the list of object classes for each training project."""

from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE training_datasets ADD COLUMN classes jsonb NOT NULL DEFAULT '[]'::jsonb")  # noqa: E501


def downgrade():
    op.drop_column("training_datasets", "classes")
