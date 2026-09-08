"""Audit DuSQL and exercise LightSQL's real SQL compiler on the supplied dev set.

No model calls. SQLite snapshots preserve mixed cells with numeric affinity;
optional local PostgreSQL verification uses transaction-local temporary tables.
No source files, application settings, or existing database tables are changed.
"""

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
# The compiler imports application settings but needs no metadata connection.
# Use process-local dummy values so this runner also works outside backend/.
for key, value in {
    "PROJECT_NAME": "DuSQL compiler verification",
    "SECRET_KEY": "dusql-offline-compiler-test-only-key",
    "DATABASE_URL": "postgresql://unused:unused@127.0.0.1:1/unused",
    "FIRST_SUPERUSER": "dusql@example.com",
    "FIRST_SUPERUSER_PASSWORD": "DuSQL-offline-test-only!",
}.items():
    os.environ.setdefault(key, value)

import sqlglot  # noqa: E402
from fastapi import HTTPException  # noqa: E402
from sqlglot import exp  # noqa: E402
from sqlglot.optimizer.scope import traverse_scope  # noqa: E402

from app.modules.catalog.models import ColumnMeta, TableMeta  # noqa: E402
from app.modules.query.exploration import compile_sql  # noqa: E402
from app.modules.query.models import SqlPlan  # noqa: E402
from app.modules.semantic.models import SemanticDefinition  # noqa: E402


def quote(name):
    return '"' + name.replace('"', '""') + '"'


def numeric(value):
    if value is None:
        return True
    if isinstance(value, bool):
        return False
    try:
        return Decimal(str(value)).is_finite()
    except ArithmeticError:
        return False


def metadata(schema, content, namespace):
    tables, models, mixed = [], [], []
    for i, name in enumerate(schema["table_names_original"]):
        source = content["tables"][name]
        columns = []
        for j, (column, kind) in enumerate(
            zip(source["header"], source["type"], strict=True)
        ):
            values = [r[j] for r in source["cell"]]
            number = kind == "number" and all(numeric(v) for v in values)
            if kind == "number" and not number:
                mixed.append(
                    {
                        "table": name,
                        "column": column,
                        "examples": [v for v in values if not numeric(v)][:3],
                    }
                )
            columns.append(
                ColumnMeta(
                    name=column,
                    ordinal=j + 1,
                    data_type="numeric" if number else "text",
                    nullable=True,
                )
            )
        tables.append(
            TableMeta(schema_name=namespace, name=name, kind="table", columns=columns)
        )
        models.append(
            {
                "id": f"t{i}",
                "label": name,
                "relation": {"schema_name": namespace, "name": name, "kind": "table"},
                "grain": "DuSQL 原始快照中的一行",
            }
        )
    return SemanticDefinition(models=models), tables, mixed


def logical_query(tree, schema):
    """Map physical Chinese table names to legal logical IDs; retain aliases."""
    result = tree.copy()
    mapping = {name: f"t{i}" for i, name in enumerate(schema["table_names_original"])}
    for scope in traverse_scope(result):
        for source in scope.sources.values():
            if isinstance(source, exp.Table):
                if source.name not in mapping or source.db or source.catalog:
                    raise ValueError("Unknown source table")
                if not source.alias:
                    source.set(
                        "alias",
                        exp.TableAlias(
                            this=exp.to_identifier(source.name, quoted=True)
                        ),
                    )
                source.set("this", exp.to_identifier(mapping[source.name]))
    return result.sql(dialect="postgres", identify=True)


def same_rows(left, right, ordered):
    def cell(value):
        if value is None:
            return ("null", "")
        if isinstance(value, (int, float, Decimal)):
            # Explicit absolute tolerance for SQLite floating aggregate arithmetic.
            return ("number", str(Decimal(str(value)).quantize(Decimal("0.00000001"))))
        return ("text", str(value))

    a = [tuple(cell(c) for c in r) for r in left]
    b = [tuple(cell(c) for c in r) for r in right]
    return a == b if ordered else Counter(a) == Counter(b)


def query_sqlite(conn, sql, parameters=None):
    deadline = time.monotonic() + 3
    conn.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
    try:
        cursor = conn.execute(sql, parameters or {})
        rows = cursor.fetchmany(1002)
        if len(rows) > 1000:
            raise ValueError("Result exceeds comparison cap (1000)")
        return rows
    finally:
        conn.set_progress_handler(None, 0)


def compiled_sqlite(compiled, kind):
    sql = compiled.sql
    if kind != "oracle":
        sql = re.sub(r"%\((p\d+)\)s", r":\1", sql).replace("%%", "%")
    return sqlglot.transpile(
        sql,
        read={"postgresql": "postgres", "mysql": "mysql", "oracle": "oracle"}[kind],
        write="sqlite",
    )[0]


def pg_query(conn, sql, parameters=None):
    # Each failing reference query must not poison the surrounding fixture transaction.
    with conn.transaction():
        cursor = conn.execute(sql, parameters)
        rows = cursor.fetchmany(1002)
        if len(rows) > 1000:
            raise ValueError("Result exceeds comparison cap (1000)")
        return rows


