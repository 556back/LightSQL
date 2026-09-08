import json
from datetime import timedelta

from fastapi import HTTPException
from sqlmodel import col, select

from app.modules.assistant.models import Conversation
from app.modules.datasources.models import now
from app.modules.datasources.service import decrypt_password, encrypt_password
from app.modules.quality.models import (
    DatasetInput,
    EvaluationDataset,
    FeedbackReviewPublic,
    QualityAudit,
    QualityFeedback,
)


def encode(value: dict) -> str:
    raw = json.dumps(value, ensure_ascii=False)
    if len(raw.encode()) > 2_000_000:
        raise HTTPException(422, "单个质量记录不能超过 2 MB")
    return encrypt_password(raw)


def decode(value: str) -> dict:
    return json.loads(decrypt_password(value))


def purge_feedback(session):
    records = session.exec(
        select(QualityFeedback).where(QualityFeedback.expires_at <= now())
    ).all()
    for record in records:
        session.delete(record)


def capture_feedback(session, user, turn, payload):
    purge_feedback(session)
    conversation = session.get(Conversation, turn.conversation_id)
    record = session.exec(
        select(QualityFeedback).where(QualityFeedback.turn_id == turn.id)
    ).first()
    timestamp = now()
    snapshot = {
        "question": payload.get("question", ""),
        "plan": payload.get("plan"),
        "feedback": payload["feedback"],
        "model": turn.model,
        "gateway_revision": turn.gateway_revision,
        "query_job_id": str(turn.query_job_id) if turn.query_job_id else None,
        "release_id": str(conversation.release_id),
    }
    if record:
        previous = decode(record.encrypted_payload)
        snapshot["reviews"] = previous.get("reviews", [])
        record.revision += 1
        record.status = "pending"
        record.updated_at = timestamp
    else:
        record = QualityFeedback(
            turn_id=turn.id,
            topic_id=conversation.topic_id,
            actor_id=user.id,
            release_id=conversation.release_id,
            encrypted_payload="",
            expires_at=timestamp + timedelta(days=90),
        )
    record.encrypted_payload = encode(snapshot)
    session.add(record)
    session.add(
        QualityAudit(
            feedback_id=record.id,
            actor_id=user.id,
            action="submitted",
            revision=record.revision,
        )
    )


def public_feedback(record):
    return FeedbackReviewPublic(
        **record.model_dump(
            exclude={"encrypted_payload", "actor_id", "release_id", "created_at"}
        ),
        snapshot=decode(record.encrypted_payload),
    )


def review(session, user, record_id, body):
    from app.modules.query.service import gate

    gate(session)
    record = session.get(QualityFeedback, record_id, populate_existing=True)
    if not record or record.expires_at.replace(tzinfo=now().tzinfo) <= now():
        raise HTTPException(404, "反馈已过期或不存在")
    if record.revision != body.expected_revision:
        raise HTTPException(409, "反馈已更新，请刷新后重新审核")
    if bool(body.dataset_id) != bool(body.case_id) or (
        body.status == "resolved" and not body.dataset_id
    ):
        raise HTTPException(422, "已解决的反馈必须关联经核对的回归题")
    if body.dataset_id:
        dataset = session.get(EvaluationDataset, body.dataset_id)
        if not dataset or dataset.topic_id != record.topic_id:
            raise HTTPException(422, "回归题集必须属于反馈主题")
        definition = DatasetInput.model_validate(decode(dataset.encrypted_payload))
        if body.case_id not in {c.id for c in definition.cases}:
            raise HTTPException(422, "回归题目不存在")
    snapshot = decode(record.encrypted_payload)
    history = snapshot.get("reviews", [])
    if len(history) >= 100:
        raise HTTPException(422, "该反馈已达到 100 次审核上限")
    history.append(
        {
            **body.model_dump(mode="json"),
            "reviewer": str(user.id),
            "at": now().isoformat(),
        }
    )
    snapshot["reviews"] = history
    record.encrypted_payload = encode(snapshot)
    record.status, record.updated_at = body.status, now()
    record.revision += 1
    session.add(record)
    session.add(
        QualityAudit(
            feedback_id=record.id,
            actor_id=user.id,
            action=body.status,
            revision=record.revision,
        )
    )
    session.commit()
    session.refresh(record)
    return public_feedback(record)


def feedback_list(session, offset=0):
    purge_feedback(session)
    session.commit()
    return [
        public_feedback(r)
        for r in session.exec(
            select(QualityFeedback)
            .order_by(col(QualityFeedback.updated_at).desc())
            .offset(offset)
            .limit(100)
        ).all()
    ]
