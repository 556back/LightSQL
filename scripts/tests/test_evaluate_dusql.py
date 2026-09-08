"""Regression checks for benchmark scoring and fixture adaptation."""

import sqlite3
import sys
from pathlib import Path

import pytest
import sqlglot

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evaluate_dusql import (  # noqa: E402
    compiled_sqlite,
    logical_query,
    metadata,
    numeric,
    query_sqlite,
    same_rows,
)
from app.modules.query.exploration import compile_sql  # noqa: E402
from app.modules.query.models import SqlPlan  # noqa: E402


@pytest.mark.parametrize(
    "a,b,ordered,expected",
    [
        ([[1], [2]], [[2], [1]], False, True),
        ([[1], [2]], [[2], [1]], True, False),
        ([[1], [1]], [[1]], False, False),
        ([[None]], [["None"]], False, False),
        ([["12"]], [[12]], False, False),
        ([[0.1 + 0.2]], [[0.3]], False, True),
    ],
)
def test_result_comparison(a, b, ordered, expected):
    assert same_rows(a, b, ordered) is expected


def test_numeric_units_are_not_silently_cleaned():
    assert numeric("12.5")
    assert not numeric("12%")
    assert not numeric("12万")
    assert not numeric("NaN")


@pytest.mark.parametrize("kind", ["postgresql", "mysql", "oracle"])
def test_chinese_self_join_aliases_and_bound_literal(kind):
    schema = {"table_names_original": ["订单"]}
    content = {
        "tables": {
            "订单": {
                "header": ["编号", "渠道"],
                "type": ["number", "text"],
                "cell": [[1, "100%原表订单"], [2, "线下"]],
            }
        }
    }
    definition, tables, _ = metadata(schema, content, "main")
    tree = sqlglot.parse_one(
        "SELECT a.编号 FROM 订单 a JOIN 订单 b ON a.编号=b.编号 WHERE b.渠道='100%原表订单'",
        read="mysql",
    )
    logical = logical_query(tree, schema)
    compiled = compile_sql(definition, tables, kind, SqlPlan(sql=logical))
    assert "100%原表订单" in compiled.parameters.values()
    assert "100%原表订单" not in compiled.sql
    with sqlite3.connect(":memory:") as conn:
        conn.execute('CREATE TABLE "订单" ("编号" NUMERIC, "渠道" TEXT)')
        conn.executemany(
            'INSERT INTO "订单" VALUES (?, ?)', content["tables"]["订单"]["cell"]
        )
        assert query_sqlite(
            conn, compiled_sqlite(compiled, kind), compiled.parameters
        ) == [(1,)]


def test_result_cap_does_not_turn_partial_results_into_pass():
    with sqlite3.connect(":memory:") as conn:
        conn.execute("CREATE TABLE t (n INTEGER)")
        conn.executemany("INSERT INTO t VALUES (?)", [(i,) for i in range(1001)])
        with pytest.raises(ValueError, match="comparison cap"):
            query_sqlite(conn, "SELECT n FROM t")


def test_missing_quoted_field_is_an_error():
    with sqlite3.connect(":memory:") as conn:
        conn.setconfig(sqlite3.SQLITE_DBCONFIG_DQS_DML, False)
        conn.execute("CREATE TABLE t (n INTEGER)")
        with pytest.raises(sqlite3.OperationalError):
            query_sqlite(conn, 'SELECT "missing" FROM t')


def test_model_preview_contains_schema_but_no_database_cells():
    import json

    from evaluate_dusql_live import prepare_messages

    schema = {"table_names_original": ["订单"], "foreign_keys": []}
    content = {
        "tables": {
            "订单": {
                "header": ["渠道"],
                "type": ["text"],
                "cell": [["private-cell-marker"]],
            }
        }
    }
    _, _, _, messages = prepare_messages(schema, content, "查询渠道")
    serialized = json.dumps(messages, ensure_ascii=False)
    assert "private-cell-marker" not in serialized
    payload = json.loads(messages[1]["content"])
    assert payload["question"] == "查询渠道"
    assert payload["catalog"]["tables"][0]["columns"][0]["name"] == "渠道"
