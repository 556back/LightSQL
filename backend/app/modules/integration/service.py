import hashlib
import json
import secrets
import uuid
from dataclasses import dataclass
from datetime import timedelta
from typing import NoReturn

import jwt
from fastapi import HTTPException
from sqlmodel import col, select

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import User
from app.modules.datasources.models import now
from app.modules.datasources.service import decrypt_password, encrypt_password
from app.modules.integration.models import (
    AssertionUse,
    ClientInput,
    EmbedSession,
    EmbedTicket,
    IntegrationAudit,
    IntegrationClient,
    IntegrationIdentity,
    IntegrationTask,
)
from app.modules.query import service as queries
from app.modules.query.compiler import fingerprint
from app.modules.query.models import QueryGrant, TableAccess

PREFIX = "/api/integration/v1"
AUDIENCE = "lightsql-integration"
ISSUER = "lightsql"
ACTIVE = {
    "queued",
    "planning",
    "querying",
    "analyzing",
    "cancelling",
    "cleanup_pending",
}


def fail(code: int, message: str) -> NoReturn:
    raise HTTPException(code, message)


def seal(data):
    return encrypt_password(json.dumps(data, ensure_ascii=False))


def unseal(data):
    return json.loads(decrypt_password(data)) if data else {}


def audit(session, client_id, action, identity_id=None, task_id=None):
    session.add(
        IntegrationAudit(
            client_id=client_id, identity_id=identity_id, task_id=task_id, action=action
        )
    )


def user_record(session, user_id):
    user = session.get(User, user_id, populate_existing=True)
    if not user or not user.is_active or user.is_superuser:
        fail(403, "集成执行身份必须映射到有效的非管理员用户")
    if session.exec(
        select(IntegrationIdentity).where(IntegrationIdentity.actor_id == user.id)
    ).first():
        fail(403, "不能将集成代理作为身份映射来源")
    return user


def config(client):
    return ClientInput.model_validate(client.config)


def scheduling_actor(session, actor_id):
    record = session.exec(
        select(IntegrationIdentity).where(IntegrationIdentity.actor_id == actor_id)
    ).first()
    return record.user_id if record else actor_id


def client_public(client):
    return {"id": str(client.id), "revision": client.revision, **client.config}


def identity(session, client, subject, user_id, enabled=True):
    user_record(session, user_id)
    record = session.exec(
        select(IntegrationIdentity).where(
            IntegrationIdentity.client_id == client.id,
            IntegrationIdentity.subject == subject,
        )
    ).first()
    if record and record.user_id != user_id:
        fail(409, "身份映射不可改绑用户；请停用旧映射并使用新的外部主体标识")
    if not record:
        actor = User(
            email=f"integration-{uuid.uuid4().hex}@internal.invalid",
            hashed_password=get_password_hash(secrets.token_urlsafe(48)),
            is_active=True,
            full_name=f"集成 · {client.name}",
        )
        session.add(actor)
        session.flush()
        record = IntegrationIdentity(
            client_id=client.id, subject=subject, user_id=user_id, actor_id=actor.id
        )
    record.enabled = enabled
    session.add(record)
    session.flush()
    return record


def create_client(session, body):
    user_record(session, body.ceiling_user_id)
    secret = secrets.token_urlsafe(48)
    client = IntegrationClient(
        name=body.name,
        ceiling_user_id=body.ceiling_user_id,
        secret_hash=get_password_hash(secret),
        enabled=body.enabled,
        config=body.model_dump(mode="json"),
    )
    session.add(client)
    session.flush()
    identity(session, client, "$app", body.ceiling_user_id)
    audit(session, client.id, "client_created")
    session.commit()
    return {**client_public(client), "client_secret": secret}


@dataclass
class Principal:
    client: IntegrationClient
    identity: IntegrationIdentity
    actor: User
    embed: EmbedSession | None = None


