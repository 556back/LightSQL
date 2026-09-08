import asyncio
import json
import uuid
from datetime import date, timedelta

import httpx
import pytest
from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.config import settings
from app.modules.assistant import context, gateway
from app.modules.assistant.models import AssistantTurn, Conversation, ModelGateway
from app.modules.datasources.models import now
from app.modules.datasources.service import decrypt_password
from app.modules.query.models import QueryGrant, QueryJob, QueryPlan
from app.modules.semantic.models import SemanticDefinition
from tests.modules.test_semantic import (  # noqa: F401
    definition,
    publish,
    save,
    topic_env,
)

BASE = "/api/v1/assistant"
KEY = "secret-model-key-never-return"
CONFIG = {
    "name": "测试智谱",
    "provider": "zhipu",
    "base_url": gateway.PRESETS[0]["base_url"],
    "model": "test-model",
    "api_key": KEY,
}


def allowed():
    data = definition()
    data["external_allowed"] = True
    for item in data["metrics"] + data["dimensions"]:
        item["external_allowed"] = True
    return data


@pytest.fixture
def assistant_env(topic_env, monkeypatch):  # noqa: F811
    client, engine, actor, source, topic_url = topic_env
    assert save(client, topic_url, allowed()).status_code == 200
    assert publish(client, topic_url).status_code == 201
    config = client.post(BASE + "/gateways", json=CONFIG)
    assert config.status_code == 201, config.text
    assert (
        client.post(
            BASE + f"/gateways/{config.json()['id']}/activate",
            json={"expected_revision": 1},
        ).status_code
        == 200
    )
    conversation = client.post(
        BASE + "/conversations", json={"topic_id": topic_url.split("/")[-1]}
    )
    assert conversation.status_code == 201, conversation.text
    calls = []

    async def fake(config, messages, schema):
        calls.append((config, messages, schema))
        return (
            json.dumps(
                {
                    "action": "plan",
                    "plan": {
                        "metrics": ["revenue"],
                        "dimensions": [{"dimension_id": "region"}],
                    },
                }
            ),
            {"prompt_tokens": 40, "completion_tokens": 20},
            1,
        )

    monkeypatch.setattr(gateway, "complete", fake)
    return (
        client,
        engine,
        actor,
        topic_url,
        BASE + "/conversations/" + conversation.json()["id"],
        calls,
    )


def ask(client, url, question="按区域统计销售额", **kwargs):
    revision = client.get(url).json()["revision"]
    return client.post(
        url + "/turns",
        json={
            "question": question,
            "mode": "metrics",
            "request_id": str(uuid.uuid4()),
            "expected_revision": revision,
            **kwargs,
        },
    )


def test_gateway_encrypt_update_switch_and_admin(env):
    client, engine, actor = env
    created = client.post(BASE + "/gateways", json=CONFIG)
    assert created.status_code == 201, created.text
    config = created.json()
    assert KEY not in created.text and "encrypted_key" not in created.text
    with Session(engine) as session:
        record = session.get(ModelGateway, uuid.UUID(config["id"]))
        assert decrypt_password(record.encrypted_key) == KEY
    update = {**CONFIG, "api_key": "", "expected_revision": 1, "model": "another-model"}
    assert (
        client.put(BASE + f"/gateways/{config['id']}", json=update).json()["revision"]
        == 2
    )
    assert (
        client.put(BASE + f"/gateways/{config['id']}", json=update).status_code == 409
    )
    assert (
        client.put(
            BASE + f"/gateways/{config['id']}",
            json={
                **update,
                "expected_revision": 2,
                "provider": "deepseek",
                "base_url": "https://api.deepseek.com",
            },
        ).status_code
        == 422
    )
    assert (
        client.post(
            BASE + f"/gateways/{config['id']}/activate", json={"expected_revision": 2}
        ).status_code
        == 200
    )
    assert client.get(BASE + "/status").json()["configured"]
    assert KEY not in client.get(BASE + "/gateways").text
    assert client.post(BASE + "/gateways/deactivate").status_code == 200
    actor.is_superuser = False
    assert client.get(BASE + "/gateways").status_code == 403
    assert client.post(BASE + "/gateways", json=CONFIG).status_code == 403
    assert (
        client.post(
            BASE + f"/gateways/{config['id']}/test", json={"expected_revision": 2}
        ).status_code
        == 403
    )


