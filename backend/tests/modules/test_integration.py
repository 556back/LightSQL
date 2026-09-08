import asyncio
import uuid
from datetime import timedelta

import jwt
import pytest
from sqlmodel import Session, select

from app.core.security import create_access_token
from app.models import User
from app.modules.datasources.models import now
from app.modules.integration import service, worker
from app.modules.integration.models import (
    EmbedTicket,
    IntegrationClient,
    IntegrationTask,
)
from app.modules.query import service as queries
from app.modules.query.models import QueryJob
from app.modules.semantic.models import TopicMember
from tests.modules.test_assistant import assistant_env  # noqa: F401
from tests.modules.test_semantic import topic_env  # noqa: F401

BASE = "/api/integration/v1"
ADMIN = "/api/v1/integrations"
ORIGIN = "https://erp.example.com"


@pytest.fixture
def integration_env(assistant_env):  # noqa: F811
    client, engine, admin, topic_url, _, calls = assistant_env
    topic_id = topic_url.rsplit("/", 1)[1]
    user = User(email="integration-member@example.com", hashed_password="unused")
    with Session(engine) as session:
        session.add(user)
        session.add(TopicMember(topic_id=uuid.UUID(topic_id), user_id=user.id))
        session.commit()
        session.refresh(user)
    grant = {
        "user_id": str(user.id),
        "metric_ids": ["revenue"],
        "dimension_ids": ["region", "day"],
        "rows": [{"model_id": "orders", "column": "tenant_id", "values": ["1"]}],
    }
    response = client.put(
        f"/api/v1/queries/topics/{topic_id}/policy",
        json={"expected_revision": 0, "grants": [grant]},
    )
    assert response.status_code == 200, response.text
    body = {
        "name": "ERP",
        "ceiling_user_id": str(user.id),
        "topic_ids": [topic_id],
        "scopes": ["query", "ask", "embed", "analysis"],
        "origins": [ORIGIN],
    }
    created = client.post(ADMIN + "/", json=body)
    assert created.status_code == 201, created.text
    record = created.json()
    credentials = {"client_id": record["id"], "client_secret": record["client_secret"]}
    token = client.post(BASE + "/token", json=credentials)
    assert token.status_code == 200, token.text
    headers = {"Authorization": f"Bearer {token.json()['access_token']}"}
    return client, engine, admin, user, topic_id, record, credentials, headers, calls


def submit(env, operation="queries", key=None, **extra):
    client, _, _, _, topic_id, _, _, headers, _ = env
    data = {
        "topic_id": topic_id,
        **(
            {"plan": {"metrics": ["revenue"]}}
            if operation == "queries"
            else {"question": "按区域统计销售额"}
        ),
        **extra,
    }
    return client.post(
        BASE + f"/{operation}",
        headers={**headers, "Idempotency-Key": key or str(uuid.uuid4())},
        json=data,
    )


def test_configuration_check_is_read_only_and_reports_reasons(integration_env):
    client, engine, _, user, topic_id, record, _, _, calls = integration_env
    body = {
        k: v for k, v in record.items() if k not in {"id", "revision", "client_secret"}
    }
    response = client.post(ADMIN + "/check", json=body)
    assert response.status_code == 200, response.text
    assert response.json()["ok"] is True
    assert response.json()["topics"][0]["topic_id"] == topic_id
    assert not calls
    with Session(engine) as session:
        assert len(session.exec(select(IntegrationClient)).all()) == 1
        assert not session.exec(select(IntegrationTask)).all()
        membership = session.exec(
            select(TopicMember).where(TopicMember.user_id == user.id)
        ).first()
        session.delete(membership)
        session.commit()
    body.update(origins=[], model_calls_per_day=0)
    blocked = client.post(ADMIN + "/check", json=body).json()
    assert not blocked["ok"]
    assert not blocked["topics"][0]["ok"]
    assert len(blocked["warnings"]) == 2
    assert not calls


