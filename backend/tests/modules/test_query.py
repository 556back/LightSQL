import uuid
from datetime import timedelta
from decimal import Decimal

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlmodel import Session, select

from app.models import User
from app.modules.catalog.models import CatalogState, ColumnMeta
from app.modules.datasources.models import now
from app.modules.query import executor, service, worker
from app.modules.query.compiler import compile_plan, typed_value
from app.modules.query.models import QueryEvent, QueryGrant, QueryJob, QueryPlan
from app.modules.semantic.models import SemanticDefinition, TopicMember
from tests.modules.test_semantic import (  # noqa: F401
    TABLES,
    definition,
    publish,
    topic_env,
)


def compile_query(plan=None, kind="postgresql", grant=None, data=None):
    return compile_plan(
        SemanticDefinition.model_validate(data or definition()),
        TABLES,
        kind,
        QueryPlan.model_validate(
            plan
            or {
                "metrics": ["revenue", "orders_count", "avg_order"],
                "dimensions": [{"dimension_id": "region"}],
            }
        ),
        grant,
    )


@pytest.mark.parametrize(
    "kind", ["postgresql", "mysql", "oracle", "dameng", "kingbase"]
)
def test_compiler_binding_composite_join_ratio_and_row_scope(kind):
    grant = QueryGrant(
        user_id=uuid.uuid4(),
        metric_ids=["revenue", "orders_count", "avg_order"],
        dimension_ids=["region"],
        rows=[{"model_id": "orders", "column": "tenant_id", "values": ["1"]}],
    )
    compiled = compile_query(kind=kind, grant=grant)
    assert "NULLIF" in compiled.sql and "JOIN" in compiled.sql
    assert "customer_id" in compiled.sql and "tenant_id" in compiled.sql
    assert "paid" not in compiled.sql
    values = (
        compiled.parameters
        if isinstance(compiled.parameters, tuple)
        else compiled.parameters.values()
    )
    assert Decimal(1) in values and "paid" in values
    assert compiled.sql.index("WHERE") < compiled.sql.index("JOIN")


def test_injection_values_remain_parameters_and_unknown_fields_rejected():
    payload = "private' OR 1=1; DROP TABLE sales.orders --"
    result = compile_query(
        {
            "metrics": ["revenue"],
            "filters": [
                {"dimension_id": "channel", "operator": "eq", "values": [payload]}
            ],
        }
    )
    assert payload not in result.sql and payload in result.parameters.values()
    for key in ("sql", "source_id", "semantic_version", "policy_fingerprint", "rows"):
        with pytest.raises(ValidationError):
            QueryPlan.model_validate({"metrics": ["revenue"], key: "malicious"})


@pytest.mark.parametrize(
    "patch",
    [
        {"metrics": ["unknown"]},
        {"metrics": ["revenue", "revenue"]},
        {"dimensions": [{"dimension_id": "status"}]},
        {"dimensions": [{"dimension_id": "channel", "grain": "month"}]},
        {"order_by": [{"field": "not_selected"}]},
        {"filters": [{"dimension_id": "channel", "operator": "gt", "values": ["A"]}]},
        {
            "filters": [
                {"dimension_id": "channel", "operator": "is_null", "values": ["A"]}
            ]
        },
        {"filters": [{"dimension_id": "channel", "operator": "in", "values": []}]},
        {"time_range": {"start": "2026-09-10", "end": "2026-09-01"}},
    ],
)
def test_invalid_semantic_plans_fail_closed(patch):
    with pytest.raises(HTTPException):
        compile_query({"metrics": ["revenue"], **patch})


def test_metric_compatibility_and_semi_additivity():
    data = definition()
    data["metrics"][1]["filter_ids"] = []
    with pytest.raises(HTTPException):
        compile_query(data=data)
    data = definition()
    data["metrics"][0].update(
        additivity="semi_additive", non_additive_dimensions=["day"]
    )
    with pytest.raises(HTTPException):
        compile_query({"metrics": ["revenue"]}, data=data)


def test_datetime_timezone_and_numeric_validation():
    timestamp = ColumnMeta(
        name="created",
        ordinal=1,
        data_type="timestamp without time zone",
        nullable=False,
    )
    assert (
        typed_value("2026-09-01T00:00:00+08:00", timestamp, semantics="utc").isoformat()
        == "2026-08-31T16:00:00"
    )
    with pytest.raises(HTTPException):
        typed_value("2026-09-01T00:00:00", timestamp)
    for value in ("NaN", "1e999", "1.5"):
        with pytest.raises(HTTPException):
            typed_value(
                value,
                ColumnMeta(name="id", ordinal=1, data_type="integer", nullable=False),
            )


