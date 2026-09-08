"""Persistent query queue. Each execution uses a bounded disposable child process."""

import json
import logging
import multiprocessing
import time
import uuid
from collections import Counter
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import timedelta
from typing import Any

from fastapi import HTTPException
from sqlalchemy.engine import Engine
from sqlmodel import Session, col, select

from app.core.config import settings
from app.core.db import engine
from app.modules.datasources.models import DataSource, DataSourceInput, now
from app.modules.datasources.service import decrypt_password
from app.modules.query.executor import child_execute
from app.modules.query.models import QueryEvent, QueryJob
from app.modules.query.service import event, gate, recheck, utc

logger = logging.getLogger(__name__)


def claim(
    db: Engine, *, allow_claim: bool = True
) -> tuple[uuid.UUID, uuid.UUID] | None:
    with Session(db) as session:
        gate(session)
        from app.modules.assistant.service import purge

        purge(session)
        jobs = session.exec(select(QueryJob).order_by(col(QueryJob.created_at))).all()
        for job in jobs:
            if (
                job.status in ("running", "cancelling")
                and job.lease_until
                and utc(job.lease_until) < now()
            ):
                job.status, job.message = (
                    "cleanup_pending",
                    "执行进程租约已过期，等待源库清理确认；任务不会自动重试",
                )
                session.add(job)
                event(session, job.topic_id, job.actor_id, "lease_expired", job.id)
            if (
                job.status == "queued"
                and (now() - utc(job.created_at)).total_seconds()
                >= settings.QUERY_MAX_QUEUE_SECONDS
            ):
                job.status, job.message, job.finished_at = (
                    "expired",
                    "排队超过时间限制，请稍后重新提交",
                    now(),
                )
                session.add(job)
                event(session, job.topic_id, job.actor_id, "queue_expired", job.id)
            if utc(job.expires_at) < now() and job.status not in (
                "running",
                "cancelling",
                "cleanup_pending",
            ):
                job.result, job.plan, job.sql_text = None, {}, ""
                if job.status == "queued":
                    job.status, job.message, job.finished_at = (
                        "expired",
                        "排队任务已过期",
                        now(),
                    )
                session.add(job)
            if utc(job.created_at) < now() - timedelta(days=90) and job.status not in (
                "running",
                "cancelling",
                "cleanup_pending",
            ):
                session.delete(job)
        for record in session.exec(
            select(QueryEvent).where(QueryEvent.created_at < now() - timedelta(days=90))
        ).all():
            session.delete(record)
        # The singleton row lock makes these limits shared across all workers.
        # Unconfirmed source cleanup also consumes a global and actor slot.
        blocked = {j.source_id for j in jobs if j.status == "cleanup_pending"}
        active = [
            j for j in jobs if j.status in ("running", "cancelling", "cleanup_pending")
        ]
        source_counts = Counter(j.source_id for j in active)
        from app.modules.integration.service import scheduling_actor

        owners = {j.actor_id: scheduling_actor(session, j.actor_id) for j in jobs}
        actors = {owners[j.actor_id] for j in active}
        if not allow_claim or len(active) >= settings.QUERY_MAX_CONCURRENCY:
            session.commit()
            return None
        job = next(
            (
                j
                for j in jobs
                if j.status == "queued"
                and j.source_id not in blocked
                and owners[j.actor_id] not in actors
                and source_counts[j.source_id] < settings.QUERY_SOURCE_MAX_CONCURRENCY
            ),
            None,
        )
        if not job:
            session.commit()
            return None
        token = uuid.uuid4()
        job.status, job.message = "running", "正在验证授权并执行查询"
        job.lease_token, job.lease_until, job.started_at = (
            token,
            now() + timedelta(seconds=60),
            now(),
        )
        session.add(job)
        event(session, job.topic_id, job.actor_id, "started", job.id)
        session.commit()
        return job.id, token


