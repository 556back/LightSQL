import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException
from sqlmodel import Session, col, select

from app.modules.catalog import introspection
from app.modules.catalog.models import (
    CatalogState,
    Change,
    ObjectRef,
    SyncJob,
    TableMeta,
)
from app.modules.datasources.models import (
    DataSource,
    DataSourceAudit,
    DataSourceInput,
    now,
)
from app.modules.datasources.service import decrypt_password

LEASE_SECONDS = 90


def source_config(source: DataSource) -> tuple[DataSourceInput, str]:
    if not source.enabled:
        raise HTTPException(409, "数据源已停用，请先启用")
    return DataSourceInput.model_validate(source), decrypt_password(
        source.encrypted_password
    )


def safe_error(exc: Exception) -> str:
    if isinstance(exc, introspection.CatalogReadError):
        return str(exc)[:300]
    if isinstance(exc, HTTPException) and isinstance(exc.detail, str):
        return exc.detail[:300]
    return "元数据读取失败，请检查连接、TLS、数据库授权及驱动；上次成功目录已保留"


def diff(before: list[dict], after: list[dict]) -> list[dict[str, Any]]:
    changes: list[Change] = []
    old = {(t["schema_name"], t["name"]): t for t in before}
    new = {(t["schema_name"], t["name"]): t for t in after}

    def encode(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)

    for key in sorted(old.keys() | new.keys()):
        path = ".".join(key)
        if key not in old or key not in new:
            changes.append(
                Change(
                    action="added" if key in new else "removed",
                    path=path,
                    detail="对象进入目录"
                    if key in new
                    else "对象移出目录（已删除、不可见或移出范围）",
                )
            )
            continue
        for field, label in (
            ("kind", "对象类型"),
            ("comment", "对象注释"),
            ("foreign_keys", "关联关系"),
            ("warnings", "元数据完整性提示"),
        ):
            if old[key].get(field) != new[key].get(field):
                changes.append(
                    Change(
                        action="changed",
                        path=path,
                        detail=label,
                        before=encode(old[key].get(field)),
                        after=encode(new[key].get(field)),
                    )
                )
        oc, nc = ({c["name"]: c for c in t["columns"]} for t in (old[key], new[key]))
        for name in sorted(oc.keys() | nc.keys()):
            if oc.get(name) == nc.get(name):
                continue
            action = (
                "added"
                if name not in oc
                else "removed"
                if name not in nc
                else "changed"
            )
            changes.append(
                Change(
                    action=action,
                    path=f"{path}.{name}",
                    detail="字段定义",
                    before=encode(oc[name]) if name in oc else None,
                    after=encode(nc[name]) if name in nc else None,
                )
            )
    return [c.model_dump() for c in changes]


def expire_jobs(session: Session) -> None:
    jobs = session.exec(
        select(SyncJob)
        .where(SyncJob.status == "running", col(SyncJob.lease_until) < now())
        .with_for_update(skip_locked=True)
    ).all()
    for job in jobs:
        job.status, job.message, job.finished_at = (
            "failed",
            "同步进程中断或超时，请重新同步；旧目录已保留",
            now(),
        )
        session.add(job)


def claim(engine: Any) -> tuple[uuid.UUID, uuid.UUID] | None:
    with Session(engine) as session:
        expire_jobs(session)
        job = session.exec(
            select(SyncJob)
            .where(SyncJob.status == "queued")
            .order_by(col(SyncJob.created_at))
            .with_for_update(skip_locked=True)
            .limit(1)
        ).first()
        if not job:
            session.commit()
            return None
        job.status, job.started_at = "running", now()
        job.message = "正在读取授权范围内的结构"
        job.lease_token, job.lease_until = (
            uuid.uuid4(),
            now() + timedelta(seconds=LEASE_SECONDS),
        )
        session.add(job)
        session.commit()
        return job.id, job.lease_token