@pytest.mark.parametrize(
    "patch",
    [
        {"name": "   "},
        {"origins": ["https://example.com:invalid"]},
        {"requests_per_minute": 9},
    ],
)
def test_configuration_check_rejects_invalid_input(integration_env, patch):
    client, _, _, _, _, record, _, _, _ = integration_env
    body = {
        k: v for k, v in record.items() if k not in {"id", "revision", "client_secret"}
    }
    assert client.post(ADMIN + "/check", json={**body, **patch}).status_code == 422


def test_configuration_check_requires_internal_admin(integration_env):
    from app.api.deps import get_current_user

    client, _, _, _, _, record, _, headers, _ = integration_env
    body = {
        k: v for k, v in record.items() if k not in {"id", "revision", "client_secret"}
    }
    override = client.app.dependency_overrides.pop(get_current_user)
    try:
        assert client.post(
            ADMIN + "/check", json=body, headers=headers
        ).status_code in (401, 403)
    finally:
        if override is not None:
            client.app.dependency_overrides[get_current_user] = override


def advance(engine, task_id):
    task_id = uuid.UUID(str(task_id))
    with Session(engine) as session:
        task = session.get(IntegrationTask, task_id)
        lease = uuid.uuid4()
        task.lease_id = lease
        task.lease_until = now() + timedelta(minutes=3)
        session.add(task)
        session.commit()
    asyncio.run(worker.advance(engine, task_id, lease))


def succeed(engine, task_id):
    with Session(engine) as session:
        task = session.get(IntegrationTask, uuid.UUID(str(task_id)))
        job = session.get(QueryJob, task.query_id)
        assert job is not None
        job.status = "succeeded"
        job.finished_at = now()
        job.row_count = 1
        job.result = {
            "columns": [
                {
                    "id": "revenue",
                    "label": "销售额",
                    "value_type": "number",
                    "unit": "元",
                    "timezone": "",
                }
            ],
            "rows": [["9007199254740993.25"]],
            "truncated": False,
            "notes": [],
        }
        session.add(job)
        session.commit()


def test_application_credentials_and_admin_projection(integration_env):
    client, _, admin, _, _, record, credentials, headers, _ = integration_env
    listing = client.get(ADMIN + "/")
    assert (
        record["client_secret"] not in listing.text
        and "secret_hash" not in listing.text
    )
    assert client.get(BASE + "/topics", headers=headers).status_code == 200
    assert (
        client.post(
            BASE + "/token", json={**credentials, "client_secret": "wrong"}
        ).status_code
        == 401
    )
    admin.is_superuser = False
    assert client.get(ADMIN + "/").status_code == 403


def test_internal_token_cannot_call_integration(integration_env):
    client, _, admin, *_ = integration_env
    token = create_access_token(admin.id, timedelta(minutes=5))
    assert (
        client.get(
            BASE + "/topics", headers={"Authorization": f"Bearer {token}"}
        ).status_code
        == 401
    )
    assert client.get(BASE + "/topics").json()["code"] == "UNAUTHENTICATED"


def test_integration_token_cannot_call_internal_api(integration_env):
    from app.api.deps import get_current_user
    from app.main import app

    client, _, _, _, _, _, _, headers, _ = integration_env
    override = app.dependency_overrides.pop(get_current_user)
    try:
        assert client.get("/api/v1/users/me", headers=headers).status_code == 401
    finally:
        app.dependency_overrides[get_current_user] = override


def test_task_idempotency_and_raw_sql_rejected(integration_env):
    a = submit(integration_env, key="stable")
    assert a.status_code == 202, a.text
    b = submit(integration_env, key="stable")
    assert a.json()["task_id"] == b.json()["task_id"]
    assert (
        submit(
            integration_env, key="stable", plan={"metrics": ["revenue"], "limit": 1}
        ).status_code
        == 409
    )
    assert (
        submit(
            integration_env, plan={"kind": "sql", "sql": "select * from secret"}
        ).status_code
        == 422
    )
    assert submit(integration_env, user_id=str(uuid.uuid4())).status_code == 422


