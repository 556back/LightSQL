import json
import uuid
from datetime import timedelta
from pathlib import Path

import pytest
from sqlmodel import Session

from app.modules.catalog import introspection, service
from app.modules.catalog.models import (
    CatalogState,
    ColumnMeta,
    ForeignKeyMeta,
    ObjectRef,
    SyncJob,
    TableMeta,
)
from app.modules.datasources.models import DataSourceInput, now
from tests.modules.test_datasources import (  # noqa: F401
    PASSWORD,
    create,
    update_body,
)

REFS = [
    ObjectRef(schema_name="sales", name=name, kind="table")
    for name in ("customers", "orders")
]
TABLES = [
    TableMeta(
        **REFS[0].model_dump(),
        columns=[
            ColumnMeta(
                name="id",
                ordinal=1,
                data_type="integer",
                nullable=False,
                primary_key=True,
            )
        ],
    ),
    TableMeta(
        **REFS[1].model_dump(),
        columns=[
            ColumnMeta(
                name="amount",
                ordinal=1,
                data_type="numeric(12,2)",
                nullable=True,
                comment="订单金额（元）",
            )
        ],
        foreign_keys=[
            ForeignKeyMeta(
                name="customer_fk",
                columns=["amount"],
                target_schema="sales",
                target_table="customers",
                target_columns=["id"],
            )
        ],
    ),
]


def setup_catalog(client):
    source = create(client)
    url = f"/api/v1/catalog/{source['id']}"
    response = client.put(
        url + "/scope",
        json={
            "expected_revision": 0,
            "expected_source_revision": 1,
            "objects": [r.model_dump() for r in REFS],
        },
    )
    assert response.status_code == 200, response.text
    return source, url


def complete(client, engine, url, monkeypatch, tables=None):
    monkeypatch.setattr(
        introspection,
        "read_snapshot",
        lambda *_: (
            tables if tables is not None else [t.model_copy(deep=True) for t in TABLES]
        ),
    )
    queued = client.post(url + "/sync")
    assert queued.status_code == 202, queued.text
    claimed = service.claim(engine)
    assert claimed
    service.run_job(engine, *claimed)
    return client.get(url + "/jobs").json()[0]


def test_scope_default_deny_validation_and_optimistic_lock(env):
    client, _, _ = env
    source = create(client)
    url = f"/api/v1/catalog/{source['id']}"
    assert client.get(url).json()["tables"] == []
    assert client.post(url + "/sync").status_code == 409
    body = {
        "expected_revision": 0,
        "expected_source_revision": 1,
        "objects": [REFS[0].model_dump()],
    }
    assert (
        client.put(
            url + "/scope", json={**body, "objects": body["objects"] * 2}
        ).status_code
        == 422
    )
    assert (
        client.put(url + "/scope", json={**body, "sql": "select *"}).status_code == 422
    )
    assert client.put(url + "/scope", json=body).status_code == 200
    assert client.put(url + "/scope", json=body).status_code == 409


def test_catalog_admin_required_for_every_endpoint(env):
    client, _, actor = env
    _, url = setup_catalog(client)
    actor.is_superuser = False
    responses = [
        client.get(url),
        client.get(url + "/schemas"),
        client.get(url + "/discover?schema_name=sales"),
        client.get(url + "/jobs"),
        client.post(url + "/sync"),
        client.put(
            url + "/scope",
            json={"expected_revision": 1, "expected_source_revision": 1, "objects": []},
        ),
    ]
    assert all(r.status_code == 403 for r in responses)


def test_queue_dedup_claim_once_and_successful_snapshot(env, monkeypatch):
    client, engine, _ = env
    _, url = setup_catalog(client)
    first = client.post(url + "/sync").json()
    assert client.post(url + "/sync").json()["id"] == first["id"]
    token = service.claim(engine)
    assert token and service.claim(engine) is None
    monkeypatch.setattr(introspection, "read_snapshot", lambda *_: TABLES)
    service.run_job(engine, *token)
    catalog = client.get(url).json()
    assert (
        catalog["version"] == 1
        and len(catalog["tables"]) == 2
        and not catalog["needs_sync"]
    )
    assert PASSWORD not in client.get(url + "/jobs").text
    assert client.get(url + "/jobs").json()[0]["status"] == "succeeded"