def principal(session, identity_id):
    record = session.get(IntegrationIdentity, identity_id, populate_existing=True)
    if not record or not record.enabled:
        fail(403, "集成身份已停用")
    client = session.get(IntegrationClient, record.client_id, populate_existing=True)
    if not client or not client.enabled:
        fail(403, "接入应用已停用")
    user_record(session, record.user_id)
    user_record(session, client.ceiling_user_id)
    actor = session.get(User, record.actor_id, populate_existing=True)
    if not actor or not actor.is_active or actor.is_superuser:
        fail(403, "集成执行身份不可用")
    return Principal(client, record, actor)


def scope(p, name):
    if name not in p.client.config["scopes"]:
        fail(403, "应用未获此能力授权")


def topic_access(p, topic_id):
    if str(topic_id) not in p.client.config["topic_ids"] or (
        p.embed and p.embed.topic_id and p.embed.topic_id != topic_id
    ):
        fail(403, "主题超出应用或嵌入会话范围")


def intersect(left: QueryGrant, right: QueryGrant, actor_id):
    # Row predicates are ANDed by the existing compiler. Keep both sets, but
    # never let one side's scope supply a model missing from the other side.
    left_models = {r.model_id for r in left.rows}
    right_models = {r.model_id for r in right.rows}
    allowed_models = left_models | right_models
    if not left.unrestricted and not right.unrestricted:
        allowed_models = left_models & right_models
    rows = [r for r in left.rows + right.rows if r.model_id in allowed_models]
    right_tables = {t.model_id: set(t.columns) for t in right.exploration}
    tables = []
    for table in left.exploration:
        columns = sorted(set(table.columns) & right_tables.get(table.model_id, set()))
        if columns:
            tables.append(TableAccess(model_id=table.model_id, columns=columns))
    return QueryGrant(
        user_id=actor_id,
        metric_ids=sorted(set(left.metric_ids) & set(right.metric_ids)),
        dimension_ids=sorted(set(left.dimension_ids) & set(right.dimension_ids)),
        exploration=tables,
        unrestricted=left.unrestricted and right.unrestricted,
        rows=rows,
    )


def resolve_actor(session, topic_id, actor):
    record = session.exec(
        select(IntegrationIdentity).where(IntegrationIdentity.actor_id == actor.id)
    ).first()
    if not record:
        return None
    p = principal(session, record.id)
    topic_access(p, topic_id)
    user = user_record(session, record.user_id)
    ceiling = user_record(session, p.client.ceiling_user_id)
    context = list(queries.resolve(session, topic_id, user))
    upper = queries.resolve(session, topic_id, ceiling)
    grant = intersect(context[5], upper[5], actor.id)
    if "explore" not in p.client.config["scopes"]:
        grant.exploration = []
    context[5] = grant
    context[6] = fingerprint(
        {
            "user": context[6],
            "ceiling": upper[6],
            "client": str(p.client.id),
            "revision": p.client.revision,
            "identity": str(record.id),
            "grant": grant.model_dump(mode="json"),
        }
    )
    return tuple(context)


def issue(p, embed=None):
    expiry = now() + timedelta(minutes=15)
    claims = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": str(p.identity.id),
        "cid": str(p.client.id),
        "rev": p.client.revision,
        "iat": now(),
        "exp": expiry,
        "kind": "embed" if embed else "application",
    }
    if embed:
        claims["sid"] = str(embed.id)
    return {
        "access_token": jwt.encode(claims, settings.SECRET_KEY, algorithm="HS256"),
        "token_type": "bearer",
        "expires_in": 900,
        "session_id": str(embed.id) if embed else None,
    }


