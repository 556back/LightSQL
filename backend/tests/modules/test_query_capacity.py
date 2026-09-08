"""Scheduler boundaries; cross-process locking is also exercised on PostgreSQL."""

import uuid
from datetime import timedelta

from sqlmodel import Session, select

from app.core.config import settings
from app.modules.datasources.models import now
from app.modules.query.models import QueryEvent, QueryJob
from app.modules.query.worker import claim


def queued(session, *, source=None, actor=None, **values):
    job = QueryJob(
        actor_id=actor or uuid.uuid4(),
        source_id=source or uuid.uuid4(),
        request_id=uuid.uuid4(),
        topic_id=uuid.uuid4(),
        release_id=uuid.uuid4(),
        semantic_version=1,
        policy_fingerprint="test",
        plan_fingerprint="test",
        plan={},
        expires_at=now() + timedelta(hours=1),
        **values,
    )
    session.add(job)
    session.commit()
    return job.id


def test_global_capacity_and_source_fairness(env):
    _, db, _ = env
    source = uuid.uuid4()
    with Session(db) as session:
        same_source = [queued(session, source=source) for _ in range(3)]
        others = [queued(session) for _ in range(4)]
    selected = [claim(db)[0] for _ in range(5)]
    assert selected == same_source[:2] + others[:3]
    assert claim(db) is None


def test_actor_cannot_execute_twice_across_sources(env):
    _, db, _ = env
    actor = uuid.uuid4()
    with Session(db) as session:
        first = queued(session, actor=actor)
        second = queued(session, actor=actor)
        other = queued(session)
    assert claim(db)[0] == first
    assert claim(db)[0] == other
    assert claim(db) is None
    with Session(db) as session:
        job = session.get(QueryJob, first)
        job.status = "succeeded"
        session.add(job)
        session.commit()
    assert claim(db)[0] == second


def test_pending_cleanup_blocks_source_actor_and_consumes_capacity(env, monkeypatch):
    _, db, _ = env
    monkeypatch.setattr(settings, "QUERY_MAX_CONCURRENCY", 2)
    actor, source = uuid.uuid4(), uuid.uuid4()
    with Session(db) as session:
        queued(session, actor=actor, source=source, status="cleanup_pending")
        queued(session, source=source)
        queued(session, actor=actor)
        other = queued(session)
        queued(session)
    assert claim(db)[0] == other
    assert claim(db) is None


def test_queue_timeout_is_audited_even_with_full_local_pool(env):
    _, db, _ = env
    with Session(db) as session:
        job_id = queued(session, created_at=now() - timedelta(seconds=31))
    assert claim(db, allow_claim=False) is None
    assert claim(db, allow_claim=False) is None
    with Session(db) as session:
        job = session.get(QueryJob, job_id)
        assert job.status == "expired" and job.started_at is None
        assert job.finished_at is not None
        events = session.exec(
            select(QueryEvent).where(QueryEvent.job_id == job_id)
        ).all()
        assert [e.action for e in events] == ["queue_expired"]


def test_expired_lease_reserves_slot_and_allows_other_source(env):
    _, db, _ = env
    with Session(db) as session:
        stale = queued(
            session, status="running", lease_until=now() - timedelta(seconds=1)
        )
        other = queued(session)
    assert claim(db)[0] == other
    with Session(db) as session:
        assert session.get(QueryJob, stale).status == "cleanup_pending"


def test_lower_source_limit_and_cancelling_reserve_slot(env, monkeypatch):
    _, db, _ = env
    monkeypatch.setattr(settings, "QUERY_SOURCE_MAX_CONCURRENCY", 1)
    source = uuid.uuid4()
    with Session(db) as session:
        queued(
            session,
            source=source,
            status="cancelling",
            lease_until=now() + timedelta(seconds=30),
        )
        queued(session, source=source)
        other = queued(session)
    assert claim(db)[0] == other
    assert claim(db) is None
