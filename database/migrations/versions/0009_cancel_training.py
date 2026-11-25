"""Allow training jobs to finish in a cancelled state."""

from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("training_jobs_status_check", "training_jobs", type_="check")
    op.create_check_constraint(
        "training_jobs_status_check", "training_jobs",
        "status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled')",
    )


def downgrade():
    op.execute("UPDATE training_jobs SET status = 'failed' WHERE status = 'cancelled'")
    op.drop_constraint("training_jobs_status_check", "training_jobs", type_="check")
    op.create_check_constraint(
        "training_jobs_status_check", "training_jobs",
        "status IN ('queued', 'running', 'succeeded', 'failed')",
    )
