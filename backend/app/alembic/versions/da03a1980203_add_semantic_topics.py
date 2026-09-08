"""Business topics, explicit membership and immutable semantic releases."""

import sqlalchemy as sa
from alembic import op

revision = "da03a1980203"
down_revision = "cc2a7e810902"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("topic",
        sa.Column("id",sa.Uuid(),primary_key=True),
        sa.Column("name",sa.String(80),nullable=False),
        sa.Column("name_key",sa.String(160),nullable=False,unique=True),
        sa.Column("description",sa.String(500),nullable=False),
        sa.Column("source_id",sa.Uuid(),sa.ForeignKey("datasource.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("enabled",sa.Boolean(),nullable=False),
        sa.Column("revision",sa.Integer(),nullable=False),
        sa.Column("current_version",sa.Integer(),nullable=False),
        sa.Column("draft",sa.JSON(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False),
    )
    op.create_index("ix_topic_source_id","topic",["source_id"])
    op.create_table("topicmember",
        sa.Column("topic_id",sa.Uuid(),sa.ForeignKey("topic.id",ondelete="CASCADE"),primary_key=True),
        sa.Column("user_id",sa.Uuid(),sa.ForeignKey("user.id",ondelete="CASCADE"),primary_key=True),
    )
    op.create_table("semanticrelease",
        sa.Column("id",sa.Uuid(),primary_key=True),
        sa.Column("topic_id",sa.Uuid(),sa.ForeignKey("topic.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("version",sa.Integer(),nullable=False),
        sa.Column("definition",sa.JSON(),nullable=False),
        sa.Column("catalog_version",sa.Integer(),nullable=False),
        sa.Column("source_revision",sa.Integer(),nullable=False),
        sa.Column("scope_revision",sa.Integer(),nullable=False),
        sa.Column("binding_digest",sa.String(64),nullable=False),
        sa.Column("published_by",sa.Uuid(),nullable=False),
        sa.Column("note",sa.String(300),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.UniqueConstraint("topic_id","version"),
    )
    op.create_index("ix_semanticrelease_topic_id","semanticrelease",["topic_id"])
    op.create_table("topicaudit",
        sa.Column("id",sa.Uuid(),primary_key=True),
        sa.Column("topic_id",sa.Uuid(),nullable=False),
        sa.Column("actor_id",sa.Uuid(),nullable=False),
        sa.Column("action",sa.String(40),nullable=False),
        sa.Column("revision",sa.Integer(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
    )
    op.create_index("ix_topicaudit_topic_id","topicaudit",["topic_id"])


def downgrade():
    op.drop_table("topicaudit")
    op.drop_table("semanticrelease")
    op.drop_table("topicmember")
    op.drop_table("topic")