@pytest.mark.parametrize(
    "url",
    [
        "http://open.bigmodel.cn/api/paas/v4",
        "https://evil.example/v1",
        "https://open.bigmodel.cn@evil.example/v1",
        "https://open.bigmodel.cn/api/paas/v4?key=secret",
        "https://127.0.0.1/v1",
    ],
)
def test_invalid_endpoint_and_validation_never_echo_key(env, url):
    client, _, _ = env
    response = client.post(BASE + "/gateways", json={**CONFIG, "base_url": url})
    assert response.status_code == 422 and KEY not in response.text
    bad = client.post(BASE + "/gateways", json={**CONFIG, "api_key": KEY * 1000})
    assert bad.status_code == 422 and KEY not in bad.text


def test_custom_endpoint_requires_deployment_allowlist(monkeypatch):
    with pytest.raises(HTTPException):
        gateway.validate_endpoint("custom", "https://model.internal/v1")
    monkeypatch.setattr(
        settings, "MODEL_GATEWAY_ALLOWED_BASE_URLS", ["https://model.internal/v1"]
    )
    assert (
        gateway.validate_endpoint("custom", "https://model.internal/v1/")
        == "https://model.internal/v1"
    )


def test_plan_roundtrip_execute_idempotency_and_encrypted_history(assistant_env):
    client, engine, _, _, url, calls = assistant_env
    request_id = str(uuid.uuid4())
    result = ask(client, url, request_id=request_id)
    assert result.status_code == 200, result.text
    turn = result.json()["turns"][-1]
    assert turn["status"] == "ready", result.text
    assert turn["attempts"] == 1
    assert len(calls) == 1
    assert ask(client, url, request_id=request_id).json()["revision"] == 1
    assert len(calls) == 1
    assert ask(client, url, "销售额", request_id=request_id).status_code == 409
    first = client.post(url + f"/turns/{turn['id']}/execute")
    assert first.status_code == 202, first.text
    second = client.post(url + f"/turns/{turn['id']}/execute")
    assert first.json()["id"] == second.json()["id"]
    with Session(engine) as session:
        record = session.get(AssistantTurn, uuid.UUID(turn["id"]))
        assert "销售额" not in record.encrypted_payload
        assert record.prompt_tokens == 40 and record.completion_tokens == 20
        assert len(session.exec(select(QueryJob)).all()) == 1


def test_local_entity_and_history_redaction(assistant_env, monkeypatch):
    client, _, _, _, url, _ = assistant_env
    sent = []

    async def fake(_config, messages, _schema):
        sent.append(json.dumps(messages, ensure_ascii=False))
        return (
            json.dumps(
                {
                    "action": "plan",
                    "plan": {
                        "metrics": ["revenue"],
                        "filters": [
                            {
                                "dimension_id": "channel",
                                "operator": "eq",
                                "values": ["value_1"],
                            }
                        ],
                    },
                }
            ),
            {},
            0,
        )

    monkeypatch.setattr(gateway, "complete", fake)
    first = ask(client, url, "官网销售额")
    assert first.json()["turns"][-1]["plan"]["filters"][0]["values"] == [
        "private_channel_code"
    ]
    assert ask(client, url, "按区域分组").json()["turns"][-1]["status"] == "ready"
    for text in sent:
        for private in (
            "private_channel_code",
            "官网",
            "线上直营",
            "sales.orders",
            "tenant_id",
            "encrypted_key",
        ):
            assert private not in text
    assert "previous_plan" in sent[-1]


@pytest.mark.parametrize(
    "question",
    [
        "张三的销售额",
        "帮我瞅瞅最近销售表现，画个图呗",
        "编号13800138000的销售额",
        "销售额超过10000000了吗",
    ],
)
def test_natural_language_is_not_a_vocabulary_allowlist(assistant_env, question):
    client, _, _, _, url, calls = assistant_env
    result = ask(client, url, question)
    assert result.json()["turns"][-1]["status"] == "ready"
    assert len(calls) == 1
    assert json.loads(calls[0][1][1]["content"])["question"] == question


