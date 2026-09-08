import uuid
from datetime import datetime
from typing import Literal

from pydantic import Field as PField
from pydantic import SecretStr
from sqlalchemy import Column, DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.modules.datasources.models import now
from app.modules.query.models import QueryPlan, SqlPlan
from app.modules.semantic.models import StrictModel


class GatewayInput(StrictModel):
    name: str = PField(min_length=1, max_length=80)
    provider: Literal["zhipu", "deepseek", "qwen", "custom"]
    base_url: str = PField(min_length=1, max_length=300)
    model: str = PField(min_length=1, max_length=120, pattern=r"^[a-zA-Z0-9_.:/-]+$")
    api_key: SecretStr | None = PField(default=None, max_length=4096)
    timeout_seconds: int = PField(default=45, ge=5, le=90)
    max_tokens: int = PField(default=4096, ge=256, le=16384)
    json_mode: bool = True
    thinking: Literal["default", "enabled", "disabled"] = "default"
    expected_revision: int = PField(default=0, ge=0)


class ModelGateway(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=80)
    provider: str = Field(max_length=20)
    base_url: str = Field(max_length=300)
    model: str = Field(max_length=120)
    encrypted_key: str
    timeout_seconds: int = 45
    max_tokens: int = 4096
    json_mode: bool = True
    thinking: str = Field(default="default", max_length=12)
    revision: int = 1


class GatewayState(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)
    active_id: uuid.UUID | None = None


class GatewayAudit(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    actor_id: uuid.UUID
    gateway_id: uuid.UUID
    action: str = Field(max_length=24)
    revision: int
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class GatewayPublic(StrictModel):
    id: uuid.UUID
    name: str
    provider: str
    base_url: str
    model: str
    timeout_seconds: int
    max_tokens: int
    json_mode: bool
    thinking: str
    revision: int
    has_key: bool
    active: bool


class GatewayRevision(StrictModel):
    expected_revision: int = PField(ge=1)


class GatewayTest(StrictModel):
    success: bool
    message: str
    elapsed_ms: int


class ConversationCreate(StrictModel):
    topic_id: uuid.UUID


class Conversation(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    actor_id: uuid.UUID = Field(index=True)
    topic_id: uuid.UUID = Field(index=True)
    release_id: uuid.UUID
    policy_fingerprint: str = Field(max_length=64)
    revision: int = 0
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class AskInput(StrictModel):
    request_id: uuid.UUID
    expected_revision: int = PField(ge=0)
    question: str = PField(min_length=1, max_length=2000)
    reset_context: bool = False
    mode: Literal["auto", "metrics", "explore"] = "auto"
    entity_choices: dict[str, str] = PField(default_factory=dict, max_length=20)


class AssistantTurn(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("conversation_id", "request_id"),)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(index=True)
    request_id: uuid.UUID
    input_digest: str = Field(max_length=64)
    sequence: int
    status: str = Field(default="planning", max_length=24, index=True)
    encrypted_payload: str = ""
    message: str = Field(default="正在生成查询计划", max_length=500)
    gateway_id: uuid.UUID | None = None
    gateway_revision: int | None = None
    model: str = Field(default="", max_length=120)
    attempts: int = 0
    elapsed_ms: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    query_job_id: uuid.UUID | None = None
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class EntityOption(StrictModel):
    id: str
    label: str
    dimension: str


class EntityAmbiguity(StrictModel):
    mention: str
    options: list[EntityOption]


class TurnPublic(StrictModel):
    id: uuid.UUID
    sequence: int
    status: str
    question: str
    message: str
    plan: QueryPlan | None = None
    sql_plan: SqlPlan | None = None
    chart: Literal["auto", "table", "bar", "line"] = "auto"
    analysis_requested: bool = False
    ambiguities: list[EntityAmbiguity] = []
    model: str
    attempts: int
    elapsed_ms: int
    query_job_id: uuid.UUID | None
    feedback: FeedbackPublic | None = None


class ConversationPublic(StrictModel):
    id: uuid.UUID
    topic_id: uuid.UUID
    revision: int
    expires_at: datetime
    turns: list[TurnPublic]
    created_at: datetime


class FeedbackInput(StrictModel):
    rating: Literal["helpful", "incorrect"]
    category: Literal["none", "metric", "filter", "data", "chart", "other"] = "none"
    comment: str = PField(default="", max_length=1000)


class FeedbackPublic(FeedbackInput):
    updated_at: datetime


class AnswerEvidence(StrictModel):
    topic: str
    semantic_version: int
    catalog_version: int
    published_at: datetime
    owner: str
    timezone: str
    database_type: str
    sources: list[str]
    metrics: list[str]
    fixed_filters: list[str]
    policy: str
    notes: list[str]
    query_id: uuid.UUID | None = None
    queried_at: datetime | None = None
    expires_at: datetime | None = None


class PlanDecision(StrictModel):
    action: Literal["plan", "clarify", "unsupported"]
    message: str = PField(default="", max_length=500)
    plan: QueryPlan | None = None
    sql_plan: SqlPlan | None = None
    chart: Literal["auto", "table", "bar", "line"] = "auto"
    analysis_requested: bool = False


class AnalysisFact(StrictModel):
    id: str
    label: str
    value: str


class AnalysisFinding(StrictModel):
    fact_ids: list[str] = PField(min_length=1, max_length=8)
    interpretation: str = PField(max_length=600)
    next_step: str = PField(default="", max_length=400)


class AnalysisDecision(StrictModel):
    findings: list[AnalysisFinding] = PField(min_length=1, max_length=6)


class AnalysisPublic(StrictModel):
    facts: list[AnalysisFact]
    findings: list[AnalysisFinding] = []
    scope: str
    model: str = ""