def error(exc):
    return str(exc.detail if isinstance(exc, HTTPException) else exc).splitlines()[0][
        :400
    ]


def audit(directory):
    schemas = json.loads((directory / "db_schema.json").read_text(encoding="utf-8"))
    contents = json.loads((directory / "db_content.json").read_text(encoding="utf-8"))
    for schema in schemas:
        schema.setdefault("table_names_original", schema["table_names"])
        schema.setdefault("column_names_original", schema["column_names"])
    schema_by_id = {s["db_id"]: s for s in schemas}
    content_by_id = {s["db_id"]: s for s in contents}
    issues = []
    split_stats = {}
    selected = None
    for split in ("train", "dev", "test"):
        cases = json.loads((directory / f"{split}.json").read_text(encoding="utf-8"))
        ids = [c["question_id"] for c in cases]
        split_stats[split] = {
            "cases": len(cases),
            "databases": len({c["db_id"] for c in cases}),
            "with_reference_sql": sum(bool(c["query"]) for c in cases),
            "duplicate_question_ids": len(ids) - len(set(ids)),
        }
        for case in cases:
            if case["db_id"] not in schema_by_id or case["db_id"] not in content_by_id:
                issues.append(
                    {
                        "split": split,
                        "id": case["question_id"],
                        "error": "missing database",
                    }
                )
        if split == "dev":
            selected = cases
    for schema in schemas:
        for i, name in enumerate(schema["table_names_original"]):
            table = content_by_id[schema["db_id"]]["tables"][name]
            expected = [c for tid, c in schema["column_names_original"] if tid == i]
            if expected != table["header"]:
                issues.append(
                    {
                        "db_id": schema["db_id"],
                        "table": name,
                        "error": "schema/content column mismatch",
                    }
                )
            if any(len(r) != len(table["header"]) for r in table["cell"]):
                issues.append(
                    {
                        "db_id": schema["db_id"],
                        "table": name,
                        "error": "row width mismatch",
                    }
                )
    gold = {}
    for line in (directory / "gold_dev.sql").read_text(encoding="utf-8").splitlines():
        qid, sql, db = line.split("\t")
        gold[qid] = (sql, db)
    mismatches = [
        c["question_id"]
        for c in selected
        if gold.get(c["question_id"]) != (c["query"], c["db_id"])
    ]
    return (
        schema_by_id,
        content_by_id,
        selected,
        {
            "schemas": len(schemas),
            "contents": len(contents),
            "splits": split_stats,
            "issues": issues,
            "gold_dev_mismatches": mismatches,
            "sha256": {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(directory.glob("*"))
                if p.suffix in (".json", ".sql")
            },
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "docs/DuSQL")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--postgres-local", action="store_true")
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Smoke-test first N cases; zero runs all dev cases",
    )
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError("Choose a new output directory to retain previous evidence")
    schemas, contents, cases, inventory = audit(args.data)
    if args.limit:
        cases = cases[: args.limit]
    args.output.mkdir(parents=True)
    report = {
        "completed": False,
        "evidence": "reference_sql_compiler_regression",
        "model_calls": 0,
        "runtime": {
            "python": sys.version,
            "sqlglot": sqlglot.__version__,
            "sqlite": sqlite3.sqlite_version,
        },
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "inventory": inventory,
        "selected_dev_cases": len(cases),
        "sqlite_policy": "number columns use NUMERIC affinity; other cells remain text; no unit/percent/date cleanup; double-quoted string fallback disabled",
        "postgres_policy": "numeric only when every non-null cell is finite numeric; otherwise text; temporary tables rolled back",
        "comparison": "8 decimal places; ordered for top-level ORDER BY, otherwise duplicate-preserving multiset; no official DuSQL score",
        "cases": [],
        "mixed_numeric_columns": [],
    }
    grouped = defaultdict(list)
    for case in cases:
        grouped[case["db_id"]].append(case)
    cfg = (
        json.loads((ROOT / ".local/demo.json").read_text())
        if args.postgres_local
        else None
    )
    counts = Counter()
    started = time.monotonic()
    for db_id, group in grouped.items():
        schema, content = schemas[db_id], contents[db_id]
        definition, tables, mixed = metadata(schema, content, "main")
        report["mixed_numeric_columns"].extend({"db_id": db_id, **m} for m in mixed)
        conn = sqlite3.connect(":memory:")
        # SQLite's legacy double-quoted-string fallback would hide unknown fields.
        conn.setconfig(sqlite3.SQLITE_DBCONFIG_DQS_DML, False)
        conn.setconfig(sqlite3.SQLITE_DBCONFIG_DQS_DDL, False)
        pg = None
        try:
            if cfg:
                import psycopg

                pg = psycopg.connect(
                    host="127.0.0.1",
                    port=15432,
                    user="postgres",
                    password=cfg["pg_password"],
                    dbname="lightsql_demo",
                    connect_timeout=5,
                )
                pg.execute("SET LOCAL statement_timeout = '3s'")
                pg.execute("SET LOCAL search_path = pg_temp")
            for table in tables:
                source = content["tables"][table.name]
                columns = ", ".join(
                    quote(c) + (" NUMERIC" if t == "number" else " TEXT")
                    for c, t in zip(source["header"], source["type"], strict=True)
                )
                conn.execute(f"CREATE TABLE {quote(table.name)} ({columns})")
                conn.executemany(
                    f"INSERT INTO {quote(table.name)} VALUES ({','.join('?' for _ in source['header'])})",
                    source["cell"],
                )
                if pg:
                    columns = ", ".join(
                        quote(c.name) + " " + c.data_type for c in table.columns
                    )
                    pg.execute(
                        f"CREATE TEMP TABLE {quote(table.name)} ({columns}) ON COMMIT DROP"
                    )
                    with pg.cursor() as cursor:
                        rows = [
                            [None if v is None else str(v) for v in r]
                            for r in source["cell"]
                        ]
                        cursor.executemany(
                            f"INSERT INTO {quote(table.name)} VALUES ({','.join('%s' for _ in source['header'])})",
                            rows,
                        )
            # Allow only read operations on the SQLite fixture after import.
            conn.execute("PRAGMA query_only = ON")
            pg_definition, pg_tables, _ = metadata(schema, content, "pg_temp")
            for case in group:
                record = {
                    "id": case["question_id"],
                    "db_id": db_id,
                    "question": case["question"],
                    "reference_sql": case["query"],
                    "dialects": {},
                }
                try:
                    tree = sqlglot.parse_one(case["query"], read="mysql")
                    if not isinstance(tree, (exp.Select, exp.SetOperation)):
                        raise ValueError("Reference is not SELECT")
                    logical = logical_query(tree, schema)
                    record["logical_sql"] = logical
                    ordered = tree.args.get("order") is not None
                    record["ordered"] = ordered
                except Exception as exc:
                    record["parse_error"] = error(exc)
                    report["cases"].append(record)
                    counts["parse_error"] += 1
                    continue
                reference = None
                try:
                    reference = query_sqlite(
                        conn, tree.sql(dialect="sqlite", identify=True)
                    )
                    record["sqlite_reference_rows"] = reference
                    counts["sqlite_reference_ok"] += 1
                except Exception as exc:
                    record["sqlite_reference_error"] = error(exc)
                    counts["sqlite_reference_error"] += 1
                for kind in ("postgresql", "mysql", "oracle"):
                    outcome = {}
                    record["dialects"][kind] = outcome
                    try:
                        compiled = compile_sql(
                            definition, tables, kind, SqlPlan(sql=logical, limit=1000)
                        )
                        outcome["compiled"] = True
                        counts[kind + "_compiled"] += 1
                    except Exception as exc:
                        outcome["compile_error"] = error(exc)
                        counts[kind + "_compile_error"] += 1
                        continue
                    if reference is not None:
                        try:
                            rows = query_sqlite(
                                conn,
                                compiled_sqlite(compiled, kind),
                                compiled.parameters,
                            )
                            outcome["sqlite_match"] = same_rows(
                                reference, rows, ordered
                            )
                            counts[
                                kind
                                + (
                                    "_sqlite_match"
                                    if outcome["sqlite_match"]
                                    else "_sqlite_mismatch"
                                )
                            ] += 1
                            if not outcome["sqlite_match"]:
                                outcome["actual_rows"] = rows
                        except Exception as exc:
                            outcome["sqlite_error"] = error(exc)
                            counts[kind + "_sqlite_error"] += 1
                if pg:
                    try:
                        pg_reference = pg_query(
                            pg, tree.sql(dialect="postgres", identify=True)
                        )
                        record["postgres_reference_rows"] = pg_reference
                        counts["postgres_reference_ok"] += 1
                    except Exception as exc:
                        record["postgres_reference_error"] = error(exc)
                        counts["postgres_reference_error"] += 1
                    else:
                        try:
                            compiled = compile_sql(
                                pg_definition,
                                pg_tables,
                                "postgresql",
                                SqlPlan(sql=logical, limit=1000),
                            )
                            rows = pg_query(pg, compiled.sql, compiled.parameters)
                            record["postgres_match"] = same_rows(
                                pg_reference, rows, ordered
                            )
                            counts[
                                "postgres_match"
                                if record["postgres_match"]
                                else "postgres_mismatch"
                            ] += 1
                            if not record["postgres_match"]:
                                record["postgres_actual_rows"] = rows
                        except Exception as exc:
                            record["postgres_compiled_error"] = error(exc)
                            counts["postgres_compiled_error"] += 1
                report["cases"].append(record)
        finally:
            conn.close()
            if pg:
                pg.rollback()
                pg.close()
        print(
            json.dumps(
                {
                    "database": db_id,
                    "completed": len(report["cases"]),
                    "total": len(cases),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        report["counts"] = dict(counts)
        report["completed"] = len(report["cases"]) == len(cases)
        report["elapsed_seconds"] = round(time.monotonic() - started, 2)
        (args.output / "report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
    print(
        json.dumps(
            {"counts": counts, "elapsed_seconds": report["elapsed_seconds"]},
            ensure_ascii=False,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
