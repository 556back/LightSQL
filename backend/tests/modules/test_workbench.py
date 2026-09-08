# ruff: noqa: F811
import asyncio
import uuid
from datetime import timedelta

import pytest
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import User
from app.modules.assistant import service, workbench
from app.modules.assistant.models import AssistantTurn, Conversation
from app.modules.datasources.models import now
from app.modules.query.models import QueryJob
from tests.modules.test_assistant import (  # noqa: F401
    ask,
    assistant_env,
    topic_env,
)
from tests.modules.test_semantic import publish


def test_evidence_uses_compiled_sources_and_published_definition(assistant_env):
    client, _, _, _, url, _ = assistant_env
    turn = ask(client, url).json()["turns"][-1]
    result = client.get(url + f"/turns/{turn['id']}/evidence")
    assert result.status_code == 200, result.text
    data = result.json()
    assert data["semantic_version"] == 1
    assert data["owner"] == "经营管理部"
    assert len(data["sources"]) == 2
    assert any("sales.orders" in s for s in data["sources"])
    assert data["fixed_filters"]
    assert data["query_id"] is None and data["queried_at"] is None
    assert any("不代表数据更新水位" in s for s in data["notes"])


def test_feedback_upsert_encrypted_and_history_roundtrip(assistant_env):
    client, engine, _, _, url, calls = assistant_env
    turn = ask(client, url).json()["turns"][-1]
    endpoint = url + f"/turns/{turn['id']}/feedback"
    body = {
        "rating": "incorrect",
        "category": "metric",
        "comment": "口径待核对-私人说明",
    }
    assert client.put(endpoint, json=body).status_code == 200
    assert client.get(url).json()["turns"][0]["feedback"]["comment"] == body["comment"]
    with Session(engine) as session:
        record = session.get(AssistantTurn, uuid.UUID(turn["id"]))
        assert body["comment"] not in record.encrypted_payload
        assert service.unpack(record)["plan"]
    assert client.put(endpoint, json={"rating": "helpful"}).status_code == 200
    history = client.get("/api/v1/assistant/conversations").json()
    assert history[0]["turns"][0]["feedback"]["rating"] == "helpful"
    assert history[0]["created_at"]
    assert len(calls) == 1  # Feedback must never call the model.


@pytest.mark.parametrize(
    "body",
    [
        {"rating": "incorrect"},
        {"rating": "other"},
        {"rating": "helpful", "comment": "x" * 1001},
    ],
)
def test_invalid_feedback_rejected(assistant_env, body):
    client, _, _, _, url, _ = assistant_env
    turn = ask(client, url).json()["turns"][-1]
    assert (
        client.put(url + f"/turns/{turn['id']}/feedback", json=body).status_code == 422
    )


def test_other_owner_and_changed_release_cannot_read_or_feedback(assistant_env):
    client, _, actor, topic_url, url, _ = assistant_env
    turn = ask(client, url).json()["turns"][-1]
    endpoint = url + f"/turns/{turn['id']}"
    old = actor.id
    actor.id = uuid.uuid4()
    assert client.get(endpoint + "/evidence").status_code == 404
    assert client.get(url + "/events").status_code == 404
    assert (
        client.put(endpoint + "/feedback", json={"rating": "helpful"}).status_code
        == 404
    )
    actor.id = old
    assert publish(client, topic_url).status_code == 201
    assert client.get(endpoint + "/evidence").status_code == 409
    assert (
        client.put(endpoint + "/feedback", json={"rating": "helpful"}).status_code
        == 409
    )


def test_snapshot_restores_jobs_without_resubmission_and_rechecks_account(
    assistant_env,
):
    client, engine, actor, _, url, calls = assistant_env
    turn = ask(client, url).json()["turns"][-1]
    response = client.post(url + f"/turns/{turn['id']}/execute")
    assert response.status_code == 202
    conversation_id = uuid.UUID(url.split("/")[-1])
    first = workbench.snapshot(engine, actor.id, conversation_id)
    second = workbench.snapshot(engine, actor.id, conversation_id)
    assert first == second and first["jobs"][0]["status"] == "queued"
    assert len(calls) == 1
    with Session(engine) as session:
        assert len(session.exec(select(QueryJob)).all()) == 1
        user = session.get(User, actor.id)
        user.is_active = False
        session.add(user)
        session.commit()
    with pytest.raises(HTTPException) as exc:
        workbench.snapshot(engine, actor.id, conversation_id)
    assert exc.value.status_code == 403


def test_expired_feedback_is_purged_and_snapshot_denied(assistant_env):
    client, engine, actor, _, url, _ = assistant_env
    turn = ask(client, url).json()["turns"][-1]
    assert (
        client.put(
            url + f"/turns/{turn['id']}/feedback", json={"rating": "helpful"}
        ).status_code
        == 200
    )
    conversation_id = uuid.UUID(url.split("/")[-1])
    with Session(engine) as session:
        conversation = session.get(Conversation, conversation_id)
        conversation.expires_at = now() - timedelta(seconds=1)
        session.add(conversation)
        session.commit()
    with pytest.raises(HTTPException) as exc:
        workbench.snapshot(engine, actor.id, conversation_id)
    assert exc.value.status_code == 410
    with Session(engine) as session:
        assert not session.get(AssistantTurn, uuid.UUID(turn["id"])).encrypted_payload


def test_stream_frame_and_access_error(assistant_env):
    from app.api.routes.assistant import conversation_events

    client, engine, actor, _, url, _ = assistant_env
    ask(client, url)
    conversation_id = uuid.UUID(url.split("/")[-1])

    class Request:
        async def is_disconnected(self):
            return False

    async def verify():
        with Session(engine) as session:
            response = await conversation_events(
                conversation_id, Request(), session, actor
            )
            iterator = response.body_iterator
            frame = await anext(iterator)
            assert "event: snapshot" in frame and "id: " in frame

            with Session(engine) as other:
                user = other.get(User, actor.id)
                user.is_active = False
                other.add(user)
                other.commit()
            frame = await anext(iterator)
            assert "event: access_error" in frame and "账号已不可用" in frame
            await iterator.aclose()

    asyncio.run(verify())
