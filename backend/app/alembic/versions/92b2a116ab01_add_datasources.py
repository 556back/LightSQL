"""Add encrypted data source configurations and audit events."""

from alembic import op
import sqlalchemy as sa

revision = "92b2a116ab01"
down_revision = "fe56fa70289e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "datasource",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("name_key", sa.String(80), nullable=False, unique=True),
        sa.Column("database_type", sa.String(20), nullable=False),
        sa.Column("host", sa.String(253), nullable=False),
        sa.Column("port", sa.Integer(), nullable=False),
        sa.Column("database", sa.String(128), nullable=False),
        sa.Column("username", sa.String(128), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("tls_mode", sa.String(20), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("encrypted_password", sa.String(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("last_tested_at", sa.DateTime(timezone=True)),
        sa.Column("latency_ms", sa.Integer()),
        sa.Column("last_error", sa.String(300)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "datasourceaudit",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("datasource_id", sa.Uuid(), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(30), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_datasourceaudit_datasource_id", "datasourceaudit", ["datasource_id"])
    op.create_index("ix_datasourceaudit_actor_id", "datasourceaudit", ["actor_id"])


def downgrade():
    op.drop_table("datasourceaudit")
    op.drop_table("datasource")