def authenticate(session, token):
    try:
        claims = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
            audience=AUDIENCE,
            issuer=ISSUER,
            options={"require": ["exp", "iat", "sub", "cid", "rev", "kind"]},
        )
        p = principal(session, uuid.UUID(claims["sub"]))
        if str(p.client.id) != claims["cid"] or p.client.revision != claims["rev"]:
            fail(401, "应用令牌已失效")
        if claims["kind"] == "embed":
            embed = session.get(EmbedSession, uuid.UUID(claims["sid"]))
            if (
                not embed
                or embed.identity_id != p.identity.id
                or embed.revoked
                or embed.revision != p.client.revision
                or queries.utc(embed.expires_at) <= now()
            ):
                fail(401, "嵌入会话已失效")
            p.embed = embed
        elif claims["kind"] != "application":
            fail(401, "令牌类型不支持")
        return p
    except jwt.InvalidTokenError, ValueError, KeyError, TypeError:
        fail(401, "访问令牌无效或已过期")


def token(session, body):
    queries.gate(session)
    client = session.get(IntegrationClient, body.client_id)
    if (
        not client
        or not client.enabled
        or not verify_password(
            body.client_secret.get_secret_value(), client.secret_hash
        )[0]
    ):
        fail(401, "应用凭证无效")
    subject = "$app"
    if body.subject_assertion:
        cfg = config(client)
        if not cfg.assertion_public_key:
            fail(403, "此应用未配置可信身份签发方")
        try:
            claims = jwt.decode(
                body.subject_assertion.get_secret_value(),
                cfg.assertion_public_key,
                algorithms=["RS256"],
                issuer=cfg.assertion_issuer,
                audience=AUDIENCE,
                options={"require": ["sub", "exp", "iat", "jti", "client_id"]},
            )
            if (
                claims["client_id"] != str(client.id)
                or claims["sub"] == "$app"
                or not isinstance(claims["sub"], str)
                or len(claims["sub"]) > 200
                or claims["exp"] - claims["iat"] > 120
            ):
                fail(401, "用户身份声明不符合约定")
            digest = fingerprint([str(client.id), claims["jti"]])
            if session.get(AssertionUse, digest):
                fail(401, "用户身份声明已经使用")
            session.add(
                AssertionUse(id=digest, expires_at=now() + timedelta(minutes=3))
            )
            subject = claims["sub"]
        except jwt.InvalidTokenError, ValueError, TypeError, KeyError:
            fail(401, "用户身份声明无效")
    record = session.exec(
        select(IntegrationIdentity).where(
            IntegrationIdentity.client_id == client.id,
            IntegrationIdentity.subject == subject,
        )
    ).first()
    if not record:
        fail(403, "外部用户尚未登记映射")
    p = principal(session, record.id)
    rate_limit(session, p)
    audit(session, client.id, "token_issued", record.id)
    session.commit()
    return issue(p)


def rate_limit(session, p):
    queries.gate(session)
    count = len(
        session.exec(
            select(IntegrationAudit.id).where(
                IntegrationAudit.client_id == p.client.id,
                IntegrationAudit.action == "request",
                IntegrationAudit.created_at > now() - timedelta(minutes=1),
            )
        ).all()
    )
    if count >= p.client.config["requests_per_minute"]:
        raise HTTPException(429, "应用调用频率超过限额", headers={"Retry-After": "5"})
    audit(session, p.client.id, "request", p.identity.id)
    session.commit()


def ticket(session, p, body):
    scope(p, "embed")
    if p.embed:
        fail(403, "浏览器会话不能签发票据")
    if body.origin not in p.client.config["origins"]:
        fail(403, "未登记的嵌入来源")
    if body.topic_id:
        topic_access(p, body.topic_id)
        queries.resolve(session, body.topic_id, p.actor)
    secret = secrets.token_urlsafe(48)
    session.add(
        EmbedTicket(
            id=hashlib.sha256(secret.encode()).hexdigest(),
            identity_id=p.identity.id,
            revision=p.client.revision,
            origin=body.origin,
            challenge=body.challenge,
            topic_id=body.topic_id,
            expires_at=now() + timedelta(seconds=60),
        )
    )
    audit(session, p.client.id, "ticket_issued", p.identity.id)
    session.commit()
    return {"ticket": secret, "expires_in": 60}


