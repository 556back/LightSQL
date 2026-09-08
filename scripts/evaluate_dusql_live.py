"""Bounded live DuSQL sample using the active gateway and production explore prompt.

One first PostgreSQL-verifiable question per dev database, at most 17 model calls.
No gold SQL/results or database cells are sent to the model. Temporary PostgreSQL
tables are rolled back. This is a component integration sample, not an API/worker
or official DuSQL benchmark. The reference eligibility filter biases the sample.
"""

import argparse
import asyncio
import json
import time
from collections import Counter
from datetime import date
from pathlib import Path

from evaluate_dusql import ROOT, audit, error, metadata, pg_query, quote, same_rows

import psycopg
from sqlalchemy import URL
from sqlmodel import Session, create_engine

from app.core.config import settings
from app.modules.assistant import context, gateway
from app.modules.assistant.models import PlanDecision
from app.modules.query.exploration import catalog, compile_sql


def prepare_messages(schema, content, question):
    definition, tables, _ = metadata(schema, content, "pg_temp")
    definition.external_allowed = True
    prepared = context.prepare(
        definition, None, question, None, {}, date(2026, 9, 7), allow_empty=True
    )
    prepared.catalog["tables"] = catalog(definition, tables, None)
    prepared.catalog["relations"] = []
    for i, (left, right) in enumerate(schema.get("foreign_keys", [])):
        lt, lc = schema["column_names_original"][left]
        rt, rc = schema["column_names_original"][right]
        prepared.catalog["relations"].append(
            {
                "id": f"r{i}",
                "label": "DuSQL 提供的字段关联，基数未验证",
                "from_model": f"t{lt}",
                "to_model": f"t{rt}",
                "from_columns": [lc],
                "to_columns": [rc],
                "cardinality": "many_to_many",
                "join_type": "inner",
            }
        )
    messages = [
        {"role": "system", "content": context.EXPLORATION_SYSTEM},
        {
            "role": "user",
            "content": json.dumps(
                {
                    "question": prepared.question,
                    "mode": "explore",
                    "catalog": prepared.catalog,
                    "previous_plan": None,
                    "reference_bindings": [],
                },
                ensure_ascii=False,
            ),
        },
    ]
    return definition, tables, prepared, messages


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError("Choose a new output path")
    reference = json.loads(args.reference_report.read_text(encoding="utf-8"))
    if not reference.get("completed"):
        raise RuntimeError("Reference verification must be complete")
    schemas, contents, _, inventory = audit(ROOT / "docs/DuSQL")
    if inventory["sha256"] != reference["inventory"]["sha256"]:
        raise RuntimeError("Dataset changed since reference verification")
    selected = {}
    for case in sorted(reference["cases"], key=lambda c: c["id"]):
        if case.get("postgres_match"):
            selected.setdefault(case["db_id"], case)
    if not 1 <= len(selected) <= 17:
        raise RuntimeError("This runner is limited to 1–17 preselected model calls")
    cfg = json.loads((ROOT / ".local/demo.json").read_text())
    settings.DATASOURCE_ENCRYPTION_KEY = cfg["encryption_key"]
    engine = create_engine(
        URL.create(
            "postgresql+psycopg",
            username="postgres",
            password=cfg["pg_password"],
            host="127.0.0.1",
            port=15432,
            database="lightsql_demo",
        )
    )
    with Session(engine) as session:
        config = gateway.active(session)
        session.expunge(config)
    if "fixture" in config.model or "replay" in config.model:
        raise RuntimeError("Active gateway is not a live model")
    report = {
        "completed": False,
        "evidence": "live_model_component_sample",
        "model": config.model,
        "gateway_id": str(config.id),
        "gateway_revision": config.revision,
        "selection": "first PostgreSQL-verifiable dev question per database, sorted by question_id",
        "selected": [{"db_id": c["db_id"], "id": c["id"]} for c in selected.values()],
        "prompt": "production EXPLORATION_SYSTEM + context.prepare + exploration.catalog + PlanDecision schema",
        "attempts_per_question": 1,
        "limitations": [
            "small filtered sample, not representative accuracy",
            "no API authentication/conversation/worker coverage",
            "reference data may not reflect intended question semantics",
        ],
        "dataset_sha256": inventory["sha256"],
        "cases": [],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for db_id, case in selected.items():
        with Session(engine) as session:
            active = gateway.active(session)
            if active.id != config.id or active.revision != config.revision:
                raise RuntimeError(
                    "Active gateway changed; stopped without switching settings"
                )
        definition, tables, prepared, messages = prepare_messages(
            schemas[db_id], contents[db_id], case["question"]
        )
        record = {
            "id": case["id"],
            "db_id": db_id,
            "question": case["question"],
            "status": "error",
        }
        started = time.monotonic()
        try:
            response, usage, elapsed = await gateway.complete(
                config, messages, PlanDecision.model_json_schema()
            )
            record.update(usage=usage, model_elapsed_ms=elapsed)
            decision = PlanDecision.model_validate_json(response)
            record["decision"] = decision.model_dump(mode="json")
            if decision.action != "plan":
                record["status"] = decision.action
            else:
                if decision.sql_plan is None or decision.plan is not None:
                    raise ValueError("Expected exactly one SQL plan")
                plan = context.materialize_sql(decision.sql_plan, prepared)
                compiled = compile_sql(definition, tables, "postgresql", plan)
                with psycopg.connect(
                    host="127.0.0.1",
                    port=15432,
                    user="postgres",
                    password=cfg["pg_password"],
                    dbname="lightsql_demo",
                    connect_timeout=5,
                ) as pg:
                    try:
                        pg.execute("SET LOCAL statement_timeout = '3s'")
                        pg.execute("SET LOCAL search_path = pg_temp")
                        for table in tables:
                            source = contents[db_id]["tables"][table.name]
                            columns = ", ".join(
                                quote(c.name) + " " + c.data_type for c in table.columns
                            )
                            pg.execute(
                                f"CREATE TEMP TABLE {quote(table.name)} ({columns}) ON COMMIT DROP"
                            )
                            with pg.cursor() as cursor:
                                cursor.executemany(
                                    f"INSERT INTO {quote(table.name)} VALUES ({','.join('%s' for _ in table.columns)})",
                                    [
                                        [None if v is None else str(v) for v in r]
                                        for r in source["cell"]
                                    ],
                                )
                        rows = pg_query(pg, compiled.sql, compiled.parameters)
                        # Re-execute the gold on exactly this transaction's snapshot;
                        # JSON serialization of NUMERIC must not erase type identity.
                        import sqlglot

                        gold = sqlglot.parse_one(
                            case["reference_sql"], read="mysql"
                        ).sql(dialect="postgres", identify=True)
                        expected = pg_query(pg, gold)
                        record["expected_rows"] = expected
                        record["actual_rows"] = rows
                        record["status"] = (
                            "match"
                            if same_rows(expected, rows, case["ordered"])
                            else "mismatch"
                        )
                    finally:
                        pg.rollback()
        except Exception as exc:
            record["error"] = error(exc)
        record["elapsed_ms"] = round((time.monotonic() - started) * 1000)
        report["cases"].append(record)
        report["completed"] = len(report["cases"]) == len(selected)
        report["counts"] = dict(Counter(c["status"] for c in report["cases"]))
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        print(
            json.dumps(
                {
                    "id": case["id"],
                    "status": record["status"],
                    "completed": len(report["cases"]),
                    "total": len(selected),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
    engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
