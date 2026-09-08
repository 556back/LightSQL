import copy
import uuid

import pytest
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import User
from app.modules.catalog.models import CatalogState, ColumnMeta, TableMeta
from app.modules.datasources.models import DataSource
from app.modules.semantic.models import SemanticDefinition, SemanticRelease, TopicAudit
from app.modules.semantic.service import parse_definition
from app.modules.semantic.validation import validate
from tests.modules.test_datasources import create


def column(name, data_type="integer", pk=False):
    return ColumnMeta(
        name=name, ordinal=1, data_type=data_type, nullable=False, primary_key=pk
    )


TABLES = [
    TableMeta(
        schema_name="sales",
        name="orders",
        kind="table",
        columns=[
            column("id", pk=True),
            column("tenant_id"),
            column("customer_id"),
            column("amount", "numeric(12,2)"),
            column("order_date", "date"),
            column("channel", "text"),
            column("status", "text"),
        ],
    ),
    TableMeta(
        schema_name="sales",
        name="customers",
        kind="table",
        columns=[
            column("tenant_id", pk=True),
            column("customer_id", pk=True),
            column("region", "text"),
        ],
    ),
]


def definition():
    return SemanticDefinition.model_validate(
        {
            "owner": "经营管理部",
            "models": [
                {
                    "id": t.name,
                    "label": t.name,
                    "relation": {
                        "schema_name": t.schema_name,
                        "name": t.name,
                        "kind": t.kind,
                    },
                    "grain": "每行一个业务对象",
                    "primary_key": [c.name for c in t.columns if c.primary_key],
                }
                for t in TABLES
            ],
            "dimensions": [
                {
                    "id": "day",
                    "label": "订单日期",
                    "model_id": "orders",
                    "column": "order_date",
                    "value_type": "date",
                },
                {
                    "id": "channel",
                    "label": "渠道",
                    "model_id": "orders",
                    "column": "channel",
                    "value_type": "entity",
                },
                {
                    "id": "status",
                    "label": "状态",
                    "model_id": "orders",
                    "column": "status",
                    "value_type": "string",
                },
                {
                    "id": "region",
                    "label": "区域",
                    "model_id": "customers",
                    "column": "region",
                    "value_type": "string",
                },
            ],
            "metrics": [
                {
                    "id": "revenue",
                    "label": "销售额",
                    "model_id": "orders",
                    "aggregation": "sum",
                    "column": "amount",
                    "description": "已支付订单销售额",
                    "unit": "元",
                    "allowed_dimensions": ["day", "channel", "region"],
                    "filter_ids": ["paid"],
                    "time_dimension": "day",
                },
                {
                    "id": "orders_count",
                    "label": "订单数",
                    "model_id": "orders",
                    "aggregation": "count",
                    "description": "已支付订单行数",
                    "unit": "笔",
                    "allowed_dimensions": ["day", "channel", "region"],
                    "filter_ids": ["paid"],
                    "time_dimension": "day",
                },
                {
                    "id": "avg_order",
                    "label": "客单价",
                    "model_id": "orders",
                    "aggregation": "ratio",
                    "description": "销售额除以订单数，分母为零返回空",
                    "unit": "元/笔",
                    "allowed_dimensions": ["day", "channel", "region"],
                    "filter_ids": ["paid"],
                    "time_dimension": "day",
                    "additivity": "non_additive",
                    "numerator": "revenue",
                    "denominator": "orders_count",
                },
            ],
            "filters": [
                {
                    "id": "paid",
                    "label": "已支付",
                    "dimension_id": "status",
                    "operator": "eq",
                    "values": ["paid"],
                }
            ],
            "relations": [
                {
                    "id": "order_customer",
                    "label": "订单所属客户",
                    "from_model": "orders",
                    "to_model": "customers",
                    "from_columns": ["tenant_id", "customer_id"],
                    "to_columns": ["tenant_id", "customer_id"],
                    "description": "同一租户客户，多对一左连接",
                }
            ],
            "entities": [
                {
                    "id": "web",
                    "label": "线上直营",
                    "aliases": ["官网"],
                    "dimension_id": "channel",
                    "value": "private_channel_code",
                }
            ],
        }
    ).model_dump(mode="json")