@pytest.mark.parametrize(
    "kind,format_fragment",
    [
        ("postgresql", "YYYY-MM"),
        ("kingbase", "YYYY-MM"),
        ("mysql", "%%Y-%%m"),
        ("oracle", "YYYY-MM"),
        ("dameng", "YYYY-MM"),
    ],
)
def test_month_format_is_transpiled_before_driver_percent_escaping(
    kind, format_fragment
):
    compiled = compile_query(
        {
            "metrics": ["revenue"],
            "dimensions": [{"dimension_id": "day", "grain": "month"}],
        },
        kind=kind,
    )
    assert format_fragment in compiled.sql
    assert "%YYYY" not in compiled.sql


def test_policy_column_type_change_revokes_even_nonsemantic_column(query_env):
    import copy

    client, engine, _, source, _, topic_id = query_env
    member, _ = member_setup(query_env)
    # Row policy fields must retain their type even when no selected dimension
    # exposes them. This also protects future non-semantic organization fields.
    with Session(engine) as session:
        state = session.get(CatalogState, uuid.UUID(source["id"]))
        snapshot = copy.deepcopy(state.snapshot)
        for column in snapshot[0]["columns"]:
            if column["name"] == "tenant_id":
                column["data_type"] = "bigint"
        state.snapshot = snapshot
        session.add(state)
        session.commit()
    use_user(member)
    assert submit(client, topic_id).status_code in (403, 409)


@pytest.fixture
def query_env(topic_env):  # noqa: F811 - imported pytest fixture
    client, engine, actor, source, topic_url = topic_env
    assert publish(client, topic_url).status_code == 201
    topic_id = topic_url.rsplit("/", 1)[-1]
    return client, engine, actor, source, topic_url, topic_id


def submit(client, topic_id, request_id=None, plan=None):
    return client.post(
        "/api/v1/queries/",
        json={
            "topic_id": topic_id,
            "request_id": request_id or str(uuid.uuid4()),
            "plan": plan or {"metrics": ["revenue"]},
        },
    )


def test_submission_idempotency_quota_cancel_and_audit(query_env):
    client, engine, _, _, _, topic_id = query_env
    request_id = str(uuid.uuid4())
    first = submit(client, topic_id, request_id)
    assert first.status_code == 202, first.text
    assert submit(client, topic_id, request_id).json()["id"] == first.json()["id"]
    assert (
        submit(client, topic_id, request_id, {"metrics": ["orders_count"]}).status_code
        == 409
    )
    assert submit(client, topic_id).status_code == 202
    assert submit(client, topic_id).status_code == 202
    assert submit(client, topic_id).status_code == 429
    job_id = first.json()["id"]
    assert (
        client.post(f"/api/v1/queries/{job_id}/cancel").json()["status"] == "cancelled"
    )
    assert submit(client, topic_id).status_code == 202
    with Session(engine) as session:
        assert session.exec(
            select(QueryEvent).where(QueryEvent.action == "cancel_requested")
        ).all()


def member_setup(query_env):
    client, engine, actor, _, _, topic_id = query_env
    member = User(email="query-member@example.com", hashed_password="unused")
    with Session(engine) as session:
        session.add(member)
        session.add(TopicMember(topic_id=uuid.UUID(topic_id), user_id=member.id))
        session.commit()
        session.refresh(member)
    grant = {
        "user_id": str(member.id),
        "metric_ids": ["revenue"],
        "dimension_ids": ["region", "day"],
        "rows": [{"model_id": "orders", "column": "tenant_id", "values": ["1"]}],
    }
    policy = client.put(
        f"/api/v1/queries/topics/{topic_id}/policy",
        json={"expected_revision": 0, "grants": [grant]},
    )
    assert policy.status_code == 200, policy.text
    return member, grant


def use_user(user):
    from app.api.deps import get_current_user
    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: user


def test_member_metric_dimension_row_policy_and_result_revocation(query_env):
    client, engine, actor, _, _, topic_id = query_env
    member, grant = member_setup(query_env)
    use_user(member)
    assert (
        submit(client, topic_id, plan={"metrics": ["orders_count"]}).status_code == 403
    )
    assert (
        submit(
            client,
            topic_id,
            plan={"metrics": ["revenue"], "dimensions": [{"dimension_id": "channel"}]},
        ).status_code
        == 403
    )
    first = submit(client, topic_id)
    assert first.status_code == 202 and first.json()["sql"] is None
    job_id = first.json()["id"]
    with Session(engine) as session:
        job = session.get(QueryJob, uuid.UUID(job_id))
        job.status = "succeeded"
        job.result = {"columns": [], "rows": [], "truncated": False, "notes": []}
        session.add(job)
        session.commit()
    assert client.get(f"/api/v1/queries/{job_id}/result").status_code == 200
    use_user(actor)
    assert client.get(f"/api/v1/queries/{job_id}/result").status_code == 404
    assert (
        client.put(
            f"/api/v1/queries/topics/{topic_id}/policy",
            json={"expected_revision": 1, "grants": []},
        ).status_code
        == 200
    )
    use_user(member)
    assert client.get(f"/api/v1/queries/{job_id}/result").status_code == 403
    assert client.get("/api/v1/queries/audit").status_code == 403


