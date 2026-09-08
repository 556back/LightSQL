import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import col, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import Message, User
from app.modules.catalog.models import CatalogState
from app.modules.datasources.models import DataSource
from app.modules.semantic import service
from app.modules.semantic.models import (
    DraftUpdate,
    ExportPublic,
    ImportRequest,
    MembersUpdate,
    PublishedTopic,
    PublishRequest,
    ReleasePublic,
    RevisionRequest,
    SemanticDefinition,
    SemanticRelease,
    Topic,
    TopicCreate,
    TopicDetail,
    TopicMember,
    TopicSummary,
    ValidationReport,
)

router = APIRouter(prefix="/topics", tags=["topics"])
admin = [Depends(get_current_active_superuser)]


@router.get("/")
def list_topics(session: SessionDep, current_user: CurrentUser) -> list[TopicSummary]:
    return [
        service.summary(session, t, admin=current_user.is_superuser)
        for t in service.all_topics(session, current_user)
    ]


@router.post("/", status_code=201, dependencies=admin)
def create_topic(
    body: TopicCreate, session: SessionDep, current_user: CurrentUser
) -> TopicDetail:
    source = session.exec(
        select(DataSource).where(DataSource.id == body.source_id).with_for_update()
    ).first()
    if not source or not source.enabled:
        raise HTTPException(409, "请先选择一个启用的数据源")
    topic = Topic(
        name=body.name,
        name_key=body.name.casefold(),
        description=body.description,
        source_id=body.source_id,
        draft=SemanticDefinition(owner=body.owner).model_dump(mode="json"),
    )
    session.add(topic)
    service.audit(session, topic, current_user, "created")
    service.commit(session)
    session.refresh(topic)
    return service.detail(session, topic)


@router.get("/{topic_id}", dependencies=admin)
def get_topic(topic_id: uuid.UUID, session: SessionDep) -> TopicDetail:
    return service.detail(session, service.get_topic(session, topic_id))


