import uuid
from datetime import datetime
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field as PField
from pydantic import SecretStr, field_validator, model_validator
from sqlalchemy import JSON, Column, DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.modules.assistant.models import AnalysisPublic
from app.modules.datasources.models import now
from app.modules.query.models import QueryPlan, QueryResult
from app.modules.semantic.models import StrictModel

SCOPES = {"query", "ask", "explore", "analysis", "embed"}


class ClientInput(StrictModel):
    name: str = PField(min_length=1, max_length=80)
    ceiling_user_id: uuid.UUID
    topic_ids: list[uuid.UUID] = PField(min_length=1, max_length=100)
    scopes: list[str] = PField(default_factory=lambda: ["query", "ask", "embed"])
    origins: list[str] = PField(default_factory=list, max_length=20)
    enabled: bool = True
    max_pending: int = PField(default=3, ge=1, le=20)
    requests_per_minute: int = PField(default=120, ge=10, le=600)
    model_calls_per_day: int = PField(default=100, ge=0, le=10000)
    assertion_issuer: str = PField(default="", max_length=300)
    assertion_public_key: str = PField(default="", max_length=5000)

    @field_validator("name", "assertion_issuer", "assertion_public_key", mode="before")
    @classmethod
    def trim_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("scopes")
    @classmethod
    def valid_scopes(cls, value):
        if not value or not set(value) <= SCOPES:
            raise ValueError("未知的应用能力")
        return sorted(set(value))

    @field_validator("origins")
    @classmethod
    def valid_origins(cls, value):
        for origin in value:
            parsed = urlsplit(origin)
            # Validate port syntax as well as the hostname.
            _ = parsed.port
            local = parsed.hostname in ("localhost", "127.0.0.1")
            if (
                (parsed.scheme != "https" and not (local and parsed.scheme == "http"))
                or not parsed.hostname
                or parsed.username
                or parsed.password
                or parsed.path
                or parsed.query
                or parsed.fragment
                or "*" in origin
                or origin != f"{parsed.scheme}://{parsed.netloc}"
            ):
                raise ValueError("来源须为完整 HTTPS 源；仅本机开发允许 HTTP")
        return sorted(set(value))

    @model_validator(mode="after")
    def assertion_config(self):
        if bool(self.assertion_issuer) != bool(self.assertion_public_key):
            raise ValueError("身份签发方与 RSA 公钥必须同时填写")
        if self.assertion_public_key:
            from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
            from cryptography.hazmat.primitives.serialization import load_pem_public_key

            key = load_pem_public_key(self.assertion_public_key.encode())
            if not isinstance(key, RSAPublicKey) or key.key_size < 2048:
                raise ValueError("需使用至少 2048 位 RSA 公钥")
        return self


class ClientUpdate(ClientInput):
    expected_revision: int = PField(ge=1)


class IntegrationClient(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    ceiling_user_id: uuid.UUID
    secret_hash: str
    revision: int = 1
    enabled: bool = True
    config: dict = Field(sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class IntegrationIdentity(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("client_id", "subject"),)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    client_id: uuid.UUID = Field(index=True)
    subject: str = Field(max_length=200)
    user_id: uuid.UUID
    actor_id: uuid.UUID = Field(unique=True, index=True)
    enabled: bool = True


class IdentityInput(StrictModel):
    subject: str = PField(min_length=1, max_length=200)
    user_id: uuid.UUID
    enabled: bool = True


class TokenInput(StrictModel):
    grant_type: Literal["client_credentials"] = "client_credentials"
    client_id: uuid.UUID
    client_secret: SecretStr
    subject_assertion: SecretStr | None = None


class EmbedTicket(SQLModel, table=True):
    id: str = Field(primary_key=True, max_length=64)
    identity_id: uuid.UUID
    revision: int
    origin: str
    challenge: str
    topic_id: uuid.UUID | None = None
    consumed: bool = False
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class EmbedSession(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    identity_id: uuid.UUID = Field(index=True)
    revision: int
    topic_id: uuid.UUID | None = None
    revoked: bool = False
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class TicketInput(StrictModel):
    origin: str = PField(max_length=300)
    challenge: str = PField(min_length=32, max_length=128, pattern=r"^[a-zA-Z0-9_-]+$")
    topic_id: uuid.UUID | None = None


class SessionInput(StrictModel):
    ticket: SecretStr
    challenge: str = PField(min_length=32, max_length=128)


class AnswerInput(StrictModel):
    topic_id: uuid.UUID
    question: str = PField(min_length=1, max_length=2000)
    mode: Literal["metrics", "auto", "explore"] = "metrics"
    include_analysis: bool = False
    conversation_id: uuid.UUID | None = None
    expected_revision: int = PField(default=0, ge=0)
    entity_choices: dict[str, str] = PField(default_factory=dict, max_length=20)


class QueryInput(StrictModel):
    topic_id: uuid.UUID
    plan: QueryPlan
    include_analysis: bool = False


class IntegrationTask(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("identity_id", "operation", "idempotency_key"),)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    client_id: uuid.UUID = Field(index=True)
    identity_id: uuid.UUID = Field(index=True)
    operation: str
    idempotency_key: str = Field(max_length=128)
    digest: str
    topic_id: uuid.UUID
    policy_digest: str
    encrypted_input: str
    encrypted_output: str = ""
    status: str = Field(default="queued", index=True)
    message: str = "已接收请求"
    conversation_id: uuid.UUID | None = Field(default=None, index=True)
    turn_id: uuid.UUID | None = None
    query_id: uuid.UUID | None = None
    parent_id: uuid.UUID | None = None
    embed_session_id: uuid.UUID | None = None
    cancel_requested: bool = False
    analysis_status: str = "not_requested"
    lease_id: uuid.UUID | None = None
    lease_until: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class IntegrationAudit(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    client_id: uuid.UUID = Field(index=True)
    identity_id: uuid.UUID | None = None
    task_id: uuid.UUID | None = None
    action: str = Field(index=True)
    created_at: datetime = Field(
        default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class AssertionUse(SQLModel, table=True):
    id: str = Field(primary_key=True, max_length=64)
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class TaskPublic(StrictModel):
    task_id: uuid.UUID
    topic_id: uuid.UUID
    conversation_id: uuid.UUID | None
    revision: int
    status: str
    message: str
    analysis_status: str
    expires_at: datetime
    status_url: str
    clarification: dict | None
    question: str


class IntegrationResult(QueryResult):
    task_id: uuid.UUID
    row_count: int
    queried_at: datetime | None
    expires_at: datetime
    semantic_version: int
    chart: str
    analysis: AnalysisPublic | None
    analysis_status: str
    evidence: dict | None
    warnings: list[str]


class TokenPublic(StrictModel):
    access_token: str
    token_type: Literal["bearer"]
    expires_in: int
    session_id: uuid.UUID | None


class SessionPublic(TokenPublic):
    topic_id: uuid.UUID | None
    principal_id: uuid.UUID