def test_policy_validation_missing_root_and_optimistic_revision(query_env):
    client, _, _, _, _, topic_id = query_env
    member, grant = member_setup(query_env)
    for rows in (
        [],
        [{"model_id": "customers", "column": "tenant_id", "values": ["1"]}],
        [{"model_id": "orders", "column": "bad", "values": ["1"]}],
    ):
        response = client.put(
            f"/api/v1/queries/topics/{topic_id}/policy",
            json={"expected_revision": 1, "grants": [{**grant, "rows": rows}]},
        )
        assert response.status_code == 422
    assert (
        client.put(
            f"/api/v1/queries/topics/{topic_id}/policy",
            json={"expected_revision": 0, "grants": [grant]},
        ).status_code
        == 409
    )


def test_republish_and_catalog_changes_block_execution(query_env):
    client, engine, _, source, url, topic_id = query_env
    job = submit(client, topic_id).json()
    assert publish(client, url).status_code == 201
    with Session(engine) as session:
        with pytest.raises(HTTPException):
            service.recheck(session, session.get(QueryJob, uuid.UUID(job["id"])))
        state = session.get(CatalogState, uuid.UUID(source["id"]))
        state.revision += 1
        session.add(state)
        session.commit()
    assert submit(client, topic_id).status_code == 409


def test_expired_lease_blocks_source_and_requires_audited_cleanup(query_env):
    client, engine, _, _, _, topic_id = query_env
    first = submit(client, topic_id).json()
    claimed = worker.claim(engine)
    assert claimed[0] == uuid.UUID(first["id"])
    assert worker.claim(engine) is None
    with Session(engine) as session:
        job = session.get(QueryJob, claimed[0])
        job.lease_until = now() - timedelta(seconds=1)
        session.add(job)
        session.commit()
    assert worker.claim(engine) is None
    assert submit(client, topic_id).status_code == 409
    response = client.post(
        f"/api/v1/queries/{first['id']}/confirm-cleanup",
        json={"note": "DBA 已确认测试源中的查询会话结束"},
    )
    assert response.status_code == 200
    assert submit(client, topic_id).status_code == 202


def test_decimal_dates_null_and_payload_limits():
    assert (
        executor.serialize_cell(Decimal("9007199254740993.01")) == "9007199254740993.01"
    )
    assert executor.serialize_cell(None) is None
    assert executor.serialize_cell(True) is True
    with pytest.raises(ValueError):
        executor.serialize_cell("中" * 6000)


@pytest.mark.parametrize("rollback_fails", [False, True])
def test_executor_byte_limit_and_uncertain_cleanup(monkeypatch, rollback_fails):
    import threading

    from app.modules.datasources.models import DataSourceInput
    from app.modules.query.compiler import CompiledQuery
    from app.modules.query.models import ResultColumn
    from tests.modules.test_datasources import BODY

    class Cursor:
        description = [("value",)]
        rows = iter([("one",), ("two",), ("three",)])

        def execute(self, *_args):
            return self

        def fetchone(self):
            return next(self.rows, None)

    class Connection:
        def cursor(self):
            return Cursor()

        def rollback(self):
            if rollback_fails:
                raise OSError("simulated network interruption")

        def close(self):
            pass

    monkeypatch.setattr(executor, "open_connection", lambda *_: Connection())
    result = executor.execute(
        DataSourceInput.model_validate(
            {k: v for k, v in BODY.items() if k != "password"}
        ),
        "unused",
        CompiledQuery(
            "SELECT value",
            {},
            [ResultColumn(id="value", label="值", value_type="string")],
            [],
        ),
        QueryPlan(metrics=["revenue"]),
        threading.Event(),
        max_bytes=8,
    )
    if rollback_fails:
        assert result["status"] == "cleanup_pending" and "result" not in result
    else:
        assert (
            result["status"] == "succeeded"
            and result["row_count"] == 1
            and result["truncated"]
        )


def test_expired_result_is_inaccessible_and_purged(query_env):
    client, engine, _, _, _, topic_id = query_env
    first = submit(client, topic_id).json()
    with Session(engine) as session:
        job = session.get(QueryJob, uuid.UUID(first["id"]))
        job.status = "succeeded"
        job.expires_at = now() - timedelta(seconds=1)
        job.result = {"private": "expired"}
        session.add(job)
        session.commit()
    assert client.get(f"/api/v1/queries/{first['id']}/result").status_code == 410
    worker.claim(engine)
    with Session(engine) as session:
        job = session.get(QueryJob, uuid.UUID(first["id"]))
        assert job.result is None and job.plan == {} and job.sql_text == ""
