import json
import uuid
from typing import Any, Literal

import yaml
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select

from app.models import User
from app.modules.catalog.models import CatalogState
from app.modules.datasources.models import DataSource, now
from app.modules.semantic.models import (
    PublishedDimension,
    PublishedMetric,
    PublishedTopic,
    SemanticDefinition,
    SemanticRelease,
    Topic,
    TopicAudit,
    TopicDetail,
    TopicMember,
    TopicSummary,
    ValidationReport,
)
from app.modules.semantic.validation import validate


def get_topic(session: Session, topic_id: uuid.UUID, *, lock: bool = False) -> Topic:
    query = select(Topic).where(Topic.id == topic_id)
    topic = session.exec(query.with_for_update() if lock else query).first()
    if not topic:
        raise HTTPException(404, "业务主题不存在")
    return topic


def expected(topic: Topic, revision: int) -> None:
    if topic.revision != revision:
        raise HTTPException(409, "主题已被更新，请刷新后重试；未保存的编辑请先导出备份")


def audit(session: Session, topic: Topic, actor: User, action: str) -> None:
    session.add(
        TopicAudit(
            topic_id=topic.id, actor_id=actor.id, action=action, revision=topic.revision
        )
    )


def commit(session: Session) -> None:
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "主题名称或版本冲突，请刷新后重试") from None


def changed(session: Session, topic: Topic, actor: User, action: str) -> None:
    topic.revision += 1
    topic.updated_at = now()
    session.add(topic)
    audit(session, topic, actor, action)
    commit(session)


def release_for(
    session: Session, topic: Topic, version: int | None = None
) -> SemanticRelease | None:
    return session.exec(
        select(SemanticRelease).where(
            SemanticRelease.topic_id == topic.id,
            SemanticRelease.version
            == (topic.current_version if version is None else version),
        )
    ).first()


def report(
    session: Session, topic: Topic, definition: SemanticDefinition | None = None
) -> ValidationReport:
    result = validate(
        definition or SemanticDefinition.model_validate(topic.draft),
        session.get(DataSource, topic.source_id),
        session.get(CatalogState, topic.source_id),
    )
    result.draft_revision = topic.revision
    return result


def availability(
    session: Session, topic: Topic
) -> Literal["draft", "ready", "needs_review", "disabled"]:
    if not topic.enabled:
        return "disabled"
    release = release_for(session, topic)
    if not release:
        return "draft"
    checked = report(
        session, topic, SemanticDefinition.model_validate(release.definition)
    )
    return (
        "ready"
        if checked.valid and checked.binding_digest == release.binding_digest
        else "needs_review"
    )


def summary(session: Session, topic: Topic, *, admin: bool) -> TopicSummary:
    release = release_for(session, topic)
    definition = topic.draft if admin else release.definition if release else {}
    source = session.get(DataSource, topic.source_id) if admin else None
    return TopicSummary(
        id=topic.id,
        name=topic.name,
        description=topic.description,
        source_id=topic.source_id if admin else None,
        source_name=source.name if source else None,
        revision=topic.revision,
        current_version=topic.current_version,
        enabled=topic.enabled,
        availability=availability(session, topic),
        metric_count=len(definition.get("metrics", [])),
        dimension_count=len(definition.get("dimensions", [])),
        updated_at=topic.updated_at,
    )


def detail(session: Session, topic: Topic) -> TopicDetail:
    return TopicDetail(
        **summary(session, topic, admin=True).model_dump(),
        definition=SemanticDefinition.model_validate(topic.draft),
        member_ids=list(
            session.exec(
                select(TopicMember.user_id).where(TopicMember.topic_id == topic.id)
            ).all()
        ),
    )


def authorize(session: Session, topic: Topic, user: User) -> None:
    if not user.is_superuser and (
        not topic.enabled
        or not topic.current_version
        or session.get(TopicMember, (topic.id, user.id)) is None
    ):
        raise HTTPException(404, "业务主题不存在或未获授权")