def test_query_results_exact_and_revoke_invalidates_old_results(integration_env):
    client, engine, _, _, topic, record, _, headers, _ = integration_env
    response = submit(integration_env)
    task_id = response.json()["task_id"]
    advance(engine, task_id)
    succeed(engine, task_id)
    advance(engine, task_id)
    result = client.get(BASE + f"/tasks/{task_id}/result", headers=headers)
    assert result.status_code == 200, result.text
    assert result.json()["rows"] == [["9007199254740993.25"]]
    assert "sql" not in result.json() and "secret" not in result.text
    assert result.headers["cache-control"] == "no-store"
    with Session(engine) as session:
        job = session.get(
            QueryJob, session.get(IntegrationTask, uuid.UUID(task_id)).query_id
        )
        compiled = queries.recheck(session, job)
        assert "tenant_id" in compiled.sql
        app = session.get(IntegrationClient, uuid.UUID(record["id"]))
        app.enabled = False
        session.add(app)
        session.commit()
    assert (
        client.get(BASE + f"/tasks/{task_id}/result", headers=headers).status_code
        == 403
    )


def test_cross_application_results_isolated(integration_env):
    client, _, _, user, topic, _, _, headers, _ = integration_env
    task_id = submit(integration_env).json()["task_id"]
    other = client.post(
        ADMIN + "/",
        json={"name": "Other", "ceiling_user_id": str(user.id), "topic_ids": [topic]},
    ).json()
    token = client.post(
        BASE + "/token",
        json={"client_id": other["id"], "client_secret": other["client_secret"]},
    ).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {token}"}
    assert (
        client.get(BASE + f"/tasks/{task_id}", headers=other_headers).status_code == 404
    )
    assert client.get(BASE + f"/tasks/{task_id}", headers=headers).status_code == 200


def ticket(env, origin=ORIGIN):
    client, _, _, _, topic, _, _, headers, _ = env
    return client.post(
        BASE + "/embed/tickets",
        headers=headers,
        json={"origin": origin, "challenge": "a" * 32, "topic_id": topic},
    )


def test_embed_ticket_one_use_and_wrong_origin(integration_env):
    client = integration_env[0]
    assert ticket(integration_env, "https://evil.example").status_code == 403
    value = ticket(integration_env).json()["ticket"]
    wrong = client.post(
        BASE + "/embed/sessions", json={"ticket": value, "challenge": "b" * 32}
    )
    assert wrong.status_code == 401
    first = client.post(
        BASE + "/embed/sessions", json={"ticket": value, "challenge": "a" * 32}
    )
    assert first.status_code == 201, first.text
    assert (
        client.post(
            BASE + "/embed/sessions", json={"ticket": value, "challenge": "a" * 32}
        ).status_code
        == 401
    )
    headers = {"Authorization": f"Bearer {first.json()['access_token']}"}
    assert (
        client.post(
            BASE + "/embed/tickets",
            headers=headers,
            json={"origin": ORIGIN, "challenge": "a" * 32},
        ).status_code
        == 403
    )
    assert (
        client.delete(
            BASE + f"/embed/sessions/{first.json()['session_id']}", headers=headers
        ).status_code
        == 200
    )
    assert client.get(BASE + "/topics", headers=headers).status_code == 401


def test_ticket_expiration_and_secret_validation_redaction(integration_env):
    client, engine, *_ = integration_env
    value = ticket(integration_env).json()["ticket"]
    with Session(engine) as session:
        record = session.exec(select(EmbedTicket)).first()
        record.expires_at = now() - timedelta(seconds=1)
        session.add(record)
        session.commit()
    assert (
        client.post(
            BASE + "/embed/sessions", json={"ticket": value, "challenge": "a" * 32}
        ).status_code
        == 401
    )
    invalid = client.post(
        BASE + "/embed/sessions", json={"ticket": value, "challenge": "short"}
    )
    assert invalid.status_code == 422 and value not in invalid.text


def test_answer_runs_once_and_continuation(integration_env):
    client, engine, _, _, _, _, _, headers, calls = integration_env
    response = submit(integration_env, "answers", key="question")
    assert response.status_code == 202, response.text
    task = response.json()
    assert task["conversation_id"]
    advance(engine, task["task_id"])
    assert len(calls) == 1
    assert (
        submit(integration_env, "answers", key="question").json()["task_id"]
        == task["task_id"]
    )
    advance(engine, task["task_id"])
    assert len(calls) == 1
    succeed(engine, task["task_id"])
    advance(engine, task["task_id"])
    result = client.get(BASE + f"/tasks/{task['task_id']}/result", headers=headers)
    assert result.status_code == 200, result.text
    assert result.json()["evidence"]["semantic_version"]
    followup = submit(
        integration_env,
        "answers",
        conversation_id=task["conversation_id"],
        expected_revision=1,
    )
    assert followup.status_code == 202, followup.text


