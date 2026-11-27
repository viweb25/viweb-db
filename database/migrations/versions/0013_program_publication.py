"""Keep immutable published program revisions and a pointer to the live revision."""

from alembic import op

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE inspection_program_versions (
            program_id uuid NOT NULL REFERENCES inspection_programs(id),
            revision integer NOT NULL CHECK (revision > 0),
            model_job_id uuid NOT NULL REFERENCES training_jobs(id),
            snapshot jsonb NOT NULL CHECK (jsonb_typeof(snapshot) = 'object'),
            published_at timestamptz NOT NULL DEFAULT now(),
            PRIMARY KEY (program_id, revision)
        )
    """)
    op.execute("""
        ALTER TABLE inspection_programs ADD COLUMN published_revision integer,
        ADD FOREIGN KEY (id, published_revision)
            REFERENCES inspection_program_versions(program_id, revision)
    """)
    op.execute("""
        INSERT INTO inspection_program_versions (program_id, revision, model_job_id, snapshot)
        SELECT p.id, p.revision, p.model_job_id, jsonb_build_object(
            'revision', p.revision, 'name', p.name, 'confidence', p.confidence,
            'review_margin', p.review_margin,
            'classes', CASE WHEN jsonb_array_length(d.classes) > 0
                THEN d.classes ELSE jsonb_build_array(d.part_name) END,
            'defect_classes', COALESCE((
                SELECT jsonb_agg(label ORDER BY label)
                FROM jsonb_each(d.class_info) AS c(label, info)
                WHERE info ->> 'kind' = 'defect'
            ), '[]'::jsonb),
            'zones', jsonb_agg(jsonb_build_object(
                'id', z.id, 'name', z.name, 'region', jsonb_build_object(
                    'x1', z.x1, 'x2', z.x2, 'y1', z.y1, 'y2', z.y2),
                'expected', z.expected, 'critical', z.critical
            ) ORDER BY z.position)
        )
        FROM inspection_programs p
        JOIN training_datasets d ON d.id = p.dataset_id
        JOIN inspection_zones z ON z.program_id = p.id
        JOIN training_jobs j ON j.id = p.model_job_id AND j.status = 'succeeded'
        WHERE p.archived_at IS NULL AND d.archived_at IS NULL
        GROUP BY p.id, d.id
    """)
    op.execute("""
        UPDATE inspection_programs p SET published_revision = v.revision
        FROM inspection_program_versions v WHERE v.program_id = p.id
    """)


def downgrade():
    op.drop_column("inspection_programs", "published_revision")
    op.drop_table("inspection_program_versions")
