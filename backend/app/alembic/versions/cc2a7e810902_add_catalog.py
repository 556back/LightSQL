"""Add metadata scope, snapshots and durable sync jobs."""

import sqlalchemy as sa
from alembic import op

revision = "cc2a7e810902"
down_revision = "92b2a116ab01"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "catalogstate",
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("datasource.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("source_revision", sa.Integer(), nullable=False),
        sa.Column("scope", sa.JSON(), nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("synced_scope_revision", sa.Integer(), nullable=False),
        sa.Column("synced_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "syncjob",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=False),
        sa.Column("source_revision", sa.Integer(), nullable=False),
        sa.Column("scope_revision", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("lease_token", sa.Uuid()),
        sa.Column("lease_until", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("message", sa.String(300), nullable=False),
        sa.Column("table_count", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer()),
        sa.Column("changes", sa.JSON(), nullable=False),
    )
    op.create_index("ix_syncjob_source_id", "syncjob", ["source_id"])
    op.create_index("ix_syncjob_status", "syncjob", ["status"])


def downgrade():
    op.drop_table("syncjob")
    op.drop_table("catalogstate")