def exchange(session, body):
    queries.gate(session)
    key = hashlib.sha256(body.ticket.get_secret_value().encode()).hexdigest()
    record = session.get(EmbedTicket, key)
    if (
        not record
        or record.consumed
        or queries.utc(record.expires_at) <= now()
        or not secrets.compare_digest(record.challenge, body.challenge)
    ):
        fail(401, "嵌入票据无效、过期或已使用")
    p = principal(session, record.identity_id)
    scope(p, "embed")
    if (
        record.revision != p.client.revision
        or record.origin not in p.client.config["origins"]
    ):
        fail(401, "嵌入应用配置已变更")
    record.consumed = True
    embed = EmbedSession(
        identity_id=p.identity.id,
        revision=p.client.revision,
        topic_id=record.topic_id,
        expires_at=now() + timedelta(minutes=15),
    )
    session.add_all([record, embed])
    session.flush()
    response = {
        **issue(p, embed),
        "topic_id": str(record.topic_id) if record.topic_id else None,
        "principal_id": str(p.identity.id),
    }
    session.commit()
    return response


def task_owned(session, p, task_id, check_policy=True):
    task = session.get(IntegrationTask, task_id, populate_existing=True)
    if not task or task.identity_id != p.identity.id or task.client_id != p.client.id:
        fail(404, "任务不存在")
    topic_access(p, task.topic_id)
    if task.embed_session_id:
        embed = session.get(EmbedSession, task.embed_session_id)
        if not embed or embed.revoked:
            fail(403, "任务所属嵌入会话已撤销")
    if check_policy and queries.utc(task.expires_at) > now():
        context = queries.resolve(session, task.topic_id, p.actor)
        if context[6] != task.policy_digest:
            fail(403, "任务权限或发布版本已变化")
    return task


def submit(session, p, operation, body, key, parent=None):
    scope(
        p,
        "analysis"
        if operation == "analysis"
        else "ask"
        if operation == "answer"
        else "query",
    )
    if body is not None:
        data = body.model_dump(mode="json")
        topic_id = body.topic_id
    else:
        if parent is None:
            fail(422, "缺少请求或待分析任务")
        data = {"parent_id": str(parent.id)}
        topic_id = parent.topic_id
    topic_access(p, topic_id)
    if data.get("mode", "metrics") != "metrics":
        scope(p, "explore")
    if data.get("include_analysis"):
        scope(p, "analysis")
    if not key or len(key) > 128 or not all(33 <= ord(c) <= 126 for c in key):
        fail(422, "需提供 1–128 位可见 ASCII Idempotency-Key")
    digest = fingerprint(data)
    queries.gate(session)
    prior = session.exec(
        select(IntegrationTask).where(
            IntegrationTask.identity_id == p.identity.id,
            IntegrationTask.operation == operation,
            IntegrationTask.idempotency_key == key,
        )
    ).first()
    if prior:
        if prior.digest != digest:
            fail(409, "相同幂等键不能更换输入")
        return task_owned(session, p, prior.id)
    active = session.exec(
        select(IntegrationTask).where(
            IntegrationTask.client_id == p.client.id,
            col(IntegrationTask.status).in_(ACTIVE),
        )
    ).all()
    if len(active) >= p.client.config["max_pending"]:
        raise HTTPException(429, "应用在途任务已达上限", headers={"Retry-After": "5"})
    context = queries.resolve(session, topic_id, p.actor)
    if context[3].database_type not in ("postgresql", "mysql", "oracle"):
        fail(422, "集成接口当前仅支持 PostgreSQL、MySQL、Oracle")
    conversation_id = getattr(body, "conversation_id", None)
    if conversation_id:
        from app.modules.assistant import service as assistant

        existing = session.exec(
            select(IntegrationTask).where(
                IntegrationTask.identity_id == p.identity.id,
                IntegrationTask.conversation_id == conversation_id,
            )
        ).first()
        if not existing:
            fail(404, "会话不存在")
        task_owned(session, p, existing.id)
        conversation, _ = assistant.owned(session, conversation_id, p.actor)
        if (
            conversation.topic_id != topic_id
            or conversation.revision != body.expected_revision
        ):
            fail(409, "会话主题或版本不一致")
        if any(t.conversation_id == conversation_id for t in active):
            fail(409, "会话仍有未完成任务")
    elif operation == "answer" and body.expected_revision != 0:
        fail(409, "新会话版本必须为 0")
    task = IntegrationTask(
        client_id=p.client.id,
        identity_id=p.identity.id,
        operation=operation,
        idempotency_key=key,
        digest=digest,
        topic_id=topic_id,
        policy_digest=context[6],
        encrypted_input=seal(data),
        conversation_id=conversation_id,
        parent_id=parent.id if parent else None,
        embed_session_id=p.embed.id if p.embed else None,
        expires_at=min(queries.utc(parent.expires_at), now() + timedelta(hours=24))
        if parent
        else now() + timedelta(hours=24),
    )
    session.add(task)
    if operation == "answer" and not conversation_id:
        from app.modules.assistant.models import Conversation

        task.conversation_id = task.id
        session.add(
            Conversation(
                id=task.id,
                actor_id=p.actor.id,
                topic_id=topic_id,
                release_id=context[1].id,
                policy_fingerprint=context[6],
                expires_at=task.expires_at,
            )
        )
        session.add(task)
    audit(session, p.client.id, "submitted", p.identity.id, task.id)
    session.commit()
    return task


