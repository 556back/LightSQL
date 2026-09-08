"""Bind row-policy fields to their catalog types, including non-semantic columns."""
from alembic import op
import sqlalchemy as sa

revision = "e4b106041004"
down_revision = "5b2dafec4844"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("querypolicy", sa.Column("binding_digest", sa.String(64), nullable=False, server_default=""))
    op.alter_column("querypolicy", "binding_digest", server_default=None)


def downgrade():
    op.drop_column("querypolicy", "binding_digest")