def test_model_lease_recovery_never_repeats_call(integration_env):
    _, engine, *rest = integration_env
    task_id = submit(integration_env, "answers").json()["task_id"]
    with Session(engine) as session:
        task = session.get(IntegrationTask, uuid.UUID(task_id))
        task.status = "planning"
        task.lease_id = uuid.uuid4()
        task.lease_until = now() - timedelta(seconds=1)
        session.add(task)
        session.commit()
    assert worker.claim(engine) is None
    with Session(engine) as session:
        assert session.get(IntegrationTask, uuid.UUID(task_id)).status == "failed"
    assert not rest[-1]


def test_cancel_queued_does_not_execute(integration_env):
    client, engine, _, _, _, _, _, headers, _ = integration_env
    task = submit(integration_env).json()
    assert (
        client.post(BASE + f"/tasks/{task['task_id']}/cancel", headers=headers).json()[
            "status"
        ]
        == "cancelled"
    )
    assert worker.claim(engine) is None
    with Session(engine) as session:
        assert not session.exec(select(QueryJob)).all()


def test_limits_and_scope(integration_env):
    assert submit(integration_env, "answers", mode="explore").status_code == 403
    for _ in range(3):
        assert submit(integration_env).status_code == 202
    assert submit(integration_env).status_code == 429


def test_public_openapi_contains_only_integration(integration_env):
    client = integration_env[0]
    response = client.get(BASE + "/openapi.json")
    assert response.status_code == 200, response.text
    paths = response.json()["paths"]
    assert BASE + "/answers" in paths
    assert all(p.startswith(BASE) for p in paths)


def test_registered_assertion_and_user_mapping(integration_env):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    client, _, _, user, topic, record, credentials, _, _ = integration_env
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = (
        key.public_key()
        .public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        .decode()
    )
    updated = {
        k: v for k, v in record.items() if k not in ("id", "client_secret", "revision")
    }
    updated.update(
        assertion_issuer="erp-identity",
        assertion_public_key=public,
        expected_revision=record["revision"],
    )
    assert client.put(ADMIN + f"/{record['id']}", json=updated).status_code == 200
    assert (
        client.put(
            ADMIN + f"/{record['id']}/identities",
            json={"subject": "employee-1", "user_id": str(user.id)},
        ).status_code
        == 200
    )
    claims = {
        "iss": "erp-identity",
        "aud": service.AUDIENCE,
        "sub": "employee-1",
        "client_id": record["id"],
        "jti": str(uuid.uuid4()),
        "iat": now(),
        "exp": now() + timedelta(seconds=60),
    }
    assertion = jwt.encode(claims, key, algorithm="RS256")
    response = client.post(
        BASE + "/token", json={**credentials, "subject_assertion": assertion}
    )
    assert response.status_code == 200, response.text
    assert (
        client.post(
            BASE + "/token", json={**credentials, "subject_assertion": assertion}
        ).status_code
        == 401
    )
    claims["client_id"] = str(uuid.uuid4())
    claims["jti"] = str(uuid.uuid4())
    assert (
        client.post(
            BASE + "/token",
            json={
                **credentials,
                "subject_assertion": jwt.encode(claims, key, algorithm="RS256"),
            },
        ).status_code
        == 401
    )