@pytest.fixture
def topic_env(env):
    client, engine, actor = env
    source = create(client)
    with Session(engine) as session:
        session.add(actor)
        session.add(
            CatalogState(
                source_id=uuid.UUID(source["id"]),
                source_revision=1,
                revision=1,
                synced_scope_revision=1,
                version=1,
                scope=[
                    {"schema_name": t.schema_name, "name": t.name, "kind": t.kind}
                    for t in TABLES
                ],
                snapshot=[t.model_dump() for t in TABLES],
            )
        )
        session.commit()
        session.refresh(actor)
    topic = client.post(
        "/api/v1/topics/",
        json={"name": "经营分析", "source_id": source["id"], "owner": "经营管理部"},
    )
    assert topic.status_code == 201, topic.text
    url = f"/api/v1/topics/{topic.json()['id']}"
    assert save(client, url, definition()).status_code == 200
    return client, engine, actor, source, url


def save(client, url, data, **changes):
    current = client.get(url).json()
    return client.put(
        url + "/draft",
        json={
            "expected_revision": current["revision"],
            "name": current["name"],
            "description": current["description"],
            "enabled": current["enabled"],
            "definition": data,
            **changes,
        },
    )


def check(client, url):
    return client.post(
        url + "/validate",
        json={"expected_revision": client.get(url).json()["revision"]},
    )


def publish(client, url):
    return client.post(
        url + "/releases",
        json={
            "expected_revision": client.get(url).json()["revision"],
            "note": "测试发布",
        },
    )


def codes(report):
    return {i["code"] for i in report["issues"] if i["severity"] == "error"}


def test_publish_immutable_revision_and_restore(topic_env):
    client, engine, _, _, url = topic_env
    assert check(client, url).json()["valid"]
    revision = client.get(url).json()["revision"]
    first = publish(client, url)
    assert first.status_code == 201 and first.json()["version"] == 1
    assert (
        client.post(
            url + "/releases", json={"expected_revision": revision, "note": "旧版本"}
        ).status_code
        == 409
    )
    changed = definition()
    changed["metrics"][0]["label"] = "销售金额"
    assert save(client, url, changed).status_code == 200
    assert client.get(url + "/published").json()["metrics"][0]["label"] == "销售额"
    assert publish(client, url).json()["version"] == 2
    restored = client.post(
        url + "/releases/1/restore",
        json={"expected_revision": client.get(url).json()["revision"]},
    )
    assert restored.json()["current_version"] == 2
    assert restored.json()["definition"]["metrics"][0]["label"] == "销售额"
    assert client.get(url + "/published").json()["metrics"][0]["label"] == "销售金额"
    assert publish(client, url).json()["version"] == 3
    releases = client.get(url + "/releases").json()
    assert "修改指标：revenue" in releases[0]["changes"]
    with Session(engine) as session:
        rows = session.exec(
            select(SemanticRelease).order_by(SemanticRelease.version)
        ).all()
        assert [r.definition["metrics"][0]["label"] for r in rows] == [
            "销售额",
            "销售金额",
            "销售额",
        ]
        assert session.exec(
            select(TopicAudit).where(TopicAudit.action == "published")
        ).all()


@pytest.mark.parametrize(
    "change,expected",
    [
        ("type", "AGGREGATE_TYPE"),
        ("scope", "TABLE_UNAVAILABLE"),
        ("source", "SOURCE_DISABLED"),
        ("scope_revision", "CATALOG_NOT_READY"),
    ],
)
def test_publish_revalidates_latest_catalog_and_revocation(topic_env, change, expected):
    client, engine, _, source, url = topic_env
    assert publish(client, url).status_code == 201
    assert check(client, url).json()["valid"]
    with Session(engine) as session:
        state = session.get(CatalogState, uuid.UUID(source["id"]))
        if change == "type":
            snapshot = copy.deepcopy(state.snapshot)
            snapshot[0]["columns"][3]["data_type"] = "text"
            state.snapshot = snapshot
        elif change == "scope":
            state.scope = state.scope[1:]
        elif change == "scope_revision":
            state.revision += 1
        else:
            ds = session.get(DataSource, state.source_id)
            ds.enabled = False
            session.add(ds)
        session.add(state)
        session.commit()
    assert expected in codes(check(client, url).json())
    assert publish(client, url).status_code == 422
    assert client.get(url).json()["availability"] == "needs_review"
    assert client.get(url + "/published").status_code == 409


def test_binding_fingerprint_ignores_unrelated_change_but_tracks_used_column(topic_env):
    client, engine, _, source, url = topic_env
    assert publish(client, url).status_code == 201
    with Session(engine) as session:
        state = session.get(CatalogState, uuid.UUID(source["id"]))
        snapshot = copy.deepcopy(state.snapshot)
        snapshot[0]["comment"] = "目录注释更新"
        snapshot[0]["columns"].append(column("unused", "text").model_dump())
        state.snapshot, state.version = snapshot, state.version + 1
        session.add(state)
        session.commit()
    assert client.get(url + "/published").status_code == 200
    with Session(engine) as session:
        state = session.get(CatalogState, uuid.UUID(source["id"]))
        snapshot = copy.deepcopy(state.snapshot)
        snapshot[0]["columns"][3]["data_type"] = "numeric(18,4)"
        state.snapshot = snapshot
        session.add(state)
        session.commit()
    assert check(client, url).json()["valid"]
    assert client.get(url + "/published").status_code == 409
    assert publish(client, url).status_code == 201
    assert client.get(url + "/published").status_code == 200


