"""Durable integration orchestration; model calls with unknown outcomes are not retried."""

import asyncio
import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from fastapi import HTTPException
from sqlmodel import Session, col, or_, select

from app.core.db import engine
from app.modules.assistant import service as assistant
from app.modules.assistant.models import AskInput, AssistantTurn
from app.modules.datasources.models import now
from app.modules.integration import service as svc
from app.modules.integration.models import (
    AssertionUse,
    EmbedSession,
    EmbedTicket,
    IntegrationAudit,
    IntegrationTask,
)
from app.modules.query import service as queries
from app.modules.query.models import QueryJob, QueryPlan, QuerySubmission

logger = logging.getLogger(__name__)


def check_query_task(session, job):
    task = session.exec(
        select(IntegrationTask).where(
            or_(
                IntegrationTask.query_id == job.id,
                IntegrationTask.id == job.request_id,
                IntegrationTask.turn_id == job.request_id,
            )
        )
    ).first()
    if task:
        p = svc.principal(session, task.identity_id)
        svc.task_owned(session, p, task.id)
        if task.cancel_requested or task.status in ("cancelled", "failed", "expired"):
            svc.fail(403, "集成任务已取消或不可用")


def model_budget(session, p, task):
    queries.gate(session)
    count = len(
        session.exec(
            select(IntegrationAudit.id).where(
                IntegrationAudit.client_id == p.client.id,
                IntegrationAudit.action == "model_reserved",
                IntegrationAudit.created_at > now() - timedelta(days=1),
            )
        ).all()
    )
    if count >= p.client.config["model_calls_per_day"]:
        svc.fail(429, "应用模型调用日额度已用完")
    svc.audit(session, p.client.id, "model_reserved", p.identity.id, task.id)
    session.commit()


def claim(db):
    with Session(db) as session:
        queries.gate(session)
        tasks = session.exec(
            select(IntegrationTask).order_by(col(IntegrationTask.created_at))
        ).all()
        for task in tasks:
            if (
                task.lease_id
                and task.lease_until
                and queries.utc(task.lease_until) < now()
            ):
                if task.status in ("planning", "analyzing"):
                    if task.status == "analyzing" and task.query_id:
                        task.analysis_status, task.status = "failed", "succeeded"
                        task.message = "分析中断，已保留查询结果；模型调用不自动重试"
                    else:
                        task.status, task.message = (
                            "failed",
                            "规划中断，模型调用状态不明；未自动重试",
                        )
                task.lease_id, task.lease_until = None, None
                session.add(task)
            if queries.utc(task.expires_at) <= now() and task.status not in svc.ACTIVE:
                task.encrypted_input, task.encrypted_output = "", ""
                session.add(task)
            if (
                queries.utc(task.created_at) < now() - timedelta(days=90)
                and task.status not in svc.ACTIVE
            ):
                session.delete(task)
        for model, predicate in [
            (EmbedTicket, EmbedTicket.expires_at < now()),
            (AssertionUse, AssertionUse.expires_at < now()),
            (
                IntegrationAudit,
                IntegrationAudit.created_at < now() - timedelta(days=90),
            ),
        ]:
            for record in session.exec(select(model).where(predicate)).all():
                session.delete(record)
        # Keep session revocation tombstones as long as the related task summaries.
        for record in session.exec(
            select(EmbedSession).where(
                EmbedSession.expires_at < now() - timedelta(days=90)
            )
        ).all():
            session.delete(record)
        active = [
            t
            for t in tasks
            if t.lease_id and t.lease_until and queries.utc(t.lease_until) > now()
        ]
        from app.modules.integration.models import IntegrationIdentity

        owners = {
            i.id: i.user_id for i in session.exec(select(IntegrationIdentity)).all()
        }
        candidate = next(
            (
                t
                for t in tasks
                if t.status in svc.ACTIVE
                and not t.lease_id
                and (not t.lease_until or queries.utc(t.lease_until) <= now())
                and not any(
                    owners.get(a.identity_id, a.identity_id)
                    == owners.get(t.identity_id, t.identity_id)
                    for a in active
                )
            ),
            None,
        )
        if len(active) >= 4 or not candidate:
            session.commit()
            return None
        candidate.lease_id = uuid.uuid4()
        candidate.lease_until = now() + timedelta(minutes=3)
        session.add(candidate)
        session.commit()
        return candidate.id, candidate.lease_id


def save(session, task, status, message):
    task.status, task.message = status, message
    session.add(task)
    session.commit()