def test_external_permission_and_authorized_catalog():
    data = allowed()
    data["metrics"][0]["external_allowed"] = False
    definition = SemanticDefinition.model_validate(data)
    grant = QueryGrant(
        user_id=uuid.uuid4(),
        metric_ids=["orders_count"],
        dimension_ids=["region"],
        unrestricted=True,
    )
    prepared = context.prepare(
        definition, grant, "订单数按区域", None, {}, date(2026, 9, 7)
    )
    assert [m["id"] for m in prepared.catalog["metrics"]] == ["orders_count"]
    assert [d["id"] for d in prepared.catalog["dimensions"]] == ["region"]
    with pytest.raises(HTTPException):
        context.materialize(QueryPlan(metrics=["revenue"]), prepared)
    definition.external_allowed = False
    with pytest.raises(HTTPException):
        context.prepare(definition, grant, "订单数", None, {}, date(2026, 9, 7))


def test_ambiguous_entities_require_local_choice():
    data = allowed()
    data["entities"].append(
        {
            "id": "web2",
            "label": "另一官网",
            "aliases": ["官网"],
            "dimension_id": "channel",
            "value": "other_private_code",
        }
    )
    definition = SemanticDefinition.model_validate(data)
    prepared = context.prepare(definition, None, "官网销售额", None, {}, date.today())
    assert len(prepared.ambiguities[0].options) == 2
    assert not prepared.refs
    chosen = context.prepare(
        definition, None, "官网销售额", None, {"官网": "web2"}, date.today()
    )
    assert not chosen.ambiguities and chosen.refs["value_1"][1] == "other_private_code"
    with pytest.raises(HTTPException):
        context.prepare(
            definition, None, "官网销售额", None, {"官网": "bogus"}, date.today()
        )


@pytest.mark.parametrize(
    "value,dimension",
    [
        ("private_channel_code", "channel"),
        ("value_99", "channel"),
        ("value_1", "region"),
    ],
)
def test_model_cannot_forge_values_or_cross_dimension_refs(value, dimension):
    prepared = context.prepare(
        SemanticDefinition.model_validate(allowed()),
        None,
        "官网销售额",
        None,
        {},
        date.today(),
    )
    plan = QueryPlan(
        metrics=["revenue"],
        filters=[{"dimension_id": dimension, "operator": "eq", "values": [value]}],
    )
    with pytest.raises(HTTPException):
        context.materialize(plan, prepared)


def test_repair_bounded_and_no_unsafe_error_forwarding(assistant_env, monkeypatch):
    client, _, _, _, url, _ = assistant_env
    sent = []

    async def invalid(_config, messages, _schema):
        sent.append(json.dumps(messages))
        return (
            '{"action":"plan","plan":{"metrics":["revenue"],"sql":"SECRET SQL"}}',
            {},
            0,
        )

    monkeypatch.setattr(gateway, "complete", invalid)
    turn = ask(client, url).json()["turns"][-1]
    assert turn["status"] == "failed" and turn["attempts"] == 2 and len(sent) == 2
    assert "SECRET SQL" not in sent[-1]
    assert client.post(url + f"/turns/{turn['id']}/execute").status_code == 409


def test_clarification_and_context_reset(assistant_env, monkeypatch):
    client, _, _, _, url, _ = assistant_env
    sent = []

    async def clarify(_config, messages, _schema):
        sent.append(json.loads(messages[1]["content"]))
        return '{"action":"clarify","message":"请补充日期范围"}', {}, 0

    monkeypatch.setattr(gateway, "complete", clarify)
    assert ask(client, url).json()["turns"][-1]["status"] == "clarification"
    ask(client, url, "本月")
    assert "销售额" in sent[-1]["question"] and "本月" in sent[-1]["question"]
    ask(client, url, "订单数", reset_context=True)
    assert sent[-1]["question"] == "订单数" and sent[-1]["previous_plan"] is None


def test_republish_expiration_and_owner_isolation(assistant_env):
    client, engine, actor, topic_url, url, _ = assistant_env
    ask(client, url)
    old_id = actor.id
    actor.id = uuid.uuid4()
    assert client.get(url).status_code == 404
    actor.id = old_id
    assert publish(client, topic_url).status_code == 201
    assert client.get(url).status_code == 409
    with Session(engine) as session:
        conversation = session.get(Conversation, uuid.UUID(url.split("/")[-1]))
        conversation.expires_at = now() - timedelta(seconds=1)
        session.add(conversation)
        session.commit()
    assert client.get(url).status_code == 410
    with Session(engine) as session:
        assert not session.exec(select(AssistantTurn)).one().encrypted_payload


