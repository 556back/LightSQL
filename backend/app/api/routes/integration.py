import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import col, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.modules.datasources.models import now
from app.modules.integration import service as svc
from app.modules.integration.models import (
    AnswerInput,
    ClientInput,
    ClientUpdate,
    EmbedSession,
    IdentityInput,
    IntegrationAudit,
    IntegrationClient,
    IntegrationIdentity,
    IntegrationResult,
    IntegrationTask,
    QueryInput,
    SessionInput,
    SessionPublic,
    TaskPublic,
    TicketInput,
    TokenInput,
    TokenPublic,
)
from app.modules.query import service as queries

router = APIRouter(prefix=svc.PREFIX, tags=["integration"])
admin_router = APIRouter(
    prefix="/integrations",
    tags=["integrations-admin"],
    dependencies=[Depends(get_current_active_superuser)],
)
bearer = HTTPBearer(auto_error=False)


def authenticated(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
):
    if not credentials:
        svc.fail(401, "需要应用或嵌入会话令牌")
    p = svc.authenticate(session, credentials.credentials)
    svc.rate_limit(session, p)
    return p


PrincipalDep = Annotated[svc.Principal, Depends(authenticated)]
Key = Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=128)]


@admin_router.get("/")
def clients(session: SessionDep) -> list[dict]:
    return [svc.client_public(c) for c in session.exec(select(IntegrationClient)).all()]


@admin_router.post("/", status_code=201)
def create_client(body: ClientInput, session: SessionDep) -> dict:
    queries.gate(session)
    return svc.create_client(session, body)


@admin_router.post("/check")
def check_client(body: ClientInput, session: SessionDep) -> dict:
    """Inspect configuration without issuing tokens, SQL or model requests."""
    user = svc.user_record(session, body.ceiling_user_id)
    checks = []
    for topic_id in dict.fromkeys(body.topic_ids):
        try:
            topic, release, _, _, _, grant, _ = queries.resolve(session, topic_id, user)
            checks.append(
                {
                    "topic_id": str(topic_id),
                    "name": topic.name,
                    "ok": True,
                    "message": f"已发布 v{release.version}，可用指标 {len(grant.metric_ids)} 项、维度 {len(grant.dimension_ids)} 项",
                }
            )
        except HTTPException as exc:
            checks.append(
                {"topic_id": str(topic_id), "ok": False, "message": str(exc.detail)}
            )
    warnings = []
    if not body.enabled:
        warnings.append("应用已停用，启用后才能调用。")
    if "embed" in body.scopes and not body.origins:
        warnings.append("尚未填写允许嵌入的来源，嵌入页面将无法授权。")
    if "embed" in body.scopes and "ask" not in body.scopes:
        warnings.append("嵌入问数需要同时开启自然语言问数能力。")
    if "explore" in body.scopes and "ask" not in body.scopes:
        warnings.append("自由探索需要同时开启自然语言问数能力。")
    if body.model_calls_per_day == 0 and set(body.scopes) & {"ask", "analysis"}:
        warnings.append("模型调用额度为 0，自然语言问数和结果分析将无法执行。")
    return {
        "ok": all(c["ok"] for c in checks) and not warnings,
        "topics": checks,
        "warnings": warnings,
    }


@admin_router.put("/{client_id}")
def update_client(
    client_id: uuid.UUID, body: ClientUpdate, session: SessionDep
) -> dict:
    queries.gate(session)
    client = session.get(IntegrationClient, client_id)
    if not client or client.revision != body.expected_revision:
        svc.fail(409, "应用配置已变化，请刷新")
    if body.ceiling_user_id != client.ceiling_user_id:
        svc.fail(409, "应用权限上限用户不可改绑；请创建新应用")
    svc.user_record(session, body.ceiling_user_id)
    client.config = body.model_dump(mode="json", exclude={"expected_revision"})
    client.enabled, client.name = body.enabled, body.name
    client.revision += 1
    session.add(client)
    svc.audit(session, client.id, "client_updated")
    session.commit()
    return svc.client_public(client)