def live_job(session: Session, job_id: uuid.UUID, token: uuid.UUID) -> SyncJob | None:
    job = session.exec(
        select(SyncJob).where(SyncJob.id == job_id).with_for_update()
    ).first()
    if (
        not job
        or job.status != "running"
        or job.lease_token != token
        or not job.lease_until
    ):
        return None
    deadline: datetime = job.lease_until
    if deadline.replace(tzinfo=UTC) <= now():
        return None
    return job


def run_job(engine: Any, job_id: uuid.UUID, token: uuid.UUID) -> None:
    def heartbeat() -> None:
        with Session(engine) as session:
            job = live_job(session, job_id, token)
            if not job:
                raise introspection.CatalogReadError("任务已失效")
            job.lease_until = now() + timedelta(seconds=LEASE_SECONDS)
            session.add(job)
            session.commit()

    snapshot = None
    error = ""
    try:
        with Session(engine) as session:
            job = session.get(SyncJob, job_id)
            if not job:
                return
            source = session.get(DataSource, job.source_id)
            state = session.get(CatalogState, job.source_id)
            if (
                not source
                or not state
                or source.revision != job.source_revision
                or state.revision != job.scope_revision
            ):
                raise introspection.CatalogReadError(
                    "数据源或同步范围已变化，请重新同步"
                )
            config, password = source_config(source)
            scope = [ObjectRef.model_validate(ref) for ref in state.scope]
        snapshot = [
            t.model_dump()
            for t in introspection.read_snapshot(config, password, scope, heartbeat)
        ]
    except Exception as exc:
        error = safe_error(exc)
    with Session(engine) as session:
        # Match the API's source -> state -> job lock order, without holding any
        # transaction open while contacting a remote database.
        row = session.get(SyncJob, job_id)
        if not row:
            return
        source = session.exec(
            select(DataSource).where(DataSource.id == row.source_id).with_for_update()
        ).first()
        state = session.exec(
            select(CatalogState)
            .where(CatalogState.source_id == row.source_id)
            .with_for_update()
        ).first()
        job = live_job(session, job_id, token)
        if not job:
            return  # Expired workers cannot publish late results.
        if (
            not source
            or not source.enabled
            or not state
            or source.revision != job.source_revision
            or state.revision != job.scope_revision
            or state.source_revision != source.revision
        ):
            job.status, job.message = (
                "superseded",
                "数据源或同步范围已变化，已丢弃旧任务结果",
            )
        elif snapshot is None:
            job.status, job.message = "failed", error
        else:
            job.changes = diff(state.snapshot, snapshot)
            state.snapshot = snapshot
            state.version += 1
            state.synced_at, state.synced_scope_revision = now(), state.revision
            job.status = "succeeded"
            job.message = f"同步完成：{len(snapshot)} 个对象，{len(job.changes)} 项变更"
            warning_count = sum(bool(t.get("warnings")) for t in snapshot)
            if warning_count:
                job.message += f"；{warning_count} 个对象存在元数据提示"
            job.table_count, job.version = len(snapshot), state.version
            session.add(state)
        job.finished_at, job.lease_until = now(), None
        session.add(job)
        session.add(
            DataSourceAudit(
                datasource_id=job.source_id,
                actor_id=job.actor_id,
                action=f"catalog_{job.status}",
                details={"job_id": str(job.id)},
            )
        )
        session.commit()


def visible_tables(state: CatalogState) -> list[TableMeta]:
    allowed = {(r["schema_name"], r["name"], r["kind"]) for r in state.scope}
    tables = [
        TableMeta.model_validate(t)
        for t in state.snapshot
        if (t["schema_name"], t["name"], t["kind"]) in allowed
    ]
    present = {(t.schema_name, t.name) for t in tables}
    for table in tables:
        table.foreign_keys = [
            fk
            for fk in table.foreign_keys
            if (fk.target_schema, fk.target_table) in present
        ]
    return tables


def recent_jobs(session: Session, source_id: uuid.UUID) -> list[SyncJob]:
    return list(
        session.exec(
            select(SyncJob)
            .where(SyncJob.source_id == source_id)
            .order_by(col(SyncJob.created_at).desc())
            .limit(20)
        ).all()
    )