@pytest.mark.parametrize("provider", ["zhipu", "deepseek", "qwen", "custom"])
def test_gateway_http_contract(provider, env, monkeypatch):
    client, engine, _ = env
    config = client.post(BASE + "/gateways", json=CONFIG).json()
    with Session(engine) as session:
        record = session.get(ModelGateway, uuid.UUID(config["id"]))
        session.expunge(record)
    record.provider = provider
    record.thinking = "disabled"
    if provider == "custom":
        record.base_url = "https://approved.example/v1"
        monkeypatch.setattr(
            settings, "MODEL_GATEWAY_ALLOWED_BASE_URLS", [record.base_url]
        )
    else:
        record.base_url = next(
            p["base_url"] for p in gateway.PRESETS if p["provider"] == provider
        )
    captured = []

    def handle(request):
        captured.append(json.loads(request.content))
        assert request.headers["Authorization"] == "Bearer " + KEY
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"finish_reason": "stop", "message": {"content": '{"ok":true}'}}
                ],
                "usage": {"prompt_tokens": 5},
            },
        )

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(handle), **kwargs),
    )
    content, usage, _ = asyncio.run(
        gateway.complete(record, [{"role": "user", "content": "test json"}], {})
    )
    assert json.loads(content) == {"ok": True} and usage["prompt_tokens"] == 5
    assert captured[0]["response_format"] == {"type": "json_object"}
    assert "tools" not in captured[0]
    if provider == "qwen":
        assert captured[0]["enable_thinking"] is False
    else:
        assert captured[0]["thinking"] == {"type": "disabled"}


@pytest.mark.parametrize(
    "kind", ["http_error", "empty", "truncated", "invalid_json", "oversized", "timeout"]
)
def test_gateway_bad_responses_are_bounded_and_sanitized(env, monkeypatch, kind):
    client, engine, _ = env
    config_id = client.post(BASE + "/gateways", json=CONFIG).json()["id"]
    with Session(engine) as session:
        config = session.get(ModelGateway, uuid.UUID(config_id))
        session.expunge(config)

    def handle(_request):
        if kind == "timeout":
            raise httpx.ReadTimeout(KEY)
        if kind == "http_error":
            return httpx.Response(401, text=KEY)
        if kind == "invalid_json":
            return httpx.Response(200, text=KEY)
        if kind == "oversized":
            return httpx.Response(200, text="x" * 256001)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": "length" if kind == "truncated" else "stop",
                        "message": {"content": ""},
                    }
                ]
            },
        )

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(handle), **kwargs),
    )
    with pytest.raises(HTTPException) as error:
        asyncio.run(gateway.complete(config, [], {}))
    assert KEY not in str(error.value.detail)


def test_permission_revoked_during_model_generation(assistant_env, monkeypatch):
    from app.models import User

    client, engine, actor, _, url, _ = assistant_env

    async def revoke(_config, _messages, _schema):
        with Session(engine) as session:
            user = session.get(User, actor.id)
            user.is_active = False
            session.add(user)
            session.commit()
        return '{"action":"plan","plan":{"metrics":["revenue"]}}', {}, 0

    monkeypatch.setattr(gateway, "complete", revoke)
    assert ask(client, url).status_code == 403
    with Session(engine) as session:
        turn = session.exec(select(AssistantTurn)).one()
        assert turn.status == "failed"
        assert "plan" not in json.loads(decrypt_password(turn.encrypted_payload))
        assert not session.exec(select(QueryJob)).all()


def test_context_latest_turn_and_gateway_deletion(assistant_env):
    client, _, _, _, url, _ = assistant_env
    first = ask(client, url).json()["turns"][-1]
    ask(client, url, "订单数")
    assert client.post(url + f"/turns/{first['id']}/execute").status_code == 409
    config = client.get(BASE + "/gateways").json()[0]
    path = BASE + f"/gateways/{config['id']}"
    assert (
        client.request("DELETE", path, json={"expected_revision": 1}).status_code == 409
    )
    client.post(BASE + "/gateways/deactivate")
    assert (
        client.request("DELETE", path, json={"expected_revision": 1}).status_code == 200
    )
    assert not client.get(BASE + "/gateways").json()


def test_signed_invalid_subject_rejected(env):
    import jwt

    from app.api.deps import get_current_user
    from app.core import security

    _, engine, _ = env
    token = jwt.encode(
        {"sub": "not-a-uuid"}, settings.SECRET_KEY, algorithm=security.ALGORITHM
    )
    with Session(engine) as session, pytest.raises(HTTPException) as error:
        get_current_user(session, token)
    assert error.value.status_code == 401