@admin_router.post("/{client_id}/rotate-secret")
def rotate(client_id: uuid.UUID, session: SessionDep) -> dict:
    import secrets

    from app.core.security import get_password_hash

    queries.gate(session)
    client = session.get(IntegrationClient, client_id)
    if not client:
        svc.fail(404, "应用不存在")
    secret = secrets.token_urlsafe(48)
    client.secret_hash = get_password_hash(secret)
    client.revision += 1
    session.add(client)
    svc.audit(session, client.id, "secret_rotated")
    session.commit()
    return {"client_secret": secret, "revision": client.revision}


@admin_router.get("/{client_id}/identities")
def identities(client_id: uuid.UUID, session: SessionDep) -> list[IntegrationIdentity]:
    return list(
        session.exec(
            select(IntegrationIdentity).where(
                IntegrationIdentity.client_id == client_id
            )
        ).all()
    )


@admin_router.put("/{client_id}/identities")
def identity(
    client_id: uuid.UUID, body: IdentityInput, session: SessionDep
) -> IntegrationIdentity:
    queries.gate(session)
    client = session.get(IntegrationClient, client_id)
    if not client:
        svc.fail(404, "应用不存在")
    if body.subject == "$app":
        svc.fail(422, "保留的应用主体不可修改")
    record = svc.identity(session, client, body.subject, body.user_id, body.enabled)
    client.revision += 1
    session.add(client)
    svc.audit(session, client.id, "identity_updated", record.id)
    session.commit()
    return record


@admin_router.get("/{client_id}/audit")
def audit(client_id: uuid.UUID, session: SessionDep) -> list[IntegrationAudit]:
    return list(
        session.exec(
            select(IntegrationAudit)
            .where(
                IntegrationAudit.client_id == client_id,
                IntegrationAudit.action != "request",
            )
            .order_by(col(IntegrationAudit.created_at).desc())
            .limit(100)
        ).all()
    )


@router.post("/token", response_model=TokenPublic)
def token(body: TokenInput, session: SessionDep) -> dict:
    return svc.token(session, body)


@router.get("/topics")
def topics(session: SessionDep, p: PrincipalDep) -> list[dict]:
    result = []
    for topic_id in p.client.config["topic_ids"]:
        try:
            uid = uuid.UUID(topic_id)
            svc.topic_access(p, uid)
            context = queries.resolve(session, uid, p.actor)
            result.append(
                {
                    "id": topic_id,
                    "name": context[0].name,
                    "semantic_version": context[1].version,
                }
            )
        except HTTPException:
            continue
    return result


@router.get("/topics/{topic_id}/catalog")
def catalog(topic_id: uuid.UUID, session: SessionDep, p: PrincipalDep) -> dict:
    svc.topic_access(p, topic_id)
    context = queries.resolve(session, topic_id, p.actor)
    definition, grant = context[2], context[5]
    return {
        "topic_id": str(topic_id),
        "semantic_version": context[1].version,
        "metrics": [
            {"id": m.id, "label": m.label, "description": m.description, "unit": m.unit}
            for m in definition.metrics
            if m.id in grant.metric_ids
        ],
        "dimensions": [
            {"id": d.id, "label": d.label, "value_type": d.value_type}
            for d in definition.dimensions
            if d.id in grant.dimension_ids
        ],
    }


@router.post("/answers", status_code=202, response_model=TaskPublic)
def answer(body: AnswerInput, key: Key, session: SessionDep, p: PrincipalDep) -> dict:
    return svc.task_public(session, svc.submit(session, p, "answer", body, key))


@router.post("/queries", status_code=202, response_model=TaskPublic)
def query(body: QueryInput, key: Key, session: SessionDep, p: PrincipalDep) -> dict:
    return svc.task_public(session, svc.submit(session, p, "query", body, key))


@router.get("/tasks", response_model=list[TaskPublic])
def tasks(session: SessionDep, p: PrincipalDep) -> list[dict]:
    records = session.exec(
        select(IntegrationTask)
        .where(
            IntegrationTask.identity_id == p.identity.id,
            IntegrationTask.expires_at > now(),
        )
        .order_by(col(IntegrationTask.created_at).desc())
        .limit(50)
    ).all()
    result = []
    for task in records:
        try:
            result.append(svc.task_public(session, svc.task_owned(session, p, task.id)))
        except HTTPException:
            continue
    return result


