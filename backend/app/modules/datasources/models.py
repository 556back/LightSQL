import ipaddress
import re
import uuid
from datetime import UTC, datetime
from typing import Literal

from pydantic import SecretStr, field_validator
from sqlalchemy import JSON, Column, DateTime
from sqlmodel import Field, SQLModel
from sqlmodel.main import SQLModelConfig

DatabaseType = Literal["postgresql", "mysql", "oracle", "dameng", "kingbase"]
TlsMode = Literal["verify-full", "disable"]


def now() -> datetime:
    return datetime.now(UTC)


class DataSourceInput(SQLModel):
    model_config = SQLModelConfig(extra="forbid")

    name: str = Field(min_length=1, max_length=80)
    database_type: DatabaseType
    host: str = Field(min_length=1, max_length=253)
    port: int = Field(ge=1, le=65535)
    database: str = Field(min_length=1, max_length=128)
    username: str = Field(min_length=1, max_length=128)
    description: str = Field(default="", max_length=500)
    tls_mode: TlsMode = "verify-full"
    enabled: bool = True

    @field_validator("name")
    @classmethod
    def normalized_name_length(cls, value: str) -> str:
        if len(value.casefold()) > 80:
            raise ValueError("名称过长，请使用更短的名称")
        return value

    @field_validator("name", "database", "username", "description")
    @classmethod
    def clean_text(cls, value: str) -> str:
        value = value.strip()
        if any(ord(c) < 32 for c in value):
            raise ValueError("内容不能包含控制字符")
        return value

    @field_validator("name", "database", "username")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value:
            raise ValueError("请填写必填项")
        return value

    @field_validator("host")
    @classmethod
    def valid_host(cls, value: str) -> str:
        value = value.strip().lower()
        try:
            ipaddress.ip_address(value)
        except ValueError:
            if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", value):
                raise ValueError("请填写主机名或 IP，不包含协议、端口和路径")
        return value


class DataSourceCreate(DataSourceInput):
    password: SecretStr = Field(min_length=1, max_length=1024)


class DataSourceUpdate(DataSourceInput):
    # PUT replaces the public configuration; omitted password retains the secret.
    password: SecretStr | None = Field(default=None, min_length=1, max_length=1024)
    expected_revision: int = Field(ge=1)


class DataSource(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=80)
    name_key: str = Field(max_length=80, unique=True)
    database_type: str = Field(max_length=20)
    host: str = Field(max_length=253)
    port: int
    database: str = Field(max_length=128)
    username: str = Field(max_length=128)
    description: str = Field(default="", max_length=500)
    tls_mode: str = Field(default="verify-full", max_length=20)
    enabled: bool = True
    encrypted_password: str
    revision: int = 1
    status: str = Field(default="untested", max_length=20)
    last_tested_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    latency_ms: int | None = None
    last_error: str | None = Field(default=None, max_length=300)
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class DataSourcePublic(DataSourceInput):
    id: uuid.UUID
    revision: int
    status: str
    last_tested_at: datetime | None
    latency_ms: int | None
    last_error: str | None
    created_at: datetime
    updated_at: datetime
    has_password: bool = True


class DataSourcesPublic(SQLModel):
    data: list[DataSourcePublic]
    count: int


class ConnectionTestResult(SQLModel):
    success: bool
    message: str
    latency_ms: int
    tested_at: datetime
    # A successful SELECT 1 is not a privilege audit.
    readonly_verified: bool = False


class DataSourceAudit(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    datasource_id: uuid.UUID = Field(index=True)
    actor_id: uuid.UUID = Field(index=True)
    action: str = Field(max_length=30)
    details: dict[str, str | int | bool] = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
