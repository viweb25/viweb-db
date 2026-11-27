"""Inspection programs (golden layout per zone) and the log of every inspection run.

A program belongs to one training dataset (project) and uses one of its trained models.
Its zones hold the golden layout: how many of each class must be found in that region.
Every inspection writes one run row, which people can review and send back for retraining.
"""

from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE inspection_programs (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            org_id uuid NOT NULL REFERENCES organisations(id),
            dataset_id uuid NOT NULL REFERENCES training_datasets(id) ON DELETE CASCADE,
            model_job_id uuid REFERENCES training_jobs(id) ON DELETE SET NULL,
            name text NOT NULL CHECK (length(btrim(name)) BETWEEN 1 AND 80),
            confidence double precision NOT NULL DEFAULT 0.5 CHECK (confidence BETWEEN 0.05 AND 0.99),
            review_margin double precision NOT NULL DEFAULT 0.15 CHECK (review_margin BETWEEN 0 AND 0.5),
            revision integer NOT NULL DEFAULT 1 CHECK (revision > 0),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CHECK (review_margin < confidence)
        )
    """)
    op.execute("""
        CREATE INDEX inspection_programs_org_updated_idx
        ON inspection_programs (org_id, updated_at DESC, id)
    """)
    op.execute("""
        CREATE TABLE inspection_zones (
            program_id uuid NOT NULL REFERENCES inspection_programs(id) ON DELETE CASCADE,
            id uuid NOT NULL,
            name text NOT NULL CHECK (length(btrim(name)) BETWEEN 1 AND 60),
            position integer NOT NULL CHECK (position >= 0),
            x1 double precision NOT NULL, y1 double precision NOT NULL,
            x2 double precision NOT NULL, y2 double precision NOT NULL,
            expected jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(expected) = 'object'),
            critical boolean NOT NULL DEFAULT true,
            PRIMARY KEY (program_id, id),
            UNIQUE (program_id, position),
            CHECK (0 <= x1 AND x1 < x2 AND x2 <= 1 AND 0 <= y1 AND y1 < y2 AND y2 <= 1)
        )
    """)
    op.execute("""
        CREATE TABLE inspection_runs (
            id uuid PRIMARY KEY,
            org_id uuid NOT NULL REFERENCES organisations(id),
            program_id uuid NOT NULL REFERENCES inspection_programs(id) ON DELETE CASCADE,
            model_job_id uuid REFERENCES training_jobs(id) ON DELETE SET NULL,
            decision text NOT NULL CHECK (decision IN ('PASS', 'FAIL', 'REVIEW')),
            zone_results jsonb NOT NULL CHECK (jsonb_typeof(zone_results) = 'array'),
            detections jsonb NOT NULL CHECK (jsonb_typeof(detections) = 'array'),
            confidence double precision NOT NULL,
            image_digest text NOT NULL CHECK (image_digest ~ '^[a-f0-9]{64}$'),
            created_by uuid NOT NULL REFERENCES identity.users(id),
            created_at timestamptz NOT NULL DEFAULT now(),
            review_status text NOT NULL DEFAULT 'none'
                CHECK (review_status IN ('none', 'pending', 'confirmed', 'corrected')),
            review_note text NOT NULL DEFAULT '' CHECK (length(review_note) <= 400),
            reviewed_by uuid REFERENCES identity.users(id),
            reviewed_at timestamptz,
            sent_to_dataset_at timestamptz
        )
    """)
    op.execute("""
        CREATE INDEX inspection_runs_org_created_idx
        ON inspection_runs (org_id, created_at DESC, id)
    """)
    op.execute("""
        CREATE INDEX inspection_runs_program_created_idx
        ON inspection_runs (program_id, created_at DESC, id)
    """)
    op.execute("""
        CREATE INDEX inspection_runs_pending_review_idx
        ON inspection_runs (org_id, created_at DESC) WHERE review_status = 'pending'
    """)


def downgrade():
    op.drop_table("inspection_runs")
    op.drop_table("inspection_zones")
    op.drop_table("inspection_programs")