def resolve_published(
    session: Session, topic_id: uuid.UUID, user: User
) -> tuple[Topic, SemanticRelease]:
    """M04+ must resolve here; caller-supplied release IDs cannot grant access."""
    topic = get_topic(session, topic_id)
    authorize(session, topic, user)
    if availability(session, topic) != "ready":
        raise HTTPException(409, "主题尚未就绪或结构已变化，请管理员复核并重新发布")
    release = release_for(session, topic)
    assert release is not None
    return topic, release


def public_catalog(session: Session, topic_id: uuid.UUID, user: User) -> PublishedTopic:
    topic, release = resolve_published(session, topic_id, user)
    definition = SemanticDefinition.model_validate(release.definition)
    return PublishedTopic(
        id=topic.id,
        name=topic.name,
        description=topic.description,
        version=release.version,
        owner=definition.owner,
        timezone=definition.timezone,
        metrics=[
            PublishedMetric(**m.model_dump(include=set(PublishedMetric.model_fields)))
            for m in definition.metrics
        ],
        dimensions=[
            PublishedDimension(
                **d.model_dump(include=set(PublishedDimension.model_fields))
            )
            for d in definition.dimensions
        ],
    )


def definition_diff(before: dict, after: dict) -> list[str]:
    changes = []
    for field, label in (
        ("owner", "责任人"),
        ("timezone", "业务时区"),
        ("external_allowed", "语义外发策略"),
    ):
        if before.get(field) != after.get(field):
            changes.append(f"{label}已更新")
    for group, label in (
        ("models", "模型"),
        ("metrics", "指标"),
        ("dimensions", "维度"),
        ("filters", "过滤"),
        ("relations", "关联"),
        ("entities", "实体词条"),
    ):
        old = {r["id"]: r for r in before.get(group, [])}
        new = {r["id"]: r for r in after.get(group, [])}
        for key in sorted(old.keys() | new.keys()):
            if old.get(key) != new.get(key):
                verb = (
                    "新增" if key not in old else "移除" if key not in new else "修改"
                )
                changes.append(f"{verb}{label}：{key}")
    return changes


class UniqueLoader(yaml.SafeLoader):
    def construct_mapping(self, node: Any, deep: bool = False) -> dict:
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in result:
                raise ValueError("配置中存在非文本或重复键")
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def parse_definition(content: str) -> SemanticDefinition:
    if len(content.encode("utf8")) > 200_000:
        raise HTTPException(422, "配置文件不能超过 200 KB")
    try:
        if any(
            isinstance(
                token,
                (yaml.tokens.AliasToken, yaml.tokens.AnchorToken, yaml.tokens.TagToken),
            )
            for token in yaml.scan(content)
        ):
            raise ValueError("不支持 YAML 锚点、别名或自定义标签")
        raw = yaml.load(content, Loader=UniqueLoader)
        return SemanticDefinition.model_validate(raw)
    except ValidationError as exc:
        messages = [
            f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors()[:8]
        ]
        raise HTTPException(422, "语义配置格式错误：" + "；".join(messages)) from None
    except yaml.YAMLError, ValueError, TypeError, RecursionError:
        raise HTTPException(
            422, "配置不是合法的 JSON/YAML，或含重复键、锚点、自定义标签"
        ) from None


def export_definition(definition: dict, fmt: str) -> str:
    return (
        yaml.safe_dump(definition, allow_unicode=True, sort_keys=False)
        if fmt == "yaml"
        else json.dumps(definition, ensure_ascii=False, indent=2)
    )


def all_topics(session: Session, user: User) -> list[Topic]:
    query = select(Topic)
    if not user.is_superuser:
        query = query.join(TopicMember).where(
            TopicMember.user_id == user.id,
            col(Topic.enabled).is_(True),
            Topic.current_version > 0,
        )
    return list(session.exec(query.order_by(col(Topic.updated_at).desc())).all())
