import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlmodel import col, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.modules.datasources.models import now
from app.modules.query import service
from app.modules.query.models import (
    PolicyPublic,
    PolicyUpdate,
    QueryEvent,
    QueryJob,
    QueryJobPublic,
    QueryPlan,
    QueryPreview,
    QueryResult,
    QuerySubmission,
)
from app.modules.semantic.models import PublishedTopic
from app.modules.semantic.service import public_catalog

router = APIRouter(prefix="/queries", tags=["queries"])
admin = [Depends(get_current_active_superuser)]


@router.get("/capabilities")
def capabilities(_current_user: CurrentUser) -> list[dict[str, str | bool]]:
    return [
        {
            "database": kind,
            "execution_enabled": kind != "dameng",
            "binding": binding,
            "cancellation": cancel,
        }
        for kind, binding, cancel in [
            ("postgresql", "命名参数", "cancel_safe + statement_timeout"),
            ("mysql", "驱动转义参数", "同账号 KILL QUERY + MAX_EXECUTION_TIME"),
            ("oracle", "命名参数", "Connection.cancel + call_timeout"),
            ("kingbase", "PG 模式命名参数", "cancel_safe + statement_timeout"),
            (
                "dameng",
                "位置参数（编译可预览）",
                "当前驱动未提供已验证的取消接口，执行暂未开放",
            ),
        ]
    ]


@router.get("/topics/{topic_id}/catalog")
def query_catalog(
    topic_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> PublishedTopic:
    context = service.resolve(session, topic_id, current_user)
    catalog = public_catalog(session, topic_id, current_user)
    grant = context[5]
    if grant:
        catalog.metrics = [m for m in catalog.metrics if m.id in grant.metric_ids]
        catalog.dimensions = [
            d for d in catalog.dimensions if d.id in grant.dimension_ids
        ]
        for metric in catalog.metrics:
            metric.allowed_dimensions = [
                d for d in metric.allowed_dimensions if d in grant.dimension_ids
            ]
    return catalog


@router.get("/topics/{topic_id}/policy", dependencies=admin)
def get_policy(
    topic_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> PolicyPublic:
    return service.policy_public(session, topic_id, current_user)


@router.put("/topics/{topic_id}/policy", dependencies=admin)
def save_policy(
    topic_id: uuid.UUID,
    body: PolicyUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> PolicyPublic:
    return service.save_policy(session, topic_id, current_user, body)


@router.post("/topics/{topic_id}/preview")
def preview(
    topic_id: uuid.UUID, body: QueryPlan, session: SessionDep, current_user: CurrentUser
) -> QueryPreview:
    return service.preview(session, topic_id, current_user, body)


@router.post("/", status_code=202)
def submit(
    body: QuerySubmission, session: SessionDep, current_user: CurrentUser
) -> QueryJobPublic:
    try:
        # Preview is available even where execution cannot yet meet its guarantees.
        context = service.resolve(session, body.topic_id, current_user)
        if context[3].database_type == "dameng":
            raise HTTPException(
                422, "达梦执行暂未开放：当前驱动缺少已验证的取消/语句限时能力"
            )
        job = service.submit(session, current_user, body)
        return service.public(job, current_user)
    except HTTPException as exc:
        session.rollback()
        service.event(
            session,
            body.topic_id,
            current_user.id,
            "submission_rejected",
            detail=f"http_status={exc.status_code}",
        )
        session.commit()
        raise


@router.get("/")
def list_jobs(
    session: SessionDep, current_user: CurrentUser, topic_id: uuid.UUID | None = None
) -> list[QueryJobPublic]:
    query = select(QueryJob).where(QueryJob.actor_id == current_user.id)
    if topic_id:
        query = query.where(QueryJob.topic_id == topic_id)
    return [
        service.public(j, current_user)
        for j in session.exec(
            query.order_by(col(QueryJob.created_at).desc()).limit(50)
        ).all()
    ]


@router.get("/audit", dependencies=admin)
def audit(
    session: SessionDep, limit: Annotated[int, Query(ge=1, le=200)] = 50
) -> list[QueryEvent]:
    return list(
        session.exec(
            select(QueryEvent).order_by(col(QueryEvent.created_at).desc()).limit(limit)
        ).all()
    )


@router.get("/cleanup", dependencies=admin)
def pending_cleanup(
    session: SessionDep, current_user: CurrentUser
) -> list[QueryJobPublic]:
    return [
        service.public(j, current_user)
        for j in session.exec(
            select(QueryJob).where(QueryJob.status == "cleanup_pending")
        ).all()
    ]


class CleanupConfirmation(BaseModel):
    note: str = Field(min_length=10, max_length=250)


@router.post("/{job_id}/confirm-cleanup", dependencies=admin)
def confirm_cleanup(
    job_id: uuid.UUID,
    body: CleanupConfirmation,
    session: SessionDep,
    current_user: CurrentUser,
) -> QueryJobPublic:
    service.gate(session)
    job = session.get(QueryJob, job_id)
    if not job or job.status != "cleanup_pending":
        raise HTTPException(409, "此任务无需清理确认")
    job.status, job.message, job.finished_at = (
        "failed",
        "管理员已确认源库清理结束",
        now(),
    )
    job.lease_token = None
    session.add(job)
    service.event(
        session, job.topic_id, current_user.id, "cleanup_confirmed", job.id, body.note
    )
    session.commit()
    session.refresh(job)
    return service.public(job, current_user)


@router.get("/{job_id}")
def get_job(
    job_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> QueryJobPublic:
    return service.public(service.owned(session, job_id, current_user), current_user)


@router.post("/{job_id}/cancel")
def cancel(
    job_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> QueryJobPublic:
    job = service.owned(session, job_id, current_user)
    return service.public(service.cancel(session, job, current_user), current_user)


@router.get("/{job_id}/result")
def result(
    job_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> QueryResult:
    job = service.owned(session, job_id, current_user, result=True)
    if job.status != "succeeded" or job.result is None:
        raise HTTPException(409, "此查询尚无可用结果")
    return QueryResult.model_validate(job.result)
