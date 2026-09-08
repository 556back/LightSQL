import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlmodel import Session, col, select

from app.models import User
from app.modules.catalog.models import CatalogState, TableMeta
from app.modules.datasources.models import DataSource, now
from app.modules.query.compiler import (
    CompiledQuery,
    compile_plan,
    fingerprint,
    typed_value,
)
from app.modules.query.models import (
    PolicyPublic,
    PolicyUpdate,
    QueryEvent,
    QueryGate,
    QueryGrant,
    QueryJob,
    QueryJobPublic,
    QueryPlan,
    QueryPolicy,
    QueryPreview,
    QuerySubmission,
    SqlPlan,
    parse_plan,
)
from app.modules.semantic import service as semantic
from app.modules.semantic.models import SemanticDefinition, TopicMember

ACTIVE = ("queued", "running", "cancelling", "cleanup_pending")


def policy_binding(
    definition: SemanticDefinition, tables: list[TableMeta], grants: list[dict]
) -> str:
    metadata = {(t.schema_name, t.name): t for t in tables}
    models = {
        m.id: metadata.get((m.relation.schema_name, m.relation.name))
        for m in definition.models
    }
    signatures = []
    for grant in grants:
        for access in grant.get("exploration", []):
            table = models.get(access["model_id"])
            for name in access["columns"]:
                column = (
                    next((c for c in table.columns if c.name == name), None)
                    if table
                    else None
                )
                signatures.append(
                    [
                        access["model_id"],
                        name,
                        column.data_type if column else None,
                        column.nullable if column else None,
                    ]
                )
        for row in grant.get("rows", []):
            table = models.get(row["model_id"])
            column = (
                next((c for c in table.columns if c.name == row["column"]), None)
                if table
                else None
            )
            signatures.append(
                [
                    row["model_id"],
                    row["column"],
                    column.data_type if column else None,
                    column.nullable if column else None,
                ]
            )
    return fingerprint(signatures)


def utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def gate(session: Session) -> None:
    # The migration creates this singleton. Tests create metadata without migrations.
    if session.get(QueryGate, 1) is None:
        session.add(QueryGate(id=1))
        session.flush()
    session.exec(select(QueryGate).where(QueryGate.id == 1).with_for_update()).one()


def event(
    session: Session,
    topic_id: uuid.UUID,
    actor_id: uuid.UUID,
    action: str,
    job_id: uuid.UUID | None = None,
    detail: str = "",
) -> None:
    session.add(
        QueryEvent(
            topic_id=topic_id,
            actor_id=actor_id,
            action=action,
            job_id=job_id,
            detail=detail,
        )
    )


def resolve(session: Session, topic_id: uuid.UUID, user: User):
    if not user.is_active:
        raise HTTPException(403, "账号已停用")
    from app.modules.integration.service import resolve_actor

    integrated = resolve_actor(session, topic_id, user)
    if integrated is not None:
        return integrated
    topic, release = semantic.resolve_published(session, topic_id, user)
    definition = SemanticDefinition.model_validate(release.definition)
    state = session.get(CatalogState, topic.source_id)
    source = session.get(DataSource, topic.source_id)
    assert state is not None and source is not None
    grant = None
    if user.is_superuser:
        digest = fingerprint(
            {
                "admin": str(user.id),
                "release": str(release.id),
                "catalog_version": state.version,
            }
        )
    else:
        policy = session.get(QueryPolicy, topic.id)
        if (
            not policy
            or policy.release_id != release.id
            or policy.binding_digest
            != policy_binding(
                definition,
                [TableMeta.model_validate(t) for t in state.snapshot],
                policy.grants,
            )
        ):
            raise HTTPException(
                403, "查询授权尚未配置或语义版本已更新，请联系管理员确认"
            )
        grant = next(
            (
                QueryGrant.model_validate(g)
                for g in policy.grants
                if g["user_id"] == str(user.id)
            ),
            None,
        )
        if grant is None:
            raise HTTPException(403, "尚未获得本主题的查询权限")
        digest = fingerprint(
            {
                "revision": policy.revision,
                "release": str(release.id),
                "grant": grant.model_dump(mode="json"),
            }
        )
    return (
        topic,
        release,
        definition,
        source,
        [TableMeta.model_validate(t) for t in state.snapshot],
        grant,
        digest,
    )


