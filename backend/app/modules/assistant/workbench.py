"""Authorized workbench snapshots, deterministic provenance and local feedback."""

import uuid

from fastapi import HTTPException
from sqlmodel import Session

from app.models import User
from app.modules.assistant import service
from app.modules.assistant.models import (
    AnswerEvidence,
    AssistantTurn,
    FeedbackInput,
    FeedbackPublic,
)
from app.modules.datasources.models import now
from app.modules.query import service as queries
from app.modules.query.models import QueryPlan, parse_plan


def turn_for(session, user, conversation_id, turn_id, *, lock=False):
    conversation, context = service.owned(session, conversation_id, user, lock=lock)
    turn = session.get(AssistantTurn, turn_id, populate_existing=True)
    if not turn or turn.conversation_id != conversation.id:
        raise HTTPException(404, "问答轮次不存在")
    return turn, context


def feedback(session, user, conversation_id, turn_id, body: FeedbackInput):
    queries.gate(session)
    turn, _ = turn_for(session, user, conversation_id, turn_id, lock=True)
    if turn.status in ("planning", "expired"):
        raise HTTPException(409, "请等待本轮完成后反馈")
    if body.rating == "incorrect" and body.category == "none":
        raise HTTPException(422, "请选择问题分类")
    record = FeedbackPublic(**body.model_dump(), updated_at=now())
    payload = service.unpack(turn)
    payload["feedback"] = record.model_dump(mode="json")
    service.pack(turn, payload)
    session.add(turn)
    from app.modules.quality.service import capture_feedback

    capture_feedback(session, user, turn, payload)
    session.commit()
    return record


def evidence(session, user, conversation_id, turn_id):
    turn, context = turn_for(session, user, conversation_id, turn_id)
    payload = service.unpack(turn)
    if not payload.get("plan"):
        raise HTTPException(409, "本轮尚无可核对的计划")
    plan = parse_plan(payload["plan"])
    _, compiled = queries.compile_for(session, context[0].id, user, plan)
    topic, release, definition, source, _, grant, _ = context
    sources = [
        f"{m.label}（{m.id}）"
        + (
            f" · {m.relation.schema_name}.{m.relation.name}"
            if user.is_superuser
            else ""
        )
        for m in definition.models
        if m.id in compiled.source_models
    ]
    chosen = [
        m
        for m in definition.metrics
        if isinstance(plan, QueryPlan) and m.id in plan.metrics
    ]
    filter_ids = {f for m in chosen for f in m.filter_ids}
    dimensions = {d.id: d.label for d in definition.dimensions}
    job = (
        queries.owned(session, turn.query_job_id, user, result=True)
        if turn.query_job_id
        else None
    )
    return AnswerEvidence(
        topic=topic.name,
        semantic_version=release.version,
        catalog_version=release.catalog_version,
        published_at=release.created_at,
        owner=definition.owner,
        timezone=definition.timezone,
        database_type=source.database_type,
        sources=sources,
        metrics=[f"{m.label}（{m.unit}）：{m.description}" for m in chosen],
        fixed_filters=[
            f"{f.label}：{dimensions[f.dimension_id]} {f.operator} {'、'.join(map(str, f.values))}"
            for f in definition.filters
            if f.id in filter_ids
        ],
        policy="管理员 · 全部授权数据"
        if grant is None
        else "成员 · 已应用字段与行范围授权",
        notes=[
            *compiled.notes,
            "业务数据更新时间尚未提供；查询完成时间不代表数据更新水位。",
        ],
        query_id=job.id if job else None,
        queried_at=job.finished_at if job else None,
        expires_at=job.expires_at if job else None,
    )


def snapshot(bind, actor_id: uuid.UUID, conversation_id: uuid.UUID):
    # Each stream tick owns a short session; no DB connection is held while waiting.
    with Session(bind) as session:
        user = session.get(User, actor_id)
        if not user or not user.is_active:
            raise HTTPException(403, "账号已不可用")
        service.purge(session)
        session.commit()
        conversation, _ = service.owned(session, conversation_id, user)
        data = service.public(session, conversation)
        jobs = [
            queries.public(queries.owned(session, t.query_job_id, user), user)
            for t in data.turns
            if t.query_job_id
        ]
        return {
            "conversation": data.model_dump(mode="json"),
            "jobs": [j.model_dump(mode="json") for j in jobs],
        }