def test_analysis_child_task_preserves_query_and_precision(
    integration_env, monkeypatch
):
    import json

    from app.modules.assistant import gateway

    client, engine, _, _, _, _, _, headers, _ = integration_env
    task_id = submit(integration_env).json()["task_id"]
    advance(engine, task_id)
    succeed(engine, task_id)
    advance(engine, task_id)
    calls = []

    async def analysis_model(_config, messages, _schema):
        calls.append(messages)
        return (
            json.dumps(
                {
                    "findings": [
                        {"fact_ids": ["rows"], "interpretation": "结果范围见引用事实。"}
                    ]
                }
            ),
            {},
            1,
        )

    monkeypatch.setattr(gateway, "complete", analysis_model)
    response = client.post(
        BASE + f"/tasks/{task_id}/analysis",
        headers={**headers, "Idempotency-Key": "analysis-once"},
    )
    assert response.status_code == 202, response.text
    child = response.json()["task_id"]
    advance(engine, child)
    assert len(calls) == 1
    result = client.get(BASE + f"/tasks/{child}/result", headers=headers)
    assert result.status_code == 200, result.text
    assert result.json()["analysis_status"] == "succeeded"
    assert result.json()["rows"] == [["9007199254740993.25"]]
    with Session(engine) as session:
        assert len(session.exec(select(QueryJob)).all()) == 1


def test_analysis_budget_failure_keeps_table(integration_env):
    client, engine, _, _, _, record, _, headers, _ = integration_env
    with Session(engine) as session:
        app = session.get(IntegrationClient, uuid.UUID(record["id"]))
        app.config = {**app.config, "model_calls_per_day": 0}
        session.add(app)
        session.commit()
    task_id = submit(integration_env, include_analysis=True).json()["task_id"]
    advance(engine, task_id)
    succeed(engine, task_id)
    advance(engine, task_id)
    result = client.get(BASE + f"/tasks/{task_id}/result", headers=headers)
    assert result.status_code == 200, result.text
    assert result.json()["analysis_status"] == "failed"
    assert result.json()["rows"]


def test_revoking_embed_stops_query_worker(integration_env):
    from fastapi import HTTPException

    client, engine, _, _, topic, _, _, headers, _ = integration_env
    value = ticket(integration_env).json()["ticket"]
    embedded = client.post(
        BASE + "/embed/sessions", json={"ticket": value, "challenge": "a" * 32}
    ).json()
    response = client.post(
        BASE + "/queries",
        headers={
            "Authorization": "Bearer " + embedded["access_token"],
            "Idempotency-Key": "embed-query",
        },
        json={"topic_id": topic, "plan": {"metrics": ["revenue"]}},
    )
    assert response.status_code == 202
    task_id = response.json()["task_id"]
    advance(engine, task_id)
    assert (
        client.delete(BASE + "/embed/sessions", headers=headers).json()["revoked"] == 1
    )
    with Session(engine) as session:
        task = session.get(IntegrationTask, uuid.UUID(task_id))
        job = session.get(QueryJob, task.query_id)
        with pytest.raises(HTTPException):
            queries.recheck(session, job)
    assert client.get(BASE + f"/tasks/{task_id}", headers=headers).status_code == 403


def test_user_limit_shared_across_app_proxies(integration_env):
    from app.modules.query import worker as query_worker

    client, engine, _, user, topic, _, _, _, _ = integration_env
    first = submit(integration_env).json()["task_id"]
    advance(engine, first)
    second_app = client.post(
        ADMIN + "/",
        json={"name": "Second", "ceiling_user_id": str(user.id), "topic_ids": [topic]},
    ).json()
    auth = client.post(
        BASE + "/token",
        json={
            "client_id": second_app["id"],
            "client_secret": second_app["client_secret"],
        },
    ).json()
    second = client.post(
        BASE + "/queries",
        headers={
            "Authorization": "Bearer " + auth["access_token"],
            "Idempotency-Key": "same-user",
        },
        json={"topic_id": topic, "plan": {"metrics": ["revenue"]}},
    ).json()["task_id"]
    advance(engine, second)
    assert query_worker.claim(engine) is not None
    assert query_worker.claim(engine) is None


def test_embed_origin_header(integration_env):
    client, _, _, _, _, record, *_ = integration_env
    response = client.get("/embed/ask", params={"client_id": record["id"]})
    assert response.status_code == 200
    assert response.headers["content-security-policy"] == f"frame-ancestors {ORIGIN}"
    assert (
        client.get("/login").headers["content-security-policy"]
        == "frame-ancestors 'self'"
    )