@router.put("/{topic_id}/draft", dependencies=admin)
def save_draft(
    topic_id: uuid.UUID,
    body: DraftUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> TopicDetail:
    topic = service.get_topic(session, topic_id, lock=True)
    service.expected(topic, body.expected_revision)
    topic.name, topic.name_key, topic.description, topic.enabled = (
        body.name,
        body.name.casefold(),
        body.description,
        body.enabled,
    )
    topic.draft = body.definition.model_dump(mode="json")
    service.changed(session, topic, current_user, "draft_saved")
    return service.detail(session, topic)


@router.post("/{topic_id}/validate", dependencies=admin)
def validate_draft(
    topic_id: uuid.UUID, body: RevisionRequest, session: SessionDep
) -> ValidationReport:
    topic = service.get_topic(session, topic_id)
    service.expected(topic, body.expected_revision)
    return service.report(session, topic)


@router.post("/{topic_id}/releases", status_code=201, dependencies=admin)
def publish_topic(
    topic_id: uuid.UUID,
    body: PublishRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> ReleasePublic:
    topic = service.get_topic(session, topic_id)
    source_id = topic.source_id
    # Catalog synchronization uses source -> state locks. Keep this ordering.
    session.exec(
        select(DataSource).where(DataSource.id == source_id).with_for_update()
    ).first()
    session.exec(
        select(CatalogState)
        .where(CatalogState.source_id == source_id)
        .with_for_update()
    ).first()
    session.expire_all()
    topic = service.get_topic(session, topic_id, lock=True)
    service.expected(topic, body.expected_revision)
    if not topic.enabled:
        raise HTTPException(409, "请先启用主题再发布")
    checked = service.report(session, topic)
    if not checked.valid:
        raise HTTPException(
            422,
            {
                "message": "发布校验未通过",
                "issues": [i.model_dump() for i in checked.issues],
            },
        )
    state = session.get(CatalogState, source_id)
    assert state is not None
    previous = service.release_for(session, topic)
    changes = service.definition_diff(
        previous.definition if previous else {}, topic.draft
    )
    release = SemanticRelease(
        topic_id=topic.id,
        version=topic.current_version + 1,
        definition=topic.draft,
        catalog_version=state.version,
        source_revision=state.source_revision,
        scope_revision=state.revision,
        binding_digest=checked.binding_digest,
        published_by=current_user.id,
        note=body.note,
    )
    session.add(release)
    topic.current_version = release.version
    service.changed(session, topic, current_user, "published")
    session.refresh(release)
    return ReleasePublic(
        id=release.id,
        version=release.version,
        note=release.note,
        catalog_version=release.catalog_version,
        created_at=release.created_at,
        metric_count=len(release.definition["metrics"]),
        dimension_count=len(release.definition["dimensions"]),
        changes=changes,
    )


@router.get("/{topic_id}/releases", dependencies=admin)
def list_releases(topic_id: uuid.UUID, session: SessionDep) -> list[ReleasePublic]:
    service.get_topic(session, topic_id)
    releases = session.exec(
        select(SemanticRelease)
        .where(SemanticRelease.topic_id == topic_id)
        .order_by(col(SemanticRelease.version))
    ).all()
    result = []
    previous = {}
    for r in releases:
        result.append(
            ReleasePublic(
                id=r.id,
                version=r.version,
                note=r.note,
                catalog_version=r.catalog_version,
                created_at=r.created_at,
                metric_count=len(r.definition["metrics"]),
                dimension_count=len(r.definition["dimensions"]),
                changes=service.definition_diff(previous, r.definition),
            )
        )
        previous = r.definition
    return list(reversed(result))


@router.post("/{topic_id}/releases/{version}/restore", dependencies=admin)
def restore_release(
    topic_id: uuid.UUID,
    version: int,
    body: RevisionRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> TopicDetail:
    topic = service.get_topic(session, topic_id, lock=True)
    service.expected(topic, body.expected_revision)
    release = service.release_for(session, topic, version)
    if not release:
        raise HTTPException(404, "语义版本不存在")
    topic.draft = release.definition
    service.changed(session, topic, current_user, "release_restored_to_draft")
    return service.detail(session, topic)


@router.put("/{topic_id}/members", dependencies=admin)
def save_members(
    topic_id: uuid.UUID,
    body: MembersUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> TopicDetail:
    topic = service.get_topic(session, topic_id, lock=True)
    service.expected(topic, body.expected_revision)
    for user_id in set(body.user_ids):
        user = session.get(User, user_id)
        if not user or not user.is_active:
            raise HTTPException(422, "授权成员中有不存在或停用的账号")
    for row in session.exec(
        select(TopicMember).where(TopicMember.topic_id == topic.id)
    ).all():
        session.delete(row)
    session.flush()
    for user_id in set(body.user_ids):
        session.add(TopicMember(topic_id=topic.id, user_id=user_id))
    service.changed(session, topic, current_user, "members_updated")
    return service.detail(session, topic)


@router.post("/{topic_id}/import", dependencies=admin)
def import_definition(
    topic_id: uuid.UUID,
    body: ImportRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> TopicDetail:
    definition = service.parse_definition(body.content)
    topic = service.get_topic(session, topic_id, lock=True)
    service.expected(topic, body.expected_revision)
    topic.draft = definition.model_dump(mode="json")
    service.changed(session, topic, current_user, "draft_imported")
    return service.detail(session, topic)


@router.get("/{topic_id}/export", dependencies=admin)
def export_definition(
    topic_id: uuid.UUID,
    session: SessionDep,
    format: Literal["json", "yaml"] = "yaml",
    version: Annotated[int, Query(ge=0)] = 0,
) -> ExportPublic:
    topic = service.get_topic(session, topic_id)
    definition = topic.draft
    if version:
        release = service.release_for(session, topic, version)
        if not release:
            raise HTTPException(404, "语义版本不存在")
        definition = release.definition
    return ExportPublic(
        filename=f"topic-{topic.id}-{'v' + str(version) if version else 'draft'}.{format}",
        content=service.export_definition(definition, format),
    )


@router.get("/{topic_id}/published")
def get_published_topic(
    topic_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> PublishedTopic:
    return service.public_catalog(session, topic_id, current_user)


@router.delete("/{topic_id}", dependencies=admin)
def delete_draft_topic(
    topic_id: uuid.UUID,
    expected_revision: Annotated[int, Query(ge=1)],
    session: SessionDep,
    current_user: CurrentUser,
) -> Message:
    topic = service.get_topic(session, topic_id, lock=True)
    service.expected(topic, expected_revision)
    if topic.current_version:
        raise HTTPException(409, "已发布主题需保留历史，请使用停用功能")
    service.audit(session, topic, current_user, "draft_deleted")
    for member in session.exec(
        select(TopicMember).where(TopicMember.topic_id == topic.id)
    ).all():
        session.delete(member)
    session.delete(topic)
    service.commit(session)
    return Message(message="未发布主题已删除")
