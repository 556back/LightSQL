"""Synthetic three-database correctness and shared-query-capacity acceptance.

Reads only existing local M02/M04 business fixtures. Creates a fresh PostgreSQL
metadata database; never changes the main demo's topics, users or model gateway.
No model calls. Retains the isolated database and JSON report for inspection.
"""

import argparse
import json
import math
import multiprocessing
import os
import platform
import threading
import time
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path

from module1_demo import LOCAL, configure
from module4_demo import cross_definition


def cases():
    def case(name, metrics, rows, **plan):
        return {"id": name, "plan": {"metrics": metrics, **plan}, "expected": rows}

    def filtered(name, operator, values, amount, count, dimension="tenant"):
        return case(
            name,
            ["amount", "orders_count"],
            [[amount, count]],
            filters=[
                {"dimension_id": dimension, "operator": operator, "values": values}
            ],
        )

    return [
        case("decimal_sum", ["amount"], [["3500.60"]]),
        case("count_rows_including_null", ["orders_count"], [["4"]]),
        case(
            "count_non_null",
            ["orders_count"],
            [["3"]],
            filters=[
                {"dimension_id": "value", "operator": "is_not_null", "values": []}
            ],
        ),
        case("average_non_null", ["mean"], [["1166.8666666667"]]),
        case("minimum", ["minimum"], [["800.20"]]),
        case("maximum", ["maximum"], [["1500.30"]]),
        case("distinct_tenants", ["tenants"], [["2"]]),
        case("ratio_includes_null_order", ["average"], [["875.15"]]),
        case(
            "composite_join",
            ["amount", "orders_count"],
            [
                ["华东示例客户", "1200.10", "2"],
                ["华南示例客户", "800.20", "1"],
                ["华北示例客户", "1500.30", "1"],
            ],
            dimensions=[{"dimension_id": "customer"}],
        ),
        case(
            "tenant_groups",
            ["amount"],
            [["1", "2000.30"], ["2", "1500.30"]],
            dimensions=[{"dimension_id": "tenant"}],
        ),
        filtered("tenant_eq", "eq", ["1"], "2000.30", "3"),
        filtered("tenant_in", "in", ["1", "2"], "3500.60", "4"),
        filtered("greater_than", "gt", ["1"], "1500.30", "1"),
        filtered("greater_equal", "gte", ["2"], "1500.30", "1"),
        filtered("less_than", "lt", ["2"], "2000.30", "3"),
        filtered("less_equal", "lte", ["1"], "2000.30", "3"),
        filtered("half_open_range", "between", ["1", "2"], "2000.30", "3"),
        filtered("null_amount", "is_null", [], None, "1", "value"),
        filtered("non_null_amount", "is_not_null", [], "3500.60", "3", "value"),
        case(
            "empty_aggregate_zero_denominator",
            ["amount", "orders_count", "average"],
            [[None, "0", None]],
            filters=[{"dimension_id": "tenant", "operator": "eq", "values": ["999"]}],
        ),
        case(
            "empty_grouped",
            ["amount"],
            [],
            dimensions=[{"dimension_id": "customer"}],
            filters=[{"dimension_id": "tenant", "operator": "eq", "values": ["999"]}],
        ),
        case(
            "top_one_truncation",
            ["amount"],
            [["华北示例客户", "1500.30"]],
            dimensions=[{"dimension_id": "customer"}],
            order_by=[{"field": "amount", "direction": "desc"}],
            limit=1,
        ),
        filtered(
            "chinese_parameter", "eq", ["华东示例客户"], "1200.10", "2", "customer"
        ),
        filtered("injection_as_value", "eq", ["x' OR 1=1 --"], None, "0", "customer"),
        {
            **case("tenant_row_grant", ["amount", "orders_count"], [["2000.30", "3"]]),
            "grant": True,
        },
    ]


def equivalent(rows, expected):
    def normalize(cell):
        if cell is None:
            return None
        try:
            return str(Decimal(str(cell)).quantize(Decimal("0.0001")))
        except ArithmeticError:
            return str(cell)

    return Counter(tuple(map(normalize, r)) for r in rows) == Counter(
        tuple(map(normalize, r)) for r in expected
    )


