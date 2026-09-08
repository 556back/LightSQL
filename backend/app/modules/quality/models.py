import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field as PField
from pydantic import model_validator
from sqlalchemy import JSON, Column, DateTime
from sqlmodel import Field, SQLModel

from app.modules.datasources.models import now
from app.modules.semantic.models import StrictModel


class QualityFeedback(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    turn_id: uuid.UUID = Field(unique=True)
    topic_id: uuid.UUID = Field(index=True)
    actor_id: uuid.UUID
    release_id: uuid.UUID
    encrypted_payload: str
    status: str = Field(default="pending", max_length=20, index=True)
    revision: int = 1
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class QualityAudit(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    feedback_id: uuid.UUID = Field(index=True)
    actor_id: uuid.UUID
    action: str = Field(max_length=20)
    revision: int
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class ReviewInput(StrictModel):
    expected_revision: int = PField(ge=1)
    status: Literal["pending", "confirmed", "dismissed", "resolved"]
    note: str = PField(min_length=1, max_length=2000)
    dataset_id: uuid.UUID | None = None
    case_id: str | None = PField(default=None, max_length=80)


class FeedbackReviewPublic(StrictModel):
    id: uuid.UUID
    topic_id: uuid.UUID
    turn_id: uuid.UUID
    status: str
    revision: int
    updated_at: datetime
    expires_at: datetime
    snapshot: dict


Cell = str | bool | None


class GoldCase(StrictModel):
    id: str = PField(min_length=1, max_length=80)
    group: str = PField(min_length=1, max_length=80)
    split: Literal["dev", "blind"]
    question: str = PField(min_length=1, max_length=2000)
    history: list[str] = PField(default_factory=list, max_length=10)
    mode: Literal["auto", "metrics", "explore"] = "metrics"
    actor_role: str = PField(min_length=1, max_length=80)
    tags: list[str] = PField(default_factory=list, max_length=20)
    expected_action: Literal["answer", "clarify", "unsupported"]
    columns: list[str] = PField(default_factory=list, max_length=100)
    numeric_columns: list[str] = PField(default_factory=list, max_length=100)
    expected_rows: list[list[Cell]] = PField(default_factory=list, max_length=1000)
    ordered: bool = False
    tolerance: Decimal = PField(default=Decimal("0"), ge=0, le=1, allow_inf_nan=False)
    reference_sql: str = PField(default="", max_length=10000)
    reference_plan: dict = PField(default_factory=dict)

    @model_validator(mode="after")
    def consistent(self):
        if len(set(self.columns)) != len(self.columns) or not set(
            self.numeric_columns
        ) <= set(self.columns):
            raise ValueError("结果列必须唯一，数值列必须属于结果列")
        if any(len(row) != len(self.columns) for row in self.expected_rows):
            raise ValueError("期望行与列数不一致")
        if self.expected_action == "answer" and (
            not self.columns or not (self.reference_sql or self.reference_plan)
        ):
            raise ValueError("可回答题需要结果列和参考 SQL 或计划")
        if self.expected_action != "answer" and (self.columns or self.expected_rows):
            raise ValueError("澄清或不支持题不能带结果断言")
        return self


class DatasetInput(StrictModel):
    name: str = PField(min_length=1, max_length=120)
    topic_id: uuid.UUID
    semantic_version: int = PField(ge=1)
    source_snapshot: str = PField(min_length=1, max_length=300)
    as_of: str = PField(min_length=1, max_length=80)
    timezone: str = PField(min_length=1, max_length=80)
    provenance: Literal["synthetic", "business_reviewed"]
    owner: str = PField(min_length=1, max_length=100)
    cases: list[GoldCase] = PField(min_length=1, max_length=500)

    @model_validator(mode="after")
    def separated(self):
        if len({c.id for c in self.cases}) != len(self.cases):
            raise ValueError("题目 ID 不能重复")
        groups = {}
        for case in self.cases:
            if case.group in groups and groups[case.group] != case.split:
                raise ValueError("同一改写分组不能横跨开发集与盲测集")
            groups[case.group] = case.split
        return self


class EvaluationDataset(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=120)
    topic_id: uuid.UUID = Field(index=True)
    digest: str = Field(max_length=64)
    encrypted_payload: str
    created_by: uuid.UUID
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class Observation(StrictModel):
    case_id: str = PField(min_length=1, max_length=80)
    action: Literal["answer", "clarify", "unsupported", "error"]
    columns: list[str] = PField(default_factory=list, max_length=100)
    rows: list[list[Cell]] = PField(default_factory=list, max_length=1000)
    truncated: bool = False
    elapsed_ms: int = PField(ge=0)
    prompt_tokens: int = PField(default=0, ge=0)
    completion_tokens: int = PField(default=0, ge=0)
    usage_measured: bool = False
    cost: Decimal | None = PField(default=None, ge=0, allow_inf_nan=False)
    error_category: Literal[
        "none",
        "definition",
        "retrieval",
        "plan",
        "dialect",
        "permission",
        "performance",
        "model",
        "privacy",
    ] = "none"
    critical: bool = False


class RunInput(StrictModel):
    dataset_id: uuid.UUID
    dataset_digest: str = PField(pattern=r"^[a-f0-9]{64}$")
    model: str = PField(min_length=1, max_length=120)
    configuration: str = PField(min_length=1, max_length=300)
    context_variant: Literal["A", "B", "C", "D"]
    evidence: Literal["protocol_replay", "live_model", "manual"]
    split: Literal["dev", "blind"]
    currency: str = PField(default="CNY", pattern=r"^[A-Z]{3}$")
    observations: list[Observation] = PField(min_length=1, max_length=500)


class EvaluationRun(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    dataset_id: uuid.UUID = Field(index=True)
    model: str = Field(max_length=120)
    context_variant: str = Field(max_length=1)
    evidence: str = Field(max_length=24)
    split: str = Field(max_length=10)
    encrypted_payload: str
    summary: dict = Field(sa_column=Column(JSON, nullable=False))
    created_by: uuid.UUID
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class WorkerHeartbeat(SQLModel, table=True):
    id: str = Field(primary_key=True, max_length=100)
    kind: str = Field(max_length=20, index=True)
    seen_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class BackupRecord(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    checksum: str = Field(max_length=64)
    size_bytes: int
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    restored_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
