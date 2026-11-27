"""Archive inspection configuration and preserve the rules used by new runs."""

from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade():
    statements = """
        ALTER TABLE training_datasets ADD COLUMN archived_at timestamptz;
        ALTER TABLE inspection_programs
            ADD COLUMN archived_at timestamptz,
            DROP CONSTRAINT inspection_programs_dataset_id_fkey,
            ADD FOREIGN KEY (dataset_id) REFERENCES training_datasets(id) ON DELETE RESTRICT;
        ALTER TABLE inspection_runs
            ADD COLUMN program_snapshot jsonb CHECK (jsonb_typeof(program_snapshot) = 'object'),
            DROP CONSTRAINT inspection_runs_program_id_fkey,
            DROP CONSTRAINT inspection_runs_model_job_id_fkey,
            ADD FOREIGN KEY (program_id) REFERENCES inspection_programs(id) ON DELETE RESTRICT,
            ADD FOREIGN KEY (model_job_id) REFERENCES training_jobs(id) ON DELETE RESTRICT;
        CREATE INDEX inspection_runs_model_job_idx ON inspection_runs (model_job_id);
        CREATE INDEX inspection_programs_dataset_idx ON inspection_programs (dataset_id);
    """
    for statement in statements.strip().rstrip(";").split(";"):
        op.execute(statement)


def downgrade():
    statements = """
        DROP INDEX inspection_programs_dataset_idx;
        DROP INDEX inspection_runs_model_job_idx;
        ALTER TABLE inspection_runs
            DROP COLUMN program_snapshot,
            DROP CONSTRAINT inspection_runs_program_id_fkey,
            DROP CONSTRAINT inspection_runs_model_job_id_fkey,
            ADD FOREIGN KEY (program_id) REFERENCES inspection_programs(id) ON DELETE CASCADE,
            ADD FOREIGN KEY (model_job_id) REFERENCES training_jobs(id) ON DELETE SET NULL;
        ALTER TABLE inspection_programs
            DROP COLUMN archived_at,
            DROP CONSTRAINT inspection_programs_dataset_id_fkey,
            ADD FOREIGN KEY (dataset_id) REFERENCES training_datasets(id) ON DELETE CASCADE;
        ALTER TABLE training_datasets DROP COLUMN archived_at;
    """
    for statement in statements.strip().rstrip(";").split(";"):
        op.execute(statement)