def definition_for(tables):
    from app.modules.semantic.models import SemanticDefinition

    definition = cross_definition(tables).model_dump(mode="json")
    orders = next(t for t in tables if t.name.lower() == "m02_orders")
    amount = next(c.name for c in orders.columns if c.name.lower() == "amount")
    tenant = next(c.name for c in orders.columns if c.name.lower() == "tenant_id")
    definition["dimensions"].append(
        {
            "id": "value",
            "label": "金额",
            "model_id": "orders",
            "column": amount,
            "value_type": "number",
        }
    )
    base = definition["metrics"][0]
    for name, agg, column in [
        ("mean", "avg", amount),
        ("minimum", "min", amount),
        ("maximum", "max", amount),
        ("tenants", "count_distinct", tenant),
    ]:
        definition["metrics"].append(
            {
                **base,
                "id": name,
                "label": name,
                "aggregation": agg,
                "column": column,
                "additivity": "non_additive",
            }
        )
    for metric in definition["metrics"]:
        metric["allowed_dimensions"] = ["customer", "tenant", "value"]
    return SemanticDefinition.model_validate(definition)


def fixtures():
    from sqlmodel import Session, select
    from app.core.db import engine
    from app.modules.catalog.models import CatalogState, TableMeta
    from app.modules.datasources.models import DataSource

    result = []
    for kind, port, database in [
        ("postgresql", 15432, "lightsql_demo"),
        ("mysql", 13306, "sales_demo"),
        ("oracle", 11521, "FREEPDB1"),
    ]:
        with Session(engine) as session:
            sources = session.exec(
                select(DataSource).where(DataSource.database_type == kind)
            ).all()
            source = next(
                s
                for s in sources
                if s.host == "127.0.0.1" and s.port == port and s.database == database
            )
            assert source.enabled and source.username.lower() == "light_reader"
            state = session.get(CatalogState, source.id)
            tables = [TableMeta.model_validate(t) for t in state.snapshot]
            result.append((source, state, tables, definition_for(tables)))
    return result


def matrix(fixtures):
    from app.modules.datasources.models import DataSourceInput
    from app.modules.datasources.service import decrypt_password
    from app.modules.query.compiler import compile_plan
    from app.modules.query.executor import execute
    from app.modules.query.models import QueryGrant, QueryPlan
    from app.modules.semantic.validation import validate

    records = []
    for source, state, tables, definition in fixtures:
        assert validate(definition, source, state).valid
        tenant = next(d.column for d in definition.dimensions if d.id == "tenant")
        for case in cases():
            plan = QueryPlan.model_validate(case["plan"])
            grant = (
                QueryGrant(
                    user_id=uuid.uuid4(),
                    metric_ids=plan.metrics,
                    dimension_ids=[],
                    rows=[{"model_id": "orders", "column": tenant, "values": ["1"]}],
                )
                if case.get("grant")
                else None
            )
            outcome = execute(
                DataSourceInput.model_validate(source),
                decrypt_password(source.encrypted_password),
                compile_plan(definition, tables, source.database_type, plan, grant),
                plan,
                threading.Event(),
            )
            passed = outcome["status"] == "succeeded" and equivalent(
                outcome["result"]["rows"], case["expected"]
            )
            if case["id"] == "top_one_truncation":
                passed = passed and outcome.get("truncated") is True
            records.append(
                {
                    "database": source.database_type,
                    "case": case["id"],
                    "passed": passed,
                    "status": outcome["status"],
                    "elapsed_ms": outcome.get("elapsed_ms"),
                    "rows": outcome.get("result", {}).get("rows"),
                    "expected": case["expected"],
                }
            )
        print(
            source.database_type,
            sum(r["passed"] for r in records if r["database"] == source.database_type),
            "/ 25",
            flush=True,
        )
    return records


def worker_process(url, stop):
    from sqlmodel import create_engine
    from app.modules.query.worker import run_loop

    db = create_engine(url)
    try:
        run_loop(db, stop)
    finally:
        db.dispose()