def task_public(session, task):
    from app.modules.assistant.models import Conversation

    expired = queries.utc(task.expires_at) <= now()
    conversation = (
        session.get(Conversation, task.conversation_id)
        if task.conversation_id
        else None
    )
    output = unseal(task.encrypted_output) if not expired else {}
    return {
        "task_id": str(task.id),
        "topic_id": str(task.topic_id),
        "conversation_id": str(task.conversation_id) if task.conversation_id else None,
        "revision": conversation.revision if conversation else 0,
        "status": "expired" if expired else task.status,
        "message": "结果已过期" if expired else task.message,
        "analysis_status": task.analysis_status,
        "expires_at": queries.utc(task.expires_at),
        "status_url": f"{PREFIX}/tasks/{task.id}",
        "clarification": output.get("clarification"),
        "question": unseal(task.encrypted_input).get("question", "")
        if not expired
        else "",
    }


def result(session, p, task):
    from app.modules.query.models import QueryResult

    if queries.utc(task.expires_at) <= now():
        fail(410, "查询结果已过期")
    if (
        task.status not in ("succeeded", "analyzing", "querying")
        or task.cancel_requested
    ):
        fail(409, "此任务没有可领取的结果")
    if not task.query_id:
        fail(409, "查询结果尚未就绪")
    job = queries.owned(session, task.query_id, p.actor, result=True)
    if job.status != "succeeded" or job.result is None:
        fail(409, "查询结果尚未就绪")
    output = unseal(task.encrypted_output)
    # Expose a dedicated public projection, never the internal plan/SQL.
    data = QueryResult.model_validate(job.result).model_dump(mode="json")
    return {
        **data,
        "task_id": str(task.id),
        "row_count": job.row_count,
        "queried_at": job.finished_at,
        "expires_at": min(queries.utc(job.expires_at), queries.utc(task.expires_at)),
        "semantic_version": job.semantic_version,
        "chart": output.get("chart", "table"),
        "analysis": output.get("analysis"),
        "analysis_status": task.analysis_status,
        "evidence": output.get("evidence"),
        "warnings": ["分析仅覆盖本次查询返回行"] if output.get("analysis") else [],
    }
