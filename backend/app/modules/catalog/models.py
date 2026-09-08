import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import JSON, Column, DateTime
from sqlmodel import Field, SQLModel

from app.modules.datasources.models import now


class ObjectRef(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_name: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=128)
    kind: Literal["table", "view"]

    @field_validator("schema_name", "name")
    @classmethod
    def valid_identifier(cls, value: str) -> str:
        if not value.strip() or any(ord(c) < 32 for c in value):
            raise ValueError("对象名称不能为空或包含控制字符")
        return value  # Preserve case, spaces, punctuation and quoted identifiers.


class ColumnMeta(BaseModel):
    name: str
    ordinal: int
    data_type: str
    nullable: bool
    comment: str = ""
    primary_key: bool = False


class ForeignKeyMeta(BaseModel):
    name: str
    columns: list[str]
    target_schema: str
    target_table: str
    target_columns: list[str]


class TableMeta(ObjectRef):
    model_config = ConfigDict(extra="forbid", frozen=False)
    comment: str = ""
    columns: list[ColumnMeta]
    foreign_keys: list[ForeignKeyMeta] = []
    warnings: list[str] = []


class ScopeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=0)
    expected_source_revision: int = Field(ge=1)
    objects: list[ObjectRef] = Field(max_length=200)

    @field_validator("objects")
    @classmethod
    def unique_objects(cls, value: list[ObjectRef]) -> list[ObjectRef]:
        if len({(x.schema_name, x.name) for x in value}) != len(value):
            raise ValueError("不能重复选择同一个对象")
        return sorted(value, key=lambda x: (x.schema_name, x.name))


class CatalogState(SQLModel, table=True):
    source_id: uuid.UUID = Field(
        foreign_key="datasource.id", ondelete="CASCADE", primary_key=True
    )
    revision: int = 1
    source_revision: int
    scope: list[dict[str, Any]] = Field(sa_column=Column(JSON, nullable=False))
    snapshot: list[dict[str, Any]] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )
    version: int = 0
    synced_scope_revision: int = 0
    synced_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )


class CatalogPublic(BaseModel):
    source_id: uuid.UUID
    revision: int
    source_revision: int
    scope: list[ObjectRef]
    tables: list[TableMeta]
    version: int
    synced_at: datetime | None
    needs_sync: bool
    needs_confirmation: bool


class Change(BaseModel):
    action: Literal["added", "removed", "changed"]
    path: str
    detail: str
    before: str | None = None
    after: str | None = None


class SyncJob(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # Retain job/audit records after deleting a source; never store credentials.
    source_id: uuid.UUID = Field(index=True)
    actor_id: uuid.UUID
    source_revision: int
    scope_revision: int
    status: str = Field(default="queued", max_length=20, index=True)
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
    message: str = Field(default="等待同步进程处理", max_length=300)
    table_count: int = 0
    version: int | None = None
    changes: list[dict[str, Any]] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )


class SyncJobPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    source_id: uuid.UUID
    source_revision: int
    scope_revision: int
    status: str
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    message: str
    table_count: int
    version: int | None
    changes: list[Change]