@router.get("/tasks/{task_id}", response_model=TaskPublic)
def task(task_id: uuid.UUID, session: SessionDep, p: PrincipalDep) -> dict:
    return svc.task_public(session, svc.task_owned(session, p, task_id))


@router.get("/tasks/{task_id}/result", response_model=IntegrationResult)
def result(task_id: uuid.UUID, session: SessionDep, p: PrincipalDep) -> dict:
    return svc.result(session, p, svc.task_owned(session, p, task_id))


@router.post("/tasks/{task_id}/analysis", status_code=202, response_model=TaskPublic)
def analysis(
    task_id: uuid.UUID, key: Key, session: SessionDep, p: PrincipalDep
) -> dict:
    parent = svc.task_owned(session, p, task_id)
    svc.result(session, p, parent)
    return svc.task_public(
        session, svc.submit(session, p, "analysis", None, key, parent)
    )


@router.post("/tasks/{task_id}/cancel", response_model=TaskPublic)
def cancel(task_id: uuid.UUID, session: SessionDep, p: PrincipalDep) -> dict:
    queries.gate(session)
    task = svc.task_owned(session, p, task_id, check_policy=False)
    if task.status in svc.ACTIVE:
        task.cancel_requested = True
        task.status = "cancelling" if task.lease_id or task.query_id else "cancelled"
        task.message = "正在取消" if task.status == "cancelling" else "已取消"
        session.add(task)
        session.commit()
    return svc.task_public(session, task)


@router.post("/embed/tickets", status_code=201)
def ticket(body: TicketInput, session: SessionDep, p: PrincipalDep) -> dict:
    return svc.ticket(session, p, body)


@router.get("/embed/config/{client_id}")
def embed_config(client_id: uuid.UUID, session: SessionDep) -> dict:
    client = session.get(IntegrationClient, client_id)
    if not client or not client.enabled or "embed" not in client.config["scopes"]:
        svc.fail(404, "嵌入应用不可用")
    return {
        "name": client.name,
        "origins": client.config["origins"],
        "scopes": client.config["scopes"],
    }


@router.post("/embed/sessions", status_code=201, response_model=SessionPublic)
def exchange(body: SessionInput, session: SessionDep) -> dict:
    return svc.exchange(session, body)


@router.delete("/embed/sessions/{session_id}")
def revoke(session_id: uuid.UUID, session: SessionDep, p: PrincipalDep) -> dict:
    queries.gate(session)
    record = session.get(EmbedSession, session_id)
    if (
        not record
        or record.identity_id != p.identity.id
        or (p.embed and p.embed.id != record.id)
    ):
        svc.fail(404, "嵌入会话不存在")
    record.revoked = True
    session.add(record)
    # The query worker also verifies this revocation during execution.
    for task in session.exec(
        select(IntegrationTask).where(
            IntegrationTask.embed_session_id == record.id,
            col(IntegrationTask.status).in_(svc.ACTIVE),
        )
    ).all():
        task.cancel_requested = True
        session.add(task)
    svc.audit(session, p.client.id, "embed_revoked", p.identity.id)
    session.commit()
    return {"revoked": True}


@router.delete("/embed/sessions")
def revoke_all(session: SessionDep, p: PrincipalDep) -> dict:
    from app.modules.integration.models import EmbedTicket

    if p.embed:
        svc.fail(403, "仅宿主后端可撤销该主体的全部嵌入会话")
    queries.gate(session)
    records = session.exec(
        select(EmbedSession).where(
            EmbedSession.identity_id == p.identity.id,
            col(EmbedSession.revoked).is_(False),
        )
    ).all()  # noqa: E712
    for record in records:
        record.revoked = True
        session.add(record)
    for pending in session.exec(
        select(EmbedTicket).where(
            EmbedTicket.identity_id == p.identity.id,
            col(EmbedTicket.consumed).is_(False),
        )
    ).all():
        pending.consumed = True
        session.add(pending)
    svc.audit(session, p.client.id, "embed_all_revoked", p.identity.id)
    session.commit()
    return {"revoked": len(records)}


@router.get("/openapi.json", include_in_schema=False)
def openapi():
    return JSONResponse(
        get_openapi(
            title="LightSQL Integration API", version="1.0.0", routes=router.routes
        )
    )
