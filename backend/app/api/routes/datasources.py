import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import col, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import Message
from app.modules.datasources import service
from app.modules.datasources.models import (
    ConnectionTestResult,
    DataSource,
    DataSourceAudit,
    DataSourceCreate,
    DataSourceInput,
    DataSourcePublic,
    DataSourcesPublic,
    DataSourceUpdate,
    now,
)

router = APIRouter(
    prefix="/datasources",
    tags=["datasources"],
    dependencies=[Depends(get_current_active_superuser)],
)


def get_source(
    session: SessionDep, source_id: uuid.UUID, *, lock: bool = False
) -> DataSource:
    query = select(DataSource).where(DataSource.id == source_id)
    if lock:
        query = query.with_for_update()
    source = session.exec(query).first()
    if not source:
        raise HTTPException(404, "数据源不存在")
    return source


def audit(
    session: SessionDep, actor_id: uuid.UUID, source_id: uuid.UUID, action: str
) -> None:
    session.add(
        DataSourceAudit(actor_id=actor_id, datasource_id=source_id, action=action)
    )


def commit(session: SessionDep) -> None:
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "数据源名称已存在，请使用其他名称") from None


@router.get("/")
def list_datasources(session: SessionDep) -> DataSourcesPublic:
    sources = session.exec(
        select(DataSource).order_by(col(DataSource.created_at).desc())
    ).all()
    return DataSourcesPublic(
        data=[DataSourcePublic.model_validate(s) for s in sources], count=len(sources)
    )


@router.post("/", status_code=201)
def create_datasource(
    body: DataSourceCreate, session: SessionDep, current_user: CurrentUser
) -> DataSourcePublic:
    service.check_host(body.host)
    source = DataSource(
        **body.model_dump(exclude={"password"}),
        name_key=body.name.casefold(),
        encrypted_password=service.encrypt_password(body.password.get_secret_value()),
    )
    session.add(source)
    audit(session, current_user.id, source.id, "created")
    commit(session)
    session.refresh(source)
    return DataSourcePublic.model_validate(source)


@router.post("/test")
def test_draft(body: DataSourceCreate) -> ConnectionTestResult:
    return service.probe(body, body.password.get_secret_value())


@router.put("/{source_id}")
def update_datasource(
    source_id: uuid.UUID,
    body: DataSourceUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> DataSourcePublic:
    service.check_host(body.host)
    source = get_source(session, source_id, lock=True)
    if source.revision != body.expected_revision:
        raise HTTPException(409, "配置已被更新，请刷新后重试")
    changes = body.model_dump(exclude={"password", "expected_revision"})
    connection_fields = (
        "database_type",
        "host",
        "port",
        "database",
        "username",
        "tls_mode",
    )
    changed = body.password is not None or any(
        getattr(source, key) != changes[key] for key in connection_fields
    )
    source.sqlmodel_update(changes)
    source.name_key = source.name.casefold()
    if body.password is not None:
        source.encrypted_password = service.encrypt_password(
            body.password.get_secret_value()
        )
    if changed:
        source.status, source.last_error, source.latency_ms, source.last_tested_at = (
            "untested",
            None,
            None,
            None,
        )
    source.revision += 1
    source.updated_at = now()
    audit(session, current_user.id, source.id, "updated")
    session.add(source)
    commit(session)
    session.refresh(source)
    return DataSourcePublic.model_validate(source)


@router.post("/{source_id}/test")
def test_datasource(
    source_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> ConnectionTestResult:
    source = get_source(session, source_id)
    if not source.enabled:
        raise HTTPException(409, "请先启用数据源再测试连接")
    revision = source.revision
    config = DataSourceInput.model_validate(source)
    password = service.decrypt_password(source.encrypted_password)
    session.rollback()  # Release the transaction before waiting on a remote connection.
    result = service.probe(config, password)
    session.expire_all()
    source = get_source(session, source_id, lock=True)
    if source.revision != revision or not source.enabled:
        raise HTTPException(409, "测试期间配置已变化，请重新测试")
    source.status = "connected" if result.success else "error"
    source.last_tested_at, source.latency_ms = result.tested_at, result.latency_ms
    source.last_error = None if result.success else result.message
    audit(
        session,
        current_user.id,
        source.id,
        "test_succeeded" if result.success else "test_failed",
    )
    session.add(source)
    commit(session)
    return result


@router.delete("/{source_id}")
def delete_datasource(
    source_id: uuid.UUID,
    expected_revision: Annotated[int, Query(ge=1)],
    session: SessionDep,
    current_user: CurrentUser,
) -> Message:
    from app.modules.semantic.models import Topic

    source = get_source(session, source_id, lock=True)
    if source.revision != expected_revision:
        raise HTTPException(409, "配置已变化，请刷新后重试")
    if session.exec(
        select(Topic.id).where(Topic.source_id == source.id).limit(1)
    ).first():
        raise HTTPException(
            409, "数据源仍被业务主题引用；请先移除未发布主题，已发布主题的历史需保留"
        )
    audit(session, current_user.id, source.id, "deleted")
    session.delete(source)
    commit(session)
    return Message(message="数据源已删除")