@pytest.mark.parametrize(
    "change,expected",
    [
        ("partial", "JOIN_NOT_UNIQUE"),
        ("fanout", "FANOUT_JOIN"),
        ("ambiguous", "JOIN_PATH"),
        ("cycle", "JOIN_CYCLE"),
        ("one_to_one", "JOIN_NOT_ONE_TO_ONE"),
    ],
)
def test_join_correctness(topic_env, change, expected):
    client, _, _, _, url = topic_env
    data = definition()
    relation = data["relations"][0]
    if change == "partial":
        relation["from_columns"] = relation["to_columns"] = ["customer_id"]
    elif change == "fanout":
        relation["cardinality"] = "many_to_many"
    elif change == "ambiguous":
        data["relations"].append({**relation, "id": "second_path"})
    elif change == "cycle":
        data["relations"].append(
            {
                **relation,
                "id": "reverse",
                "from_model": "customers",
                "to_model": "orders",
            }
        )
    else:
        relation["cardinality"] = "one_to_one"
    assert save(client, url, data).status_code == 200
    assert expected in codes(check(client, url).json())
    assert publish(client, url).status_code == 422


@pytest.mark.parametrize(
    "change,expected",
    [
        ("ratio", "RATIO_GRAIN"),
        ("additive", "ADDITIVITY"),
        ("entity", "ENTITY_AMBIGUOUS"),
        ("alias", "AMBIGUOUS_ALIAS"),
        ("sensitive", "SENSITIVE_EGRESS"),
        ("interval", "FILTER_INTERVAL"),
        ("type", "FILTER_VALUE_TYPE"),
        ("unknown", "DIMENSION_MISSING"),
    ],
)
def test_semantic_business_rules(topic_env, change, expected):
    client, _, _, _, url = topic_env
    data = definition()
    if change == "ratio":
        data["metrics"][1]["filter_ids"] = []
    elif change == "additive":
        data["metrics"][2]["additivity"] = "additive"
    elif change == "entity":
        data["entities"].append(
            {**data["entities"][0], "id": "conflict", "value": "another_code"}
        )
    elif change == "alias":
        data["metrics"][0]["aliases"] = ["渠道"]
    elif change == "sensitive":
        data["dimensions"][0].update(sensitive=True, external_allowed=True)
    elif change in ("interval", "type"):
        data["filters"][0].update(
            dimension_id="day",
            operator="between",
            values=["2026-09-10", "2026-09-01"]
            if change == "interval"
            else ["yesterday", "tomorrow"],
        )
    else:
        data["metrics"][0]["allowed_dimensions"].append("missing")
    assert save(client, url, data).status_code == 200
    assert expected in codes(check(client, url).json())


def test_member_isolation_and_private_mappings(topic_env):
    client, engine, actor, _, url = topic_env
    member = User(email="analyst@example.com", hashed_password="unused")
    with Session(engine) as session:
        session.add(member)
        session.commit()
        session.refresh(member)
        member_id = member.id
    assert (
        client.put(
            url + "/members",
            json={
                "expected_revision": client.get(url).json()["revision"],
                "user_ids": [str(member_id)],
            },
        ).status_code
        == 200
    )
    assert publish(client, url).status_code == 201
    original_id = actor.id
    actor.id, actor.is_superuser = member_id, False
    published = client.get(url + "/published")
    assert published.status_code == 200
    assert all(
        token not in published.text
        for token in [
            "private_channel_code",
            "schema_name",
            "model_id",
            "primary_key",
            "column",
            "filter_ids",
        ]
    )
    assert len(client.get("/api/v1/topics/").json()) == 1
    assert client.get("/api/v1/topics/").json()[0]["source_id"] is None
    for method, suffix, body in [
        ("get", "", None),
        ("get", "/export", None),
        ("get", "/releases", None),
        ("post", "/validate", {"expected_revision": 1}),
        ("post", "/releases", {"expected_revision": 1, "note": "x"}),
        ("post", "/import", {"expected_revision": 1, "content": "{}"}),
        ("put", "/draft", {}),
        ("put", "/members", {"expected_revision": 1, "user_ids": []}),
        ("post", "/releases/1/restore", {"expected_revision": 1}),
        ("delete", "?expected_revision=1", None),
    ]:
        assert (
            client.request(
                method, url + suffix, **({"json": body} if body is not None else {})
            ).status_code
            == 403
        )
    actor.id, actor.is_superuser = original_id, True
    assert (
        client.put(
            url + "/members",
            json={
                "expected_revision": client.get(url).json()["revision"],
                "user_ids": [],
            },
        ).status_code
        == 200
    )
    actor.id, actor.is_superuser = member_id, False
    assert client.get(url + "/published").status_code == 404
    assert client.get("/api/v1/topics/").json() == []