def run_job(db: Engine, job_id: uuid.UUID, token: uuid.UUID) -> None:
    ctx = multiprocessing.get_context("spawn")
    stop = ctx.Event()
    process = None
    outcome: dict[str, Any] = {
        "status": "failed",
        "message": "查询启动失败",
        "cleaned": True,
    }
    started = time.monotonic()
    timings: dict[str, int] = {}
    spawn_started = None
    try:
        with Session(db) as session:
            job = session.get(QueryJob, job_id)
            if (
                not job
                or job.lease_token != token
                or job.status not in ("running", "cancelling")
            ):
                return  # noqa: B012 - a newer lease/cleanup decision owns this job
            if job.cancel_requested:
                outcome = {
                    "status": "cancelled",
                    "message": "已取消，未连接源库",
                    "cleaned": True,
                }
            else:
                compiled = recheck(session, job)
                # A stable, non-secret handle for DBA source-session inspection.
                # The same marker survives a worker crash in the persisted SQL.
                compiled.sql = f"/* lightsql_job:{job.id} */ " + compiled.sql
                job.sql_text = compiled.sql
                session.add(job)
                session.commit()
                source = session.get(DataSource, job.source_id)
                assert source is not None
                source_input = DataSourceInput.model_validate(source).model_dump()
                password = decrypt_password(source.encrypted_password)
                plan = job.plan
                receive, send = ctx.Pipe(duplex=False)
                process = ctx.Process(
                    target=child_execute,
                    args=(source_input, password, compiled, plan, stop, send),
                    daemon=True,
                )
                spawn_started = time.monotonic()
                timings["prepare_ms"] = round((spawn_started - started) * 1000)
                process.start()
                timings["spawn_call_ms"] = round(
                    (time.monotonic() - spawn_started) * 1000
                )
                send.close()
        if process:
            deadline = time.monotonic() + plan["timeout_seconds"]
            while process.is_alive() and not receive.poll(0.15):
                with Session(db) as session:
                    job = session.get(QueryJob, job_id)
                    if (
                        not job
                        or job.lease_token != token
                        or job.status not in ("running", "cancelling")
                    ):
                        stop.set()
                    else:
                        if job.cancel_requested:
                            stop.set()
                        try:
                            recheck(session, job)
                        except HTTPException:
                            stop.set()
                        job.lease_until = now() + timedelta(seconds=60)
                        session.add(job)
                        session.commit()
                if time.monotonic() >= deadline:
                    stop.set()
                if time.monotonic() >= deadline + 12:
                    break
            if receive.poll(0.5):
                outcome = receive.recv()
                entered_at = outcome.pop("_child_entered_at", None)
                if entered_at is not None and spawn_started is not None:
                    timings["child_startup_ms"] = max(
                        0, round((entered_at - spawn_started) * 1000)
                    )
                if "elapsed_ms" in outcome:
                    timings["child_execution_ms"] = outcome["elapsed_ms"]
            else:
                outcome = {
                    "status": "cleanup_pending",
                    "message": "执行进程未能确认清理完成，已暂停该源的新查询",
                    "cleaned": False,
                }
            receive.close()
            if time.monotonic() >= deadline and outcome.get("cleaned"):
                outcome.update(
                    status="timed_out", message="查询超过执行时间限制，源库操作已结束"
                )
                outcome.pop("result", None)
    except HTTPException:
        outcome = {
            "status": "rejected",
            "message": "语义版本、目录或授权已变化，请重新查询",
            "cleaned": True,
        }
    except Exception:
        outcome = {
            "status": "cleanup_pending" if process else "failed",
            "message": "执行异常，请管理员检查任务记录",
            "cleaned": process is None,
        }
    finally:
        if process:
            process.join(timeout=1)
            if process.is_alive():
                process.terminate()
                process.join(timeout=2)
    with Session(db) as session:
        gate(session)
        job = session.get(QueryJob, job_id)
        if (
            not job
            or job.lease_token != token
            or job.status not in ("running", "cancelling", "cleanup_pending")
        ):
            return
        if outcome["status"] == "succeeded":
            try:
                recheck(session, job)
            except HTTPException:
                outcome.update(
                    status="rejected",
                    message="查询期间授权或语义版本已变化，结果已丢弃",
                )
                outcome.pop("result", None)
        if job.cancel_requested and outcome.get("cleaned"):
            outcome.update(status="cancelled", message="查询已取消，源库操作已结束")
            outcome.pop("result", None)
        job.status, job.message = outcome["status"], outcome["message"]
        job.result = outcome.get("result")
        job.row_count = outcome.get("row_count", 0) if job.result else 0
        job.result_bytes = outcome.get("result_bytes", 0) if job.result else 0
        job.truncated = outcome.get("truncated", False) if job.result else False
        job.elapsed_ms = round((time.monotonic() - started) * 1000)
        timings["worker_ms"] = job.elapsed_ms
        job.finished_at = now() if outcome.get("cleaned") else None
        job.lease_until = None
        session.add(job)
        event(
            session,
            job.topic_id,
            job.actor_id,
            job.status,
            job.id,
            json.dumps(timings, separators=(",", ":")),
        )
        session.commit()


def run_loop(db: Engine = engine, stop=None) -> None:
    logging.basicConfig(level=logging.INFO)
    logger.info("Query worker started")
    with ThreadPoolExecutor(max_workers=settings.QUERY_MAX_CONCURRENCY) as pool:
        pending: set[Future] = set()
        while stop is None or not stop.is_set():
            try:
                for future in list(pending):
                    if future.done():
                        pending.remove(future)
                        future.result()
                # Keep sweeping expired leases and queued jobs even when full.
                # claim() enforces shared capacity; never build an executor backlog.
                job = claim(
                    db, allow_claim=len(pending) < settings.QUERY_MAX_CONCURRENCY
                )
                if job:
                    pending.add(pool.submit(run_job, db, *job))
                    continue
                if stop is None:
                    time.sleep(0.2)
                else:
                    stop.wait(0.2)
            except KeyboardInterrupt:
                return  # The pool drains bounded executions before exiting.
            except Exception:
                logger.error("Query worker cycle failed; retrying in five seconds")
                if stop is None:
                    time.sleep(5)
                else:
                    stop.wait(5)


def main() -> None:
    from app.modules.quality.operations import heartbeat

    with heartbeat(engine, "query"):
        run_loop()


if __name__ == "__main__":
    main()