def test_revoked_objects_and_related_foreign_keys_hidden_immediately(env, monkeypatch):
    client, engine, _ = env
    _, url = setup_catalog(client)
    complete(client, engine, url, monkeypatch)
    response = client.put(
        url + "/scope",
        json={
            "expected_revision": 1,
            "expected_source_revision": 1,
            "objects": [REFS[1].model_dump()],
        },
    ).json()
    assert len(response["tables"]) == 1 and response["tables"][0]["foreign_keys"] == []
    assert response["needs_sync"]
    response = client.put(
        url + "/scope",
        json={"expected_revision": 2, "expected_source_revision": 1, "objects": []},
    ).json()
    assert response["tables"] == []


def test_failed_sync_keeps_snapshot_and_sanitizes_error(env, monkeypatch):
    client, engine, _ = env
    _, url = setup_catalog(client)
    complete(client, engine, url, monkeypatch)
    before = client.get(url).json()

    def fail(*_):
        raise RuntimeError(f"driver error password={PASSWORD}")

    monkeypatch.setattr(introspection, "read_snapshot", fail)
    client.post(url + "/sync")
    service.run_job(engine, *service.claim(engine))
    assert client.get(url).json() == before
    jobs = client.get(url + "/jobs")
    assert jobs.json()[0]["status"] == "failed" and PASSWORD not in jobs.text


@pytest.mark.parametrize("change", ["scope", "source", "delete"])
def test_racing_changes_discard_stale_worker_result(env, monkeypatch, change):
    client, engine, _ = env
    source, url = setup_catalog(client)

    def race(*_):
        if change == "scope":
            client.put(
                url + "/scope",
                json={
                    "expected_revision": 1,
                    "expected_source_revision": 1,
                    "objects": [],
                },
            )
        elif change == "source":
            client.put(
                f"/api/v1/datasources/{source['id']}",
                json=update_body(source, database="different"),
            )
        else:
            client.delete(f"/api/v1/datasources/{source['id']}?expected_revision=1")
        return TABLES

    monkeypatch.setattr(introspection, "read_snapshot", race)
    job = client.post(url + "/sync").json()
    service.run_job(engine, *service.claim(engine))
    with Session(engine) as session:
        assert session.get(SyncJob, uuid.UUID(job["id"])).status == "superseded"
        state = session.get(CatalogState, uuid.UUID(source["id"]))
        assert state is None or state.version == 0


def test_connection_changes_require_scope_reconfirmation(env, monkeypatch):
    client, engine, _ = env
    source, url = setup_catalog(client)
    complete(client, engine, url, monkeypatch)
    client.put(
        f"/api/v1/datasources/{source['id']}",
        json=update_body(source, database="different"),
    )
    assert client.get(url).json()["needs_confirmation"]
    assert client.get(url).json()["tables"] == []
    assert client.post(url + "/sync").status_code == 409
    refreshed = client.put(
        url + "/scope",
        json={
            "expected_revision": 1,
            "expected_source_revision": 2,
            "objects": [r.model_dump() for r in REFS],
        },
    ).json()
    assert refreshed["tables"] == [] and refreshed["needs_sync"]


def test_expired_worker_cannot_publish_and_retry_gets_new_job(env, monkeypatch):
    client, engine, _ = env
    _, url = setup_catalog(client)
    job = client.post(url + "/sync").json()
    token = service.claim(engine)
    with Session(engine) as session:
        row = session.get(SyncJob, uuid.UUID(job["id"]))
        row.lease_until = now() - timedelta(seconds=1)
        session.add(row)
        session.commit()
    assert client.get(url + "/jobs").json()[0]["status"] == "failed"
    monkeypatch.setattr(introspection, "read_snapshot", lambda *_: TABLES)
    service.run_job(engine, *token)
    assert client.get(url).json()["version"] == 0
    assert client.post(url + "/sync").json()["id"] != job["id"]