def compile_for(
    session: Session, topic_id: uuid.UUID, user: User, plan: QueryPlan | SqlPlan
):
    context = resolve(session, topic_id, user)
    _, _, definition, source, tables, grant, _ = context
    if isinstance(plan, SqlPlan):
        from app.modules.query.exploration import compile_sql

        return context, compile_sql(
            definition, tables, source.database_type, plan, grant
        )
    return context, compile_plan(definition, tables, source.database_type, plan, grant)


def preview(
    session: Session, topic_id: uuid.UUID, user: User, plan: QueryPlan
) -> QueryPreview:
    context, compiled = compile_for(session, topic_id, user, plan)
    return QueryPreview(
        semantic_version=context[1].version,
        columns=compiled.columns,
        sql=compiled.sql if user.is_superuser else None,
        parameter_count=len(compiled.parameters),
        policy_label="管理员 · 全部授权数据"
        if user.is_superuser
        else "成员 · 已应用查询授权",
        limit=plan.limit,
        timeout_seconds=plan.timeout_seconds,
        notes=compiled.notes,
    )


def policy_public(session: Session, topic_id: uuid.UUID, user: User) -> PolicyPublic:
    topic, release, definition, _, tables, _, _ = resolve(session, topic_id, user)
    policy = session.get(QueryPolicy, topic.id)
    metadata = {(t.schema_name, t.name): t for t in tables}
    return PolicyPublic(
        revision=policy.revision if policy else 0,
        semantic_version=release.version,
        stale=bool(
            policy
            and (
                policy.release_id != release.id
                or policy.binding_digest
                != policy_binding(definition, tables, policy.grants)
            )
        ),
        grants=[QueryGrant.model_validate(g) for g in policy.grants] if policy else [],
        models=[
            {
                "id": m.id,
                "label": m.label,
                "columns": [
                    {"name": c.name, "data_type": c.data_type}
                    for c in metadata[(m.relation.schema_name, m.relation.name)].columns
                ],
            }
            for m in definition.models
        ],
    )


def save_policy(
    session: Session, topic_id: uuid.UUID, user: User, body: PolicyUpdate
) -> PolicyPublic:
    gate(session)
    topic = semantic.get_topic(session, topic_id, lock=True)
    _, release, definition, _, tables, _, _ = resolve(session, topic_id, user)
    policy = session.get(QueryPolicy, topic.id)
    if body.expected_revision != (policy.revision if policy else 0):
        raise HTTPException(409, "查询授权已被修改，请刷新后重试")
    if len({g.user_id for g in body.grants}) != len(body.grants):
        raise HTTPException(422, "不能重复配置同一成员")
    metadata = {(t.schema_name, t.name): t for t in tables}
    models = {
        m.id: metadata[(m.relation.schema_name, m.relation.name)]
        for m in definition.models
    }
    for grant in body.grants:
        member = session.get(User, grant.user_id)
        if (
            not member
            or not member.is_active
            or not session.get(TopicMember, (topic.id, grant.user_id))
        ):
            raise HTTPException(422, "请先将有效账号加入主题成员")
        if not set(grant.metric_ids) <= {m.id for m in definition.metrics} or not set(
            grant.dimension_ids
        ) <= {d.id for d in definition.dimensions}:
            raise HTTPException(422, "查询授权引用了不存在的指标或维度")
        if grant.unrestricted and grant.rows:
            raise HTTPException(422, "全部行访问与限定行范围不能同时配置")
        if len({a.model_id for a in grant.exploration}) != len(grant.exploration):
            raise HTTPException(422, "探索表不能重复配置")
        for access in grant.exploration:
            table = models.get(access.model_id)
            if not table or not set(access.columns) <= {c.name for c in table.columns}:
                raise HTTPException(422, "探索授权引用了不存在的表或字段")
            if not grant.unrestricted and access.model_id not in {
                r.model_id for r in grant.rows
            }:
                raise HTTPException(422, "每张探索表都必须限定行范围，或显式允许全部行")
        for row in grant.rows:
            table = models.get(row.model_id)
            column = (
                next((c for c in table.columns if c.name == row.column), None)
                if table
                else None
            )
            if column is None:
                raise HTTPException(422, "行级授权引用了不存在的模型或字段")
            if column.data_type.lower().find("timestamp") >= 0:
                raise HTTPException(422, "行级授权请使用组织/租户编码字段")
            for value in row.values:
                typed_value(value, column)
        if not grant.unrestricted and any(
            m.model_id not in {r.model_id for r in grant.rows}
            for m in definition.metrics
            if m.id in grant.metric_ids
        ):
            raise HTTPException(
                422, "每个授权指标的基础模型都必须限定行范围，或显式允许全部行"
            )
    if not policy:
        policy = QueryPolicy(topic_id=topic.id, release_id=release.id, grants=[])
    else:
        policy.revision += 1
    policy.release_id = release.id
    policy.grants = [g.model_dump(mode="json") for g in body.grants]
    policy.binding_digest = policy_binding(definition, tables, policy.grants)
    session.add(policy)
    event(
        session,
        topic.id,
        user.id,
        "policy_updated",
        detail=f"revision={policy.revision};members={len(body.grants)}",
    )
    session.commit()
    return policy_public(session, topic.id, user)