def capacity(cfg, fixtures, timeout_seconds=15):
    import psycopg
    from psycopg import sql
    from sqlmodel import Session, SQLModel, create_engine, select
    from app.main import app  # noqa: F401 - register all metadata tables
    from app.api.routes.topics import publish_topic
    from app.core.config import settings
    from app.models import User
    from app.modules.catalog.models import CatalogState
    from app.modules.datasources.models import DataSource
    from app.modules.query.models import (
        QueryEvent,
        QueryGate,
        QueryJob,
        QuerySubmission,
    )
    from app.modules.query.service import submit, utc
    from app.modules.query.worker import claim
    from app.modules.semantic.models import PublishRequest, Topic

    name = "lightsql_capacity_" + uuid.uuid4().hex
    with (LOCAL / "module7-capacity-databases.jsonl").open(
        "a", encoding="utf-8"
    ) as manifest:
        manifest.write(
            json.dumps({"database": name, "purpose": "isolated synthetic capacity"})
            + "\n"
        )
    with psycopg.connect(
        host="127.0.0.1",
        port=15432,
        user="postgres",
        password=cfg["pg_password"],
        dbname="lightsql_demo",
        autocommit=True,
    ) as conn:
        conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    db = create_engine(
        settings.DATABASE_URL.unicode_string().rsplit("/", 1)[0] + "/" + name,
        pool_size=15,
    )
    SQLModel.metadata.create_all(db)
    topics, users = [], []
    with Session(db) as session:
        session.add(QueryGate(id=1))
        for i in range(10):
            user = User(
                email=f"capacity-{i}@lightsql.example.com",
                hashed_password="disabled-fixture-login",
                is_superuser=True,
            )
            session.add(user)
            session.commit()
            users.append(user.id)
        for source, state, _, definition in fixtures:
            session.add(DataSource.model_validate(source.model_dump()))
            session.commit()
            session.add(CatalogState.model_validate(state.model_dump()))
            topic = Topic(
                name=source.database_type,
                name_key=source.database_type,
                source_id=source.id,
                draft=definition.model_dump(mode="json"),
            )
            session.add(topic)
            session.commit()
            publish_topic(
                topic.id,
                PublishRequest(
                    expected_revision=1, note="M07 isolated synthetic capacity"
                ),
                session,
                session.get(User, users[0]),
            )
            topics.append(topic.id)
    assignments = [0, 0, 1, 1, 2, 2, 0, 1, 2, 0]

    def enqueue(index):
        with Session(db) as session:
            return submit(
                session,
                session.get(User, users[index]),
                QuerySubmission(
                    topic_id=topics[assignments[index]],
                    request_id=uuid.uuid4(),
                    plan={
                        "metrics": ["amount", "orders_count"],
                        "timeout_seconds": timeout_seconds,
                    },
                ),
            ).id

    ids = [enqueue(i) for i in range(10)]
    # Independent transactions compete for the same PostgreSQL singleton lock.
    with ThreadPoolExecutor(max_workers=10) as pool:
        claimed = list(pool.map(lambda _: claim(db), range(10)))
    selected = [c for c in claimed if c is not None]
    assert len(selected) == 5 and len({c[0] for c in selected}) == 5
    with Session(db) as session:
        jobs = session.exec(select(QueryJob)).all()
        running = [j for j in jobs if j.status == "running"]
        assert max(Counter(j.source_id for j in running).values()) <= 2
        # No source execution has begun: reset only these test claims for the real run loop.
        for job in running:
            job.status, job.lease_token, job.lease_until, job.started_at = (
                "queued",
                None,
                None,
                None,
            )
            session.add(job)
        session.commit()
    ctx = multiprocessing.get_context("spawn")
    stop = ctx.Event()
    loops = [
        ctx.Process(
            target=worker_process,
            args=(db.url.render_as_string(hide_password=False), stop),
        )
        for _ in range(2)
    ]
    peak, peak_source, violations = 0, 0, []
    begin = time.monotonic()
    for loop in loops:
        loop.start()
    try:
        while time.monotonic() - begin < 60:
            with Session(db) as session:
                jobs = session.exec(select(QueryJob).where(QueryJob.id.in_(ids))).all()
                active = [
                    j
                    for j in jobs
                    if j.status in ("running", "cancelling", "cleanup_pending")
                ]
                sources = Counter(j.source_id for j in active)
                actors = Counter(j.actor_id for j in active)
                peak = max(peak, len(active))
                peak_source = max(peak_source, max(sources.values(), default=0))
                if (
                    len(active) > 5
                    or max(sources.values(), default=0) > 2
                    or max(actors.values(), default=0) > 1
                ):
                    violations.append("shared capacity exceeded")
                if all(
                    j.status not in ("queued", "running", "cancelling") for j in jobs
                ):
                    break
            time.sleep(0.05)
    finally:
        stop.set()
        for loop in loops:
            loop.join(timeout=50)
            if loop.is_alive():
                loop.terminate()
                loop.join(timeout=5)
                violations.append("worker did not drain before shutdown deadline")
    with Session(db) as session:
        jobs = session.exec(select(QueryJob).where(QueryJob.id.in_(ids))).all()
        phases = {}
        for record in session.exec(
            select(QueryEvent).where(QueryEvent.job_id.in_(ids))
        ).all():
            if record.detail.startswith("{"):
                phases[str(record.job_id)] = json.loads(record.detail)
        records = [
            {
                "id": str(j.id),
                "status": j.status,
                "correct": j.status == "succeeded"
                and equivalent(j.result["rows"], [["3500.60", "4"]]),
                "queue_ms": round(
                    (utc(j.started_at) - utc(j.created_at)).total_seconds() * 1000
                )
                if j.started_at
                else None,
                "execution_ms": j.elapsed_ms,
                "phases": phases.get(str(j.id), {}),
                "total_ms": round(
                    (utc(j.finished_at) - utc(j.created_at)).total_seconds() * 1000
                )
                if j.finished_at
                else None,
            }
            for j in jobs
        ]
    timings = sorted(r["total_ms"] for r in records if r["total_ms"] is not None)
    report = {
        "metadata_database": name,
        "evidence": "synthetic_query_pipeline_no_model",
        "workers": 2,
        "worker_processes": [loop.pid for loop in loops],
        "worker_exit_codes": [loop.exitcode for loop in loops],
        "requests": len(ids),
        "query_timeout_seconds": timeout_seconds,
        "claim_race": "10 contenders / 5 unique claims",
        "peak_active": peak,
        "peak_per_source": peak_source,
        "violations": violations,
        "jobs": records,
        "p50_ms": timings[math.ceil(len(timings) * 0.5) - 1] if timings else None,
        "p95_ms": timings[math.ceil(len(timings) * 0.95) - 1] if timings else None,
        "passed": peak == 5
        and not violations
        and all(r["correct"] for r in records)
        and all(loop.exitcode == 0 for loop in loops),
    }
    db.dispose()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout-seconds", type=int, choices=[15, 20, 30], default=15)
    parser.add_argument("--repeats", type=int, choices=range(1, 6), default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    path = (
        args.output.resolve()
        if args.output
        else LOCAL
        / f"module7-capacity-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}.json"
    )
    if path.exists():
        raise RuntimeError(
            "Choose a new output path; prior capacity evidence is preserved"
        )
    cfg = configure()
    data = fixtures()
    rows = matrix(data)
    report = {
        "provenance": "synthetic",
        "matrix": rows,
        "environment": {
            "platform": platform.system(),
            "python": platform.python_version(),
            "logical_cpus": os.cpu_count(),
        },
        "capacity_runs": [],
        "passed": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for index in range(args.repeats):
        run = capacity(cfg, data, args.timeout_seconds)
        report["capacity_runs"].append(run)
        report["capacity"] = run  # Retain the previous report's last-run interface.
        path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(
            json.dumps(
                {
                    "run": index + 1,
                    "passed": run["passed"],
                    "p95_ms": run["p95_ms"],
                    "statuses": dict(Counter(j["status"] for j in run["jobs"])),
                }
            ),
            flush=True,
        )
    report["passed"] = all(r["passed"] for r in rows) and all(
        r["passed"] for r in report["capacity_runs"]
    )
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "matrix_passed": sum(r["passed"] for r in rows),
                "runs": len(report["capacity_runs"]),
                "passed": report["passed"],
                "report": str(path),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
