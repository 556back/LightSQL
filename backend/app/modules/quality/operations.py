"""Metadata-only monitoring; no query text, prompts or credentials in metrics."""

import shutil
import threading
import uuid
from contextlib import contextmanager
from datetime import timedelta

from sqlalchemy import func
from sqlmodel import Session, col, select

from app.core.config import settings
from app.modules.assistant.models import AssistantTurn
from app.modules.catalog.models import SyncJob
from app.modules.datasources.models import now
from app.modules.quality.models import BackupRecord, QualityFeedback, WorkerHeartbeat
from app.modules.quality.service import purge_feedback
from app.modules.query.models import QueryJob
from app.modules.query.service import utc


def beat(db, identity, kind):
    with Session(db) as session:
        record = session.get(WorkerHeartbeat, identity)
        if record is None:
            record = WorkerHeartbeat(id=identity, kind=kind)
        record.seen_at = now()
        session.add(record)
        if kind == "query":
            purge_feedback(session)
        session.commit()


@contextmanager
def heartbeat(db, kind):
    identity, stop = f"{kind}-{uuid.uuid4()}", threading.Event()

    def pulse():
        while not stop.is_set():
            try:
                beat(db, identity, kind)
            except Exception:
                pass  # Absent heartbeats become visible; never log connection secrets.
            stop.wait(10)

    worker = threading.Thread(target=pulse, daemon=True)
    worker.start()
    try:
        yield
    finally:
        stop.set()
        worker.join(timeout=2)


def overview(session):
    timestamp = now()
    cutoff = timestamp - timedelta(hours=24)
    purge_feedback(session)
    # Keep the heartbeat table bounded as worker instances are replaced.
    for record in session.exec(
        select(WorkerHeartbeat).where(
            WorkerHeartbeat.seen_at < timestamp - timedelta(days=7)
        )
    ).all():
        session.delete(record)
    session.commit()

    def counts(model, recent=False):
        query = select(model.status, func.count()).group_by(model.status)
        if recent:
            query = query.where(model.created_at >= cutoff)
        return dict(session.exec(query).all())

    heartbeats = {}
    for kind in ("catalog", "query"):
        last = session.exec(
            select(func.max(WorkerHeartbeat.seen_at)).where(
                WorkerHeartbeat.kind == kind
            )
        ).one()
        heartbeats[kind] = {
            "last_seen": last,
            "healthy": last is not None
            and (timestamp - utc(last)).total_seconds() < 35,
        }
    queues: dict[str, dict] = {}
    for name, model in (("query", QueryJob), ("catalog", SyncJob)):
        oldest = session.exec(
            select(func.min(model.created_at)).where(model.status == "queued")
        ).one()
        queues[name] = {
            "statuses": counts(model),
            "oldest_wait_seconds": round((timestamp - utc(oldest)).total_seconds())
            if oldest
            else 0,
        }
    prompt, completion, total = session.exec(
        select(
            func.coalesce(func.sum(AssistantTurn.prompt_tokens), 0),
            func.coalesce(func.sum(AssistantTurn.completion_tokens), 0),
            func.count(),
        ).where(AssistantTurn.created_at >= cutoff)
    ).one()
    backup = session.exec(
        select(BackupRecord).order_by(col(BackupRecord.created_at).desc()).limit(1)
    ).first()
    disk = shutil.disk_usage(".")
    recent = counts(QueryJob, True)
    alerts = []
    for kind, value in heartbeats.items():
        if not value["healthy"]:
            alerts.append(f"{kind} Worker 心跳缺失或超过 35 秒")
    for kind, queue in queues.items():
        if queue["oldest_wait_seconds"] > 60:
            alerts.append(f"{kind} 队列等待超过 60 秒")
    if queues["query"]["statuses"].get("cleanup_pending", 0):
        alerts.append("存在源库清理未确认的查询，请按运维手册处理")
    if not backup or (timestamp - utc(backup.created_at)).total_seconds() > 86400:
        alerts.append("没有 24 小时内的成功备份记录")
    if disk.free < 2 * 1024**3:
        alerts.append("应用所在磁盘可用空间不足 2 GiB")
    sources = [
        {
            "source_id": str(row[0]),
            "status": row[1],
            "count": row[2],
            "average_ms": round(row[3]) if row[3] is not None else None,
        }
        for row in session.exec(
            select(
                QueryJob.source_id,
                QueryJob.status,
                func.count(),
                func.avg(QueryJob.elapsed_ms),
            )
            .where(QueryJob.created_at >= cutoff)
            .group_by(col(QueryJob.source_id), col(QueryJob.status))
        ).all()
    ]
    return {
        "checked_at": timestamp,
        "window_hours": 24,
        "workers": heartbeats,
        "queues": queues,
        "query_capacity": {
            "global_limit": settings.QUERY_MAX_CONCURRENCY,
            "source_limit": settings.QUERY_SOURCE_MAX_CONCURRENCY,
            "actor_limit": 1,
            "queue_timeout_seconds": settings.QUERY_MAX_QUEUE_SECONDS,
            "occupied": sum(
                queues["query"]["statuses"].get(status, 0)
                for status in ("running", "cancelling", "cleanup_pending")
            ),
        },
        "queries": recent,
        "sources": sources,
        "model": {
            "turns": total,
            "statuses": counts(AssistantTurn, True),
            "prompt_tokens": prompt,
            "completion_tokens": completion,
        },
        "feedback": counts(QualityFeedback),
        "disk_free_bytes": disk.free,
        "backup": {
            "created_at": backup.created_at,
            "restored_at": backup.restored_at,
            "size_bytes": backup.size_bytes,
        }
        if backup
        else None,
        "alerts": alerts,
        "notes": [
            "心跳证明进程可访问元数据库；不代表业务源库健康。",
            "Token 统计仅含问答规划已记录的用量，不包含结果分析和连接测试，不能当作账单。",
            "备份时效来自成功记录，异地副本与密钥保管需运维核对。",
        ],
    }
