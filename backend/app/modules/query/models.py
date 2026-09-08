import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import Field as PField
from sqlalchemy import JSON, Column, DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.modules.datasources.models import now
from app.modules.semantic.models import (
    Identifier,
    LiteralValue,
    PhysicalName,
    StrictModel,
)


class Grouping(StrictModel):
    dimension_id: Identifier
    grain: Literal["value", "day", "month", "year"] = "value"


class QueryFilter(StrictModel):
    dimension_id: Identifier
    operator: Literal[
        "eq", "in", "gt", "gte", "lt", "lte", "between", "is_null", "is_not_null"
    ]
    values: list[LiteralValue] = PField(default_factory=list, max_length=50)


class TimeRange(StrictModel):
    start: LiteralValue
    end: LiteralValue


class Ordering(StrictModel):
    field: Identifier
    direction: Literal["asc", "desc"] = "asc"


class QueryPlan(StrictModel):
    metrics: list[Identifier] = PField(min_length=1, max_length=10)
    dimensions: list[Grouping] = PField(default_factory=list, max_length=5)
    filters: list[QueryFilter] = PField(default_factory=list, max_length=20)
    time_range: TimeRange | None = None
    order_by: list[Ordering] = PField(default_factory=list, max_length=5)
    limit: int = PField(default=100, ge=1, le=1000)
    timeout_seconds: int = PField(default=15, ge=1, le=30)


class SqlPlan(StrictModel):
    kind: Literal["sql"] = "sql"
    sql: str = PField(min_length=1, max_length=20000)
    limit: int = PField(default=100, ge=1, le=1000)
    timeout_seconds: int = PField(default=15, ge=1, le=30)


def parse_plan(value: dict) -> QueryPlan | SqlPlan:
    return (
        SqlPlan.model_validate(value)
        if value.get("kind") == "sql"
        else QueryPlan.model_validate(value)
    )


class QuerySubmission(StrictModel):
    topic_id: uuid.UUID
    request_id: uuid.UUID
    plan: QueryPlan | SqlPlan


class RowScope(StrictModel):
    model_id: Identifier
    column: PhysicalName
    values: list[LiteralValue] = PField(min_length=1, max_length=100)


class TableAccess(StrictModel):
    model_id: Identifier
    columns: list[PhysicalName] = PField(min_length=1, max_length=200)


class QueryGrant(StrictModel):
    user_id: uuid.UUID
    metric_ids: list[Identifier] = PField(default_factory=list, max_length=100)
    exploration: list[TableAccess] = PField(default_factory=list, max_length=30)
    dimension_ids: list[Identifier] = PField(default_factory=list, max_length=100)
    unrestricted: bool = False
    rows: list[RowScope] = PField(default_factory=list, max_length=30)


class PolicyUpdate(StrictModel):
    expected_revision: int = PField(ge=0)
    grants: list[QueryGrant] = PField(max_length=200)


class QueryPolicy(SQLModel, table=True):
    topic_id: uuid.UUID = Field(
        foreign_key="topic.id", ondelete="CASCADE", primary_key=True
    )
    revision: int = 1
    release_id: uuid.UUID
    binding_digest: str = Field(default="", max_length=64)
    grants: list[dict[str, Any]] = Field(sa_column=Column(JSON, nullable=False))


class QueryGate(SQLModel, table=True):
    """A persistent row serializes admission and claims across API/worker processes."""

    id: int = Field(default=1, primary_key=True)


class QueryJob(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("actor_id", "request_id"),)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    actor_id: uuid.UUID = Field(index=True)
    request_id: uuid.UUID
    topic_id: uuid.UUID = Field(index=True)
    source_id: uuid.UUID = Field(index=True)
    release_id: uuid.UUID
    semantic_version: int
    policy_fingerprint: str = Field(max_length=64)
    plan_fingerprint: str = Field(max_length=64)
    plan: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    sql_text: str = ""
    status: str = Field(default="queued", max_length=24, index=True)
    cancel_requested: bool = False
    lease_token: uuid.UUID | None = None
    lease_until: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    started_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    finished_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    message: str = Field(default="等待查询进程处理", max_length=300)
    result: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    row_count: int = 0
    result_bytes: int = 0
    truncated: bool = False
    elapsed_ms: int | None = None


class QueryEvent(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_id: uuid.UUID | None = Field(default=None, index=True)
    topic_id: uuid.UUID = Field(index=True)
    actor_id: uuid.UUID
    action: str = Field(max_length=40)
    detail: str = Field(default="", max_length=300)
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class ResultColumn(StrictModel):
    id: str
    label: str
    value_type: str
    unit: str = ""
    timezone: str = ""


class QueryPreview(StrictModel):
    semantic_version: int
    columns: list[ResultColumn]
    sql: str | None = None
    parameter_count: int
    policy_label: str
    limit: int
    timeout_seconds: int
    notes: list[str]


class QueryJobPublic(StrictModel):
    id: uuid.UUID
    topic_id: uuid.UUID
    semantic_version: int
    status: str
    message: str
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    expires_at: datetime
    row_count: int
    result_bytes: int
    truncated: bool
    elapsed_ms: int | None
    sql: str | None = None


class QueryResult(StrictModel):
    columns: list[ResultColumn]
    rows: list[list[str | bool | None]]
    truncated: bool
    notes: list[str]


class PolicyPublic(StrictModel):
    revision: int
    semantic_version: int
    stale: bool
    grants: list[QueryGrant]
    models: list[dict[str, Any]]