def submit(session: Session, user: User, body: QuerySubmission) -> QueryJob:
    gate(session)
    context, compiled = compile_for(session, body.topic_id, user, body.plan)
    topic, release, _, source, _, _, digest = context
    plan_hash = fingerprint(
        {"topic": str(topic.id), "plan": body.plan.model_dump(mode="json")}
    )
    previous = session.exec(
        select(QueryJob).where(
            QueryJob.actor_id == user.id, QueryJob.request_id == body.request_id
        )
    ).first()
    if previous:
        if (
            previous.plan_fingerprint != plan_hash
            or previous.policy_fingerprint != digest
            or previous.release_id != release.id
        ):
            raise HTTPException(409, "该请求标识已绑定其他计划或授权版本，请重新提交")
        return previous
    active = session.exec(
        select(QueryJob).where(col(QueryJob.status).in_(ACTIVE))
    ).all()
    if any(j.source_id == source.id and j.status == "cleanup_pending" for j in active):
        raise HTTPException(409, "此数据源有未确认结束的查询，暂不接受新任务")
    from app.modules.integration.service import scheduling_actor

    actor_owner = scheduling_actor(session, user.id)
    if (
        sum(scheduling_actor(session, j.actor_id) == actor_owner for j in active) >= 3
        or sum(j.source_id == source.id for j in active) >= 20
        or len(active) >= 100
    ):
        raise HTTPException(429, "查询队列已达到限额，请等待或取消已有任务")
    job = QueryJob(
        actor_id=user.id,
        request_id=body.request_id,
        topic_id=topic.id,
        source_id=source.id,
        release_id=release.id,
        semantic_version=release.version,
        policy_fingerprint=digest,
        plan_fingerprint=plan_hash,
        plan=body.plan.model_dump(mode="json"),
        sql_text=compiled.sql,
        expires_at=now() + timedelta(hours=24),
    )
    session.add(job)
    event(session, topic.id, user.id, "submitted", job.id)
    session.commit()
    session.refresh(job)
    return job


def owned(
    session: Session, job_id: uuid.UUID, user: User, *, result: bool = False
) -> QueryJob:
    job = session.get(QueryJob, job_id)
    if not job or job.actor_id != user.id:
        raise HTTPException(404, "查询任务不存在")
    if result:
        if utc(job.expires_at) <= now():
            raise HTTPException(410, "查询结果已过期，请重新查询")
        _, release, _, _, _, _, digest = resolve(session, job.topic_id, user)
        if release.id != job.release_id or digest != job.policy_fingerprint:
            raise HTTPException(403, "语义版本或权限已变更，请重新查询")
    return job


def recheck(session: Session, job: QueryJob) -> CompiledQuery:
    from app.modules.integration.worker import check_query_task

    check_query_task(session, job)
    user = session.get(User, job.actor_id)
    if not user:
        raise HTTPException(403, "查询用户已不存在")
    context, compiled = compile_for(session, job.topic_id, user, parse_plan(job.plan))
    if context[1].id != job.release_id or context[-1] != job.policy_fingerprint:
        raise HTTPException(403, "查询期间语义版本或权限已变化，结果不再交付")
    return compiled


def public(job: QueryJob, user: User) -> QueryJobPublic:
    return QueryJobPublic(
        **{k: getattr(job, k) for k in QueryJobPublic.model_fields if k != "sql"},
        sql=job.sql_text if user.is_superuser else None,
    )


def cancel(session: Session, job: QueryJob, user: User) -> QueryJob:
    gate(session)
    session.refresh(job)
    if job.status in ("queued", "running", "cancelling"):
        job.cancel_requested = True
        if job.status == "queued":
            job.status, job.message, job.finished_at = (
                "cancelled",
                "已取消，未连接源库",
                now(),
            )
        else:
            job.status, job.message = "cancelling", "正在请求源库停止，等待清理确认"
        session.add(job)
        event(session, job.topic_id, user.id, "cancel_requested", job.id)
        session.commit()
        session.refresh(job)
    return job
