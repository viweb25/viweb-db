"""Describe each project class as good, defect or plain object, with a short hint."""

from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE training_datasets
        ADD COLUMN class_info jsonb NOT NULL DEFAULT '{}'::jsonb
        CHECK (jsonb_typeof(class_info) = 'object')
    """)


def downgrade():
    op.drop_column("training_datasets", "class_info")
