import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import col, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.api.routes.datasources import audit, get_source
from app.modules.catalog import introspection, service
from app.modules.catalog.models import (
    CatalogPublic,
    CatalogState,
    ObjectRef,
    ScopeUpdate,
    SyncJob,
    SyncJobPublic,
)

router = APIRouter(
    prefix="/catalog",
    tags=["catalog"],
    dependencies=[Depends(get_current_active_superuser)],
)


@router.get("/{source_id}/schemas")
def list_schemas(source_id: uuid.UUID, session: SessionDep) -> list[str]:
    config, password = service.source_config(get_source(session, source_id))
    session.rollback()
    try:
        return introspection.schemas(config, password)
    except Exception as exc:
        raise HTTPException(422, service.safe_error(exc)) from None


@router.get("/{source_id}/discover")
def discover_objects(
    source_id: uuid.UUID,
    schema_name: Annotated[str, Query(min_length=1, max_length=128)],
    session: SessionDep,
) -> list[ObjectRef]:
    config, password = service.source_config(get_source(session, source_id))
    session.rollback()
    try:
        return introspection.discover(config, password, schema_name)
    except Exception as exc:
        raise HTTPException(422, service.safe_error(exc)) from None


@router.get("/{source_id}")
def get_catalog(source_id: uuid.UUID, session: SessionDep) -> CatalogPublic:
    source = get_source(session, source_id)
    state = session.get(CatalogState, source_id)
    stale = state is not None and state.source_revision != source.revision
    return CatalogPublic(
        source_id=source_id,
        source_revision=source.revision,
        revision=state.revision if state else 0,
        scope=[ObjectRef.model_validate(r) for r in state.scope] if state else [],
        tables=service.visible_tables(state)
        if state and not stale and source.enabled
        else [],
        version=state.version if state else 0,
        synced_at=state.synced_at if state else None,
        needs_sync=not state or stale or state.revision != state.synced_scope_revision,
        needs_confirmation=bool(stale),
    )


@router.put("/{source_id}/scope")
def save_scope(
    source_id: uuid.UUID,
    body: ScopeUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> CatalogPublic:
    source = get_source(session, source_id, lock=True)
    if not source.enabled:
        raise HTTPException(409, "数据源已停用，请先启用")
    state = session.get(CatalogState, source_id)
    if (
        source.revision != body.expected_source_revision
        or (state.revision if state else 0) != body.expected_revision
    ):
        raise HTTPException(409, "配置或同步范围已更新，请刷新后重试")
    if state is None:
        state = CatalogState(
            source_id=source_id, source_revision=source.revision, scope=[]
        )
    else:
        state.revision += 1
        if state.source_revision != source.revision:
            state.snapshot = []
            state.synced_at = None
    state.source_revision = source.revision
    state.scope = [ref.model_dump() for ref in body.objects]
    session.add(state)
    audit(session, current_user.id, source_id, "catalog_scope_updated")
    session.commit()
    return get_catalog(source_id, session)


@router.post("/{source_id}/sync", status_code=202)
def sync_catalog(
    source_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> SyncJobPublic:
    source = get_source(session, source_id, lock=True)
    service.source_config(source)
    state = session.get(CatalogState, source_id)
    if not state or not state.scope:
        raise HTTPException(409, "请先选择并保存同步范围")
    if state.source_revision != source.revision:
        raise HTTPException(409, "连接配置已变化，请重新确认同步范围")
    service.expire_jobs(session)
    # Source lock serializes submissions; retries return the same active job.
    active = session.exec(
        select(SyncJob).where(
            SyncJob.source_id == source_id,
            col(SyncJob.status).in_(["queued", "running"]),
            SyncJob.source_revision == source.revision,
            SyncJob.scope_revision == state.revision,
        )
    ).first()
    if active:
        session.commit()
        return SyncJobPublic.model_validate(active)
    job = SyncJob(
        source_id=source_id,
        actor_id=current_user.id,
        source_revision=source.revision,
        scope_revision=state.revision,
    )
    session.add(job)
    audit(session, current_user.id, source_id, "catalog_sync_queued")
    session.commit()
    session.refresh(job)
    return SyncJobPublic.model_validate(job)


@router.get("/{source_id}/jobs")
def list_sync_jobs(source_id: uuid.UUID, session: SessionDep) -> list[SyncJobPublic]:
    get_source(session, source_id)
    service.expire_jobs(session)
    session.commit()
    return [
        SyncJobPublic.model_validate(job)
        for job in service.recent_jobs(session, source_id)
    ]