def test_diff_column_type_comment_keys_and_no_change(env, monkeypatch):
    client, engine, _ = env
    _, url = setup_catalog(client)
    complete(client, engine, url, monkeypatch)
    assert complete(client, engine, url, monkeypatch)["changes"] == []
    updated = [t.model_copy(deep=True) for t in TABLES]
    updated[1].columns[0].data_type = "numeric(16,4)"
    updated[1].columns[0].comment = "含税金额"
    updated[1].foreign_keys = []
    changes = complete(client, engine, url, monkeypatch, updated)["changes"]
    assert {c["detail"] for c in changes} == {"字段定义", "关联关系"}
    assert "numeric(16,4)" in json.dumps(changes)
    removed = complete(client, engine, url, monkeypatch, [])["changes"]
    assert len(removed) == 2 and all(c["action"] == "removed" for c in removed)


@pytest.mark.parametrize(
    "kind,port,database,schema",
    [
        ("postgresql", 15432, "lightsql_demo", "demo_sales"),
        ("mysql", 13306, "sales_demo", "sales_demo"),
        ("oracle", 11521, "FREEPDB1", "LIGHT_DEMO"),
        ("dameng", 15236, "LIGHT_DEMO", "LIGHT_DEMO"),
        ("kingbase", 15421, "sales_demo", "light_demo"),
    ],
)
@pytest.mark.usefixtures("env")
def test_five_real_catalogs(kind, port, database, schema):
    local = Path(__file__).resolve().parents[3] / ".local"
    if not (local / "module2-fixtures.json").exists():
        pytest.skip(
            "Run scripts/module2_demo.py seed in the isolated five-database demo"
        )
    cfg = json.loads((local / "demo.json").read_text(encoding="utf8"))
    password = cfg[
        "reader_password"
        if kind in ("postgresql", "mysql")
        else "domestic_reader_password"
    ]
    source = DataSourceInput(
        name="catalog-test",
        database_type=kind,
        host="127.0.0.1",
        port=port,
        database=database,
        username="LIGHT_READER" if kind in ("oracle", "dameng") else "light_reader",
        tls_mode="disable",
    )
    visible_schemas = introspection.schemas(source, password)
    assert schema in visible_schemas
    assert not {"sys_catalog", "sysmac", "pg_catalog", "information_schema"}.intersection(visible_schemas)
    assert introspection.discover(source, password, schema + "' OR 1=1 --") == []
    refs = [
        r
        for r in introspection.discover(source, password, schema)
        if r.name.lower().startswith("m02_")
    ]
    tables = introspection.read_snapshot(source, password, refs, lambda: None)
    assert len(tables) == 3 and sum(t.kind == "view" for t in tables) == 1
    orders = next(t for t in tables if t.name.lower() == "m02_orders")
    assert orders.comment == "销售订单 · 元数据验收"
    assert (
        next(c for c in orders.columns if c.name.lower() == "amount").comment
        == "订单金额（元）"
    )
    assert next(c for c in orders.columns if c.name.lower() == "id").primary_key
    customers = next(t for t in tables if t.name.lower() == "m02_customers")
    assert [c.name.lower() for c in customers.columns if c.primary_key] == [
        "tenant_id",
        "customer_id",
    ]
    if kind == "dameng":
        assert orders.warnings and "字段映射" in orders.warnings[0]
    else:
        assert len(orders.foreign_keys) == 1 and not orders.warnings
        key = orders.foreign_keys[0]
        assert [c.lower() for c in key.columns] == ["tenant_id", "customer_id"]
        assert [c.lower() for c in key.target_columns] == ["tenant_id", "customer_id"]
    order_only = [r for r in refs if r.name.lower() == "m02_orders"]
    restricted = introspection.read_snapshot(source, password, order_only, lambda: None)
    assert restricted[0].foreign_keys == []