def test_drafts_hidden_and_disabled_publication(topic_env):
    client, _, actor, _, url = topic_env
    rev = client.get(url).json()["revision"]
    assert (
        client.put(
            url + "/members",
            json={"expected_revision": rev, "user_ids": [str(actor.id)]},
        ).status_code
        == 200
    )
    actor.is_superuser = False
    assert client.get("/api/v1/topics/").json() == []
    assert client.get(url + "/published").status_code == 404
    actor.is_superuser = True
    assert publish(client, url).status_code == 201
    assert save(client, url, definition(), enabled=False).status_code == 200
    actor.is_superuser = False
    assert client.get("/api/v1/topics/").json() == []
    assert client.get(url + "/published").status_code == 404


def test_import_export_and_restricted_yaml(topic_env):
    client, _, _, _, url = topic_env
    for fmt in ("yaml", "json"):
        content = client.get(url + "/export?format=" + fmt).json()["content"]
        assert parse_definition(content).model_dump(mode="json") == definition()
        response = client.post(
            url + "/import",
            json={
                "expected_revision": client.get(url).json()["revision"],
                "content": content,
            },
        )
        assert response.status_code == 200
    for text in [
        '{"owner":"a","owner":"b"}',
        "owner: &a name\nmodels: *a",
        "!!python/object/apply:os.system ['echo forbidden']",
        "owner: name\nsql: select secret",
        "owner: a\ntimezone: invalid/timezone",
        "owner: " + "中" * 70000,
    ]:
        with pytest.raises(HTTPException) as raised:
            parse_definition(text)
        assert raised.value.status_code == 422


def test_referenced_source_and_published_topic_cannot_be_deleted(topic_env):
    client, _, _, source, url = topic_env
    ds_url = f"/api/v1/datasources/{source['id']}?expected_revision=1"
    assert client.delete(ds_url).status_code == 409
    assert publish(client, url).status_code == 201
    assert (
        client.delete(
            url + f"?expected_revision={client.get(url).json()['revision']}"
        ).status_code
        == 409
    )
    draft = client.post(
        "/api/v1/topics/",
        json={"name": "临时", "source_id": source["id"], "owner": "a"},
    ).json()
    assert (
        client.delete(f"/api/v1/topics/{draft['id']}?expected_revision=1").status_code
        == 200
    )


def test_physical_names_preserved_and_dameng_manual_join(topic_env):
    _, engine, _, source, _ = topic_env
    data = definition()
    with Session(engine) as session:
        state = session.get(CatalogState, uuid.UUID(source["id"]))
        snapshot = copy.deepcopy(state.snapshot)
        snapshot[0]["columns"][3]["name"] = " Amount "
        snapshot[1]["warnings"] = ["外键字典不可见"]
        state.snapshot = snapshot
        data["metrics"][0]["column"] = " Amount "
        model = SemanticDefinition.model_validate(data)
        assert model.metrics[0].column == " Amount "
        result = validate(model, session.get(DataSource, state.source_id), state)
        assert result.valid
        assert any(i.code == "CATALOG_WARNING" for i in result.issues)


def test_literal_values_preserved_and_numeric_alias_equivalence(topic_env):
    _, engine, _, source, _ = topic_env
    data = definition()
    data["entities"][0]["value"] = " online "
    data["filters"][0]["values"] = [" paid "]
    parsed = SemanticDefinition.model_validate(data)
    assert parsed.entities[0].value == " online "
    assert parsed.filters[0].values == [" paid "]
    data["dimensions"][1]["column"] = "customer_id"
    data["entities"][0]["value"] = "101.0"
    data["entities"].append(
        {**data["entities"][0], "id": "numeric_alias", "value": "101"}
    )
    with Session(engine) as session:
        state = session.get(CatalogState, uuid.UUID(source["id"]))
        assert validate(
            SemanticDefinition.model_validate(data),
            session.get(DataSource, state.source_id),
            state,
        ).valid
