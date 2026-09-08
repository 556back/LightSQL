import uuid
from datetime import datetime
from typing import Annotated, Any, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator
from pydantic import Field as PField
from sqlalchemy import JSON, Column, DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.modules.catalog.models import ObjectRef
from app.modules.datasources.models import now

Identifier = Annotated[str, PField(pattern=r"^[a-z][a-z0-9_]{0,47}$")]
ShortText = Annotated[str, PField(min_length=1, max_length=120)]
Aliases = Annotated[list[ShortText], PField(max_length=15)]
PhysicalName = Annotated[
    str, StringConstraints(strip_whitespace=False, min_length=1, max_length=128)
]
LiteralValue = Annotated[str, StringConstraints(strip_whitespace=False, max_length=200)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class SemanticModel(StrictModel):
    id: Identifier
    label: ShortText
    relation: ObjectRef
    grain: str = PField(min_length=1, max_length=300)
    primary_key: list[PhysicalName] = PField(default_factory=list, max_length=16)


class Dimension(StrictModel):
    id: Identifier
    label: ShortText
    description: str = PField(default="", max_length=1000)
    aliases: Aliases = []
    model_id: Identifier
    column: PhysicalName
    value_type: Literal["string", "number", "date", "datetime", "boolean", "entity"]
    timezone_semantics: Literal["date_only", "utc", "topic_local"] = "date_only"
    sensitive: bool = False
    external_allowed: bool = False
    value_external_allowed: Literal[False] = False


class Metric(StrictModel):
    id: Identifier
    label: ShortText
    description: str = PField(min_length=1, max_length=2000)
    aliases: Aliases = []
    model_id: Identifier
    aggregation: Literal["sum", "count", "count_distinct", "avg", "min", "max", "ratio"]
    column: PhysicalName | None = None
    unit: str = PField(min_length=1, max_length=40)
    time_dimension: Identifier | None = None
    allowed_dimensions: list[Identifier] = PField(default_factory=list, max_length=100)
    filter_ids: list[Identifier] = PField(default_factory=list, max_length=50)
    additivity: Literal["additive", "semi_additive", "non_additive"] = "additive"
    non_additive_dimensions: list[Identifier] = PField(
        default_factory=list, max_length=100
    )
    numerator: Identifier | None = None
    denominator: Identifier | None = None
    zero_denominator: Literal["null"] = "null"
    external_allowed: bool = False


class FixedFilter(StrictModel):
    id: Identifier
    label: ShortText
    dimension_id: Identifier
    operator: Literal[
        "eq", "in", "gt", "gte", "lt", "lte", "between", "is_null", "is_not_null"
    ]
    values: list[LiteralValue] = PField(default_factory=list, max_length=50)


class Relation(StrictModel):
    id: Identifier
    label: ShortText
    from_model: Identifier
    to_model: Identifier
    from_columns: list[PhysicalName] = PField(min_length=1, max_length=16)
    to_columns: list[PhysicalName] = PField(min_length=1, max_length=16)
    cardinality: Literal["many_to_one", "one_to_one", "one_to_many", "many_to_many"] = (
        "many_to_one"
    )
    join_type: Literal["left", "inner"] = "left"
    description: str = PField(min_length=1, max_length=500)


class EntityEntry(StrictModel):
    id: Identifier
    dimension_id: Identifier
    label: ShortText
    aliases: Aliases = []
    value: LiteralValue = PField(min_length=1)


class SemanticDefinition(StrictModel):
    schema_version: Literal[1] = 1
    owner: str = PField(default="", max_length=120)
    timezone: str = PField(default="Asia/Shanghai", max_length=60)
    external_allowed: bool = False
    models: list[SemanticModel] = PField(default_factory=list, max_length=30)
    dimensions: list[Dimension] = PField(default_factory=list, max_length=100)
    metrics: list[Metric] = PField(default_factory=list, max_length=100)
    filters: list[FixedFilter] = PField(default_factory=list, max_length=100)
    relations: list[Relation] = PField(default_factory=list, max_length=100)
    entities: list[EntityEntry] = PField(default_factory=list, max_length=500)

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError, ValueError:
            raise ValueError("请选择有效的 IANA 时区") from None
        return value


class TopicCreate(StrictModel):
    name: str = PField(min_length=1, max_length=80)
    description: str = PField(default="", max_length=500)
    source_id: uuid.UUID
    owner: str = PField(min_length=1, max_length=120)


class DraftUpdate(StrictModel):
    expected_revision: int = PField(ge=1)
    name: str = PField(min_length=1, max_length=80)
    description: str = PField(default="", max_length=500)
    enabled: bool
    definition: SemanticDefinition


class RevisionRequest(StrictModel):
    expected_revision: int = PField(ge=1)


class PublishRequest(RevisionRequest):
    note: str = PField(min_length=1, max_length=300)


class MembersUpdate(RevisionRequest):
    user_ids: list[uuid.UUID] = PField(max_length=200)


class ImportRequest(RevisionRequest):
    content: str = PField(min_length=1, max_length=200_000)


class Topic(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=80)
    name_key: str = Field(max_length=160, unique=True)
    description: str = Field(default="", max_length=500)
    source_id: uuid.UUID = Field(
        foreign_key="datasource.id", ondelete="RESTRICT", index=True
    )
    enabled: bool = True
    revision: int = 1
    current_version: int = 0
    draft: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class TopicMember(SQLModel, table=True):
    topic_id: uuid.UUID = Field(
        foreign_key="topic.id", ondelete="CASCADE", primary_key=True
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id", ondelete="CASCADE", primary_key=True
    )


class SemanticRelease(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("topic_id", "version"),)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    topic_id: uuid.UUID = Field(foreign_key="topic.id", ondelete="RESTRICT", index=True)
    version: int
    definition: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    catalog_version: int
    source_revision: int
    scope_revision: int
    binding_digest: str = Field(max_length=64)
    published_by: uuid.UUID
    note: str = Field(max_length=300)
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class TopicAudit(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    topic_id: uuid.UUID = Field(index=True)
    actor_id: uuid.UUID
    action: str = Field(max_length=40)
    revision: int
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class ValidationIssue(StrictModel):
    severity: Literal["error", "warning"]
    code: str
    path: str
    message: str


class ValidationReport(StrictModel):
    valid: bool
    issues: list[ValidationIssue]
    catalog_version: int
    draft_revision: int = 0
    binding_digest: str


class TopicSummary(StrictModel):
    id: uuid.UUID
    name: str
    description: str
    source_id: uuid.UUID | None = None
    source_name: str | None = None
    revision: int
    current_version: int
    enabled: bool
    availability: Literal["draft", "ready", "needs_review", "disabled"]
    metric_count: int
    dimension_count: int
    updated_at: datetime


class TopicDetail(TopicSummary):
    definition: SemanticDefinition
    member_ids: list[uuid.UUID]


class ReleasePublic(StrictModel):
    id: uuid.UUID
    version: int
    note: str
    catalog_version: int
    created_at: datetime
    metric_count: int
    dimension_count: int
    changes: list[str]


class ExportPublic(StrictModel):
    filename: str
    content: str


class PublishedMetric(StrictModel):
    id: str
    label: str
    description: str
    aliases: list[str]
    unit: str
    aggregation: str
    additivity: str
    allowed_dimensions: list[str]
    time_dimension: str | None


class PublishedDimension(StrictModel):
    id: str
    label: str
    description: str
    aliases: list[str]
    value_type: str


class PublishedTopic(StrictModel):
    id: uuid.UUID
    name: str
    description: str
    version: int
    owner: str
    timezone: str
    metrics: list[PublishedMetric]
    dimensions: list[PublishedDimension]