def fresh(session, task_id, lease_id):
    session.expire_all()
    task = session.get(IntegrationTask, task_id)
    if not task or task.lease_id != lease_id:
        svc.fail(409, "任务租约已失效")
    p = svc.principal(session, task.identity_id)
    svc.task_owned(session, p, task.id)
    return task, p


async def advance(db, task_id, lease_id):
    with Session(db) as session:
        try:
            task, p = fresh(session, task_id, lease_id)
            data = svc.unseal(task.encrypted_input)
            if task.cancel_requested:
                if task.query_id:
                    job = session.get(QueryJob, task.query_id)
                    if job and job.status in queries.ACTIVE:
                        job = queries.cancel(session, job, p.actor)
                        save(
                            session,
                            task,
                            job.status
                            if job.status in ("cancelling", "cleanup_pending")
                            else "cancelled",
                            job.message,
                        )
                        return
                save(session, task, "cancelled", "任务已取消")
                return
            if queries.utc(task.expires_at) <= now() or now() - queries.utc(
                task.created_at
            ) > timedelta(minutes=5):
                if task.query_id:
                    job = session.get(QueryJob, task.query_id)
                    if job and job.status in queries.ACTIVE:
                        task.cancel_requested = True
                        session.add(task)
                        queries.cancel(session, job, p.actor)
                        save(session, task, "cancelling", "任务达到总时限，正在取消")
                        return
                save(session, task, "expired", "任务已超过处理期限")
                return
            if task.operation == "analysis" and not task.query_id:
                parent = svc.task_owned(session, p, task.parent_id)
                svc.result(session, p, parent)
                task.query_id = parent.query_id
                task.encrypted_output = parent.encrypted_output
                session.add(task)
                session.commit()
            if task.operation == "query" and not task.query_id:
                # Existing query submission is idempotent using this task UUID.
                job = queries.submit(
                    session,
                    p.actor,
                    QuerySubmission(
                        topic_id=task.topic_id,
                        request_id=task.id,
                        plan=QueryPlan.model_validate(data["plan"]),
                    ),
                )
                task.query_id = job.id
                save(session, task, "querying", "已提交查询")
                return
            if task.operation == "answer" and not task.query_id:
                if not task.conversation_id:
                    # Persist a deterministic conversation and task association in
                    # one transaction; assistant.create commits internally.
                    from app.modules.assistant.models import Conversation

                    context = queries.resolve(session, task.topic_id, p.actor)
                    conversation = Conversation(
                        id=task.id,
                        actor_id=p.actor.id,
                        topic_id=task.topic_id,
                        release_id=context[1].id,
                        policy_fingerprint=context[6],
                        expires_at=task.expires_at,
                    )
                    session.add(conversation)
                    task.conversation_id = conversation.id
                    session.add(task)
                    session.commit()
                if not task.turn_id:
                    save(session, task, "planning", "正在生成并校验查询计划")
                    model_budget(session, p, task)
                    response = await assistant.ask(
                        session,
                        p.actor,
                        task.conversation_id,
                        AskInput(
                            request_id=task.id,
                            expected_revision=data["expected_revision"],
                            question=data["question"],
                            mode=data["mode"],
                            entity_choices=data.get("entity_choices", {}),
                        ),
                    )
                    task, p = fresh(session, task_id, lease_id)
                    if task.cancel_requested:
                        save(session, task, "cancelled", "已取消，未提交数据库查询")
                        return
                    turns = session.exec(
                        select(AssistantTurn).where(
                            AssistantTurn.conversation_id == task.conversation_id,
                            AssistantTurn.request_id == task.id,
                        )
                    ).all()
                    if not turns:
                        svc.fail(409, "未生成有效轮次")
                    turn = turns[0]
                    task.turn_id = turn.id
                    public_turn = next(t for t in response.turns if t.id == turn.id)
                    task.encrypted_output = svc.seal(
                        {
                            "chart": public_turn.chart,
                            "clarification": {
                                "message": public_turn.message,
                                "ambiguities": [
                                    a.model_dump(mode="json")
                                    for a in public_turn.ambiguities
                                ],
                            }
                            if turn.status == "clarification"
                            else None,
                        }
                    )
                    if turn.status != "ready":
                        save(
                            session,
                            task,
                            "needs_clarification"
                            if turn.status == "clarification"
                            else "failed",
                            public_turn.message,
                        )
                        return
                    save(session, task, "querying", "计划已校验，准备查询")
                # Check cancellation again while holding the shared admission lock.
                queries.gate(session)
                task, p = fresh(session, task_id, lease_id)
                if task.cancel_requested:
                    save(session, task, "cancelled", "已取消，未提交数据库查询")
                    return
                job = assistant.execute(
                    session, p.actor, task.conversation_id, task.turn_id
                )
                task.query_id = job.id
                save(session, task, "querying", "已提交查询")
                return
            job = session.get(QueryJob, task.query_id)
            if not job:
                svc.fail(404, "底层查询已不存在")
            if job.status in queries.ACTIVE:
                save(
                    session,
                    task,
                    job.status
                    if job.status in ("cancelling", "cleanup_pending")
                    else "querying",
                    job.message,
                )
                return
            if job.status != "succeeded":
                save(
                    session,
                    task,
                    "cancelled"
                    if job.status == "cancelled"
                    else "expired"
                    if job.status == "expired"
                    else "failed",
                    job.message,
                )
                return
            queries.owned(session, job.id, p.actor, result=True)
            output = svc.unseal(task.encrypted_output)
            if task.conversation_id and task.turn_id:
                from app.modules.assistant.workbench import evidence

                output["evidence"] = evidence(
                    session, p.actor, task.conversation_id, task.turn_id
                ).model_dump(mode="json")
            else:
                context = queries.resolve(session, task.topic_id, p.actor)
                output["evidence"] = {
                    "topic": context[0].name,
                    "semantic_version": job.semantic_version,
                    "timezone": context[2].timezone,
                    "notes": ["业务数据更新水位未知"],
                    "queried_at": job.finished_at.isoformat()
                    if job.finished_at
                    else None,
                }
            task.encrypted_output = svc.seal(output)
            if (
                data.get("include_analysis") or task.operation == "analysis"
            ) and task.analysis_status == "not_requested":
                from app.modules.assistant.analysis import summarize_result

                task.analysis_status = "running"
                save(session, task, "analyzing", "正在分析返回结果")
                try:
                    model_budget(session, p, task)
                    analysis = await summarize_result(session, job.result)
                    task, p = fresh(session, task_id, lease_id)
                    queries.owned(session, job.id, p.actor, result=True)
                    if task.cancel_requested:
                        save(
                            session, task, "cancelled", "已取消后续分析，未交付迟到内容"
                        )
                        return
                    output["analysis"] = analysis.model_dump(mode="json")
                    task.analysis_status = "succeeded"
                except HTTPException:
                    task, p = fresh(session, task_id, lease_id)
                    task.analysis_status = "failed"
                task.encrypted_output = svc.seal(output)
            save(
                session,
                task,
                "succeeded",
                "查询完成；分析未完成"
                if task.analysis_status == "failed"
                else "已完成",
            )
            svc.audit(session, task.client_id, "succeeded", task.identity_id, task.id)
            session.commit()
        except Exception as exc:
            session.rollback()
            task = session.get(IntegrationTask, task_id, populate_existing=True)
            if task and task.lease_id == lease_id:
                task.message = "任务执行失败或授权已变化，请检查配置后重新提交"
                if isinstance(exc, HTTPException) and exc.status_code == 429:
                    task.message = "调用或模型额度已达上限，请稍后使用新请求重试"
                task.status = "failed"
                # Cancellation is allowed even after authorization was revoked.
                if task.query_id:
                    job = session.get(QueryJob, task.query_id)
                    if job and job.status in queries.ACTIVE:
                        job.cancel_requested = True
                        if job.status == "queued":
                            job.status, job.message = (
                                "cancelled",
                                "集成授权失效，查询取消",
                            )
                        elif job.status == "running":
                            job.status = "cancelling"
                        session.add(job)
                        task.status = (
                            "cleanup_pending"
                            if job.status == "cleanup_pending"
                            else "cancelling"
                            if job.status == "cancelling"
                            else "failed"
                        )
                        task.cancel_requested = True
                session.add(task)
                svc.audit(session, task.client_id, "failed", task.identity_id, task.id)
                session.commit()
                logger.warning(
                    "Integration task %s failed (%s)", task_id, type(exc).__name__
                )
        finally:
            session.rollback()
            task = session.get(IntegrationTask, task_id, populate_existing=True)
            if task and task.lease_id == lease_id:
                task.lease_id = None
                task.lease_until = now() + timedelta(seconds=2)
                session.add(task)
                session.commit()


def main():
    from app.modules.quality.operations import heartbeat

    with heartbeat(engine, "integration"):
        run_loop()


def run_loop():
    logging.basicConfig(level=logging.INFO)
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = set()
        while True:
            for future in list(futures):
                if future.done():
                    future.result()
                    futures.remove(future)
            if len(futures) < 4:
                work = claim(engine)
                if work:
                    futures.add(pool.submit(asyncio.run, advance(engine, *work)))
            time.sleep(1)


if __name__ == "__main__":
    main()
