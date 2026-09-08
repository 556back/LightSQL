"""Build 120 explicitly synthetic sales questions, SQL and verified reference rows.

Uses an in-memory snapshot of the existing M03 five-order fixture. No connections,
model calls, main-environment configuration or business data are accessed.
"""

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

CUSTOMERS = [
    [1, 101, "华东示例客户", "华东"],
    [1, 102, "华南示例客户", "华南"],
    [2, 101, "华北示例客户", "华北"],
]
ORDERS = [
    [1, 1, 101, "2026-09-01", "online", "paid", 1200, 100],
    [2, 1, 102, "2026-09-01", "partner", "paid", 800, 0],
    [3, 2, 101, "2026-09-02", "store", "paid", 1500, 300],
    [4, 1, 101, "2026-09-03", "online", "cancelled", 600, 0],
    [5, 1, 102, "2026-09-03", "online", "paid", 900, 0],
]
METRICS = [
    ("gross_sales", "销售总额", "SUM(o.gross_amount)"),
    ("refund_amount", "退款金额", "SUM(o.refund_amount)"),
    ("net_sales", "净销售额", "SUM(o.net_amount)"),
    ("order_count", "支付订单数", "COUNT(*)"),
    ("avg_order", "客单价", "1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0)"),
]
# Keep related filters/rewrites in the same split, including across metrics.
CONTEXTS = [
    ("total", "dev", "全部日期、全部渠道和客户", None, None),
    ("day", "dev", "全部日期，按订单日期逐日分组", "order_day", None),
    ("range", "dev", "订单日期从2026-09-01（含）到2026-09-03（不含）", None, None),
    ("online", "dev", "全部日期，仅线上直营渠道", None, ("channel", "online")),
    ("partner", "dev", "全部日期，仅合作渠道", None, ("channel", "partner")),
    ("region", "blind", "全部日期，按客户区域分组", "region", None),
    ("channel", "blind", "全部日期，按销售渠道分组", "channel", None),
    (
        "top",
        "blind",
        "全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序",
        "customer",
        None,
    ),
    ("east", "blind", "全部日期，仅华东示例客户", None, ("customer", "华东示例客户")),
    ("south", "blind", "全部日期，仅华南示例客户", None, ("customer", "华南示例客户")),
]
NEGATIVE = [
    (
        "ambiguous-entity",
        "dev",
        "clarify",
        ["示例渠道的净销售额是多少？", "统计示例渠道对应的净销售额。"],
        ["entity", "ambiguity"],
    ),
    (
        "missing-metric",
        "dev",
        "clarify",
        ["帮我看看销售经营情况。", "经营怎么样，帮我查一下。"],
        ["ambiguity"],
    ),
    (
        "missing-period",
        "dev",
        "clarify",
        ["统计那段时间的净销售额。", "查询之前说的那个期间的净销售额。"],
        ["missing-period"],
    ),
    (
        "missing-basis",
        "dev",
        "clarify",
        [
            "查询销售额，但我还没确定要退款前还是退款后口径。",
            "销售金额该看哪个数？我没决定是否扣除退款。",
        ],
        ["definition"],
    ),
    (
        "missing-ranking",
        "dev",
        "clarify",
        [
            "找出表现最好的客户，我尚未确定按什么指标排序。",
            "哪些客户最好？我还没选评价指标。",
        ],
        ["ambiguity"],
    ),
    (
        "yoy",
        "blind",
        "unsupported",
        [
            "仅标准指标模式下计算净销售额同比增长率。",
            "使用标准指标计划给出净销售额同比增幅。",
        ],
        ["comparison"],
    ),
    (
        "mom",
        "blind",
        "unsupported",
        [
            "仅标准指标模式下计算净销售额环比增长率。",
            "使用标准指标计划给出净销售额环比增幅。",
        ],
        ["comparison"],
    ),
    (
        "profit",
        "blind",
        "unsupported",
        ["计算销售毛利，必须扣除商品成本。", "统计扣除商品成本后的销售毛利润。"],
        ["missing-data"],
    ),
    (
        "inventory",
        "blind",
        "unsupported",
        ["查询仓库当前库存数量。", "现在仓库还剩多少件商品？"],
        ["missing-data"],
    ),
    (
        "cross-source",
        "blind",
        "unsupported",
        [
            "把当前订单和另一个未接入数据源的收款流水关联核对。",
            "跨数据源联查销售订单与尚未接入的银行收款明细。",
        ],
        ["cross-source"],
    ),
]


def snapshot_connection():
    db = sqlite3.connect(":memory:")
    db.execute("ATTACH DATABASE ':memory:' AS demo_sales")
    db.executescript("""
        CREATE TABLE demo_sales.m03_customers (
            tenant_id INTEGER, customer_id INTEGER, customer_name TEXT, region TEXT,
            PRIMARY KEY (tenant_id, customer_id));
        CREATE TABLE demo_sales.m03_orders (
            id INTEGER PRIMARY KEY, tenant_id INTEGER, customer_id INTEGER,
            order_date DATE, channel TEXT, status TEXT, gross_amount REAL,
            refund_amount REAL, net_amount REAL GENERATED ALWAYS AS (gross_amount-refund_amount));
    """)
    db.executemany("INSERT INTO demo_sales.m03_customers VALUES (?,?,?,?)", CUSTOMERS)
    db.executemany("INSERT INTO demo_sales.m03_orders VALUES (?,?,?,?,?,?,?,?)", ORDERS)
    return db


def independent_rows(metric, context):
    """Decimal/grouping oracle independent of both SQL and production compiler."""
    key, _, _, dimension, filter_value = context
    customers = {(r[0], r[1]): r for r in CUSTOMERS}
    groups = defaultdict(list)
    for order in ORDERS:
        _, tenant, customer_id, day, channel, status, gross, refund = order
        customer = customers[(tenant, customer_id)]
        if status != "paid":
            continue
        values = {
            "order_day": day,
            "channel": channel,
            "customer": customer[2],
            "region": customer[3],
        }
        if key == "range" and not "2026-09-01" <= day < "2026-09-03":
            continue
        if filter_value and values[filter_value[0]] != filter_value[1]:
            continue
        groups[values[dimension] if dimension else None].append(
            (Decimal(gross), Decimal(refund))
        )
    result = []
    for group, values in groups.items():
        gross = sum(v[0] for v in values)
        refund = sum(v[1] for v in values)
        value = {
            "gross_sales": gross,
            "refund_amount": refund,
            "net_sales": gross - refund,
            "order_count": Decimal(len(values)),
            "avg_order": (gross - refund) / len(values),
        }[metric]
        result.append(([group] if dimension else []) + [str(value)])
    if key == "top":
        result.sort(key=lambda r: (-Decimal(r[-1]), r[0]))
        result = result[:2]
    return result


def normalized(rows, numeric_indices, ordered=False):
    rows = [
        tuple(
            Decimal(str(v)).quantize(Decimal("0.00000001"))
            if i in numeric_indices and v is not None
            else str(v)
            if v is not None
            else None
            for i, v in enumerate(row)
        )
        for row in rows
    ]
    return rows if ordered else Counter(rows)


def build():
    from app.modules.quality.models import DatasetInput

    snapshot = {"provenance": "synthetic", "customers": CUSTOMERS, "orders": ORDERS}
    digest = hashlib.sha256(
        json.dumps(snapshot, ensure_ascii=False, sort_keys=True).encode()
    ).hexdigest()
    cases = []
    for context in CONTEXTS:
        key, split, wording, dimension, filter_value = context
        for metric, label, expression in METRICS:
            plan = {"metrics": [metric]}
            group_sql = {
                "order_day": "o.order_date",
                "channel": "o.channel",
                "region": "c.region",
                "customer": "c.customer_name",
            }.get(dimension)
            sql = (
                "SELECT "
                + (f"{group_sql} AS {dimension}, " if dimension else "")
                + f"{expression} AS {metric} FROM demo_sales.m03_orders o"
            )
            if dimension in ("region", "customer") or (
                filter_value and filter_value[0] == "customer"
            ):
                sql += " LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id"
            sql += " WHERE o.status='paid'"
            if dimension:
                plan["dimensions"] = [{"dimension_id": dimension}]
            if key == "range":
                plan["time_range"] = {"start": "2026-09-01", "end": "2026-09-03"}
                sql += (
                    " AND o.order_date >= '2026-09-01' AND o.order_date < '2026-09-03'"
                )
            if filter_value:
                dim, value = filter_value
                plan["filters"] = [
                    {"dimension_id": dim, "operator": "eq", "values": [value]}
                ]
                field = "o.channel" if dim == "channel" else "c.customer_name"
                sql += f" AND {field}='{value}'"
            if dimension:
                sql += f" GROUP BY {group_sql}"
            if key == "top":
                plan.update(
                    limit=2,
                    order_by=[
                        {"field": metric, "direction": "desc"},
                        {"field": "customer", "direction": "asc"},
                    ],
                )
                sql += f" ORDER BY {metric} DESC, customer ASC LIMIT 2"
            for variant in range(2):
                case = {
                    "id": f"sales-{key}-{metric}-{variant + 1}",
                    "group": f"sales-{key}",
                    "split": split,
                    "question": f"按已发布的{label}口径，{wording}，给出结果。"
                    if variant == 0
                    else f"请统计{label}，范围是{wording}，沿用已发布定义。",
                    "mode": "metrics",
                    "actor_role": "admin",
                    "tags": ["synthetic", key] + (["entity"] if filter_value else []),
                    "expected_action": "answer",
                    "columns": ([dimension] if dimension else []) + [metric],
                    "numeric_columns": [metric],
                    "expected_rows": independent_rows(metric, context),
                    "ordered": key == "top",
                    "tolerance": "0.00000001" if metric == "avg_order" else "0",
                    "reference_sql": sql,
                    "reference_plan": plan,
                }
                # Selected entity rewrites exercise inherited filter conditions.
                if variant == 1 and filter_value:
                    case["history"] = [f"按已发布的{label}口径，{wording}，给出结果。"]
                    case["question"] = (
                        "沿用刚才的客户或渠道筛选，再给我同一指标的结果。"
                    )
                    case["tags"].append("followup")
                cases.append(case)
    for group, split, action, questions, tags in NEGATIVE:
        for i, question in enumerate(questions):
            cases.append(
                {
                    "id": f"sales-{group}-{i + 1}",
                    "group": f"sales-{group}",
                    "split": split,
                    "question": question,
                    "mode": "metrics",
                    "actor_role": "admin",
                    "tags": ["synthetic", *tags],
                    "expected_action": action,
                }
            )
    dataset = DatasetInput.model_validate(
        {
            "name": "M07 销售经营120题 · 合成留出验证",
            "topic_id": "00000000-0000-0000-0000-000000000000",
            "semantic_version": 1,
            "source_snapshot": f"M03五订单三客户冻结样例；sha256:{digest}",
            "as_of": "2026-09-07",
            "timezone": "Asia/Shanghai",
            "provenance": "synthetic",
            "owner": "合成资料；业务口径负责人待确认",
            "cases": cases,
        }
    ).model_dump(mode="json")
    assert Counter(c["split"] for c in cases) == {"dev": 60, "blind": 60}
    assert Counter(c["expected_action"] for c in cases) == {
        "answer": 100,
        "clarify": 10,
        "unsupported": 10,
    }
    assert sum("entity" in c["tags"] for c in cases) >= 40
    return dataset, snapshot


def verify(dataset):
    import sqlglot
    import yaml
    from app.modules.catalog.models import ColumnMeta, TableMeta
    from app.modules.query.compiler import compile_plan
    from app.modules.query.models import QueryPlan
    from app.modules.semantic.models import SemanticDefinition

    definition = SemanticDefinition.model_validate(
        yaml.safe_load(
            (ROOT / "docs/examples/销售经营语义示例.yaml").read_text(encoding="utf8")
        )
    )
    db = snapshot_connection()
    tables = []
    for name in ("m03_orders", "m03_customers"):
        columns = [
            ColumnMeta(
                name=r[1],
                ordinal=r[0] + 1,
                data_type="numeric(14,2)" if r[2] == "REAL" else r[2],
                nullable=not r[3],
                primary_key=bool(r[5]),
            )
            for r in db.execute(f"PRAGMA demo_sales.table_xinfo('{name}')")
        ]
        tables.append(
            TableMeta(
                schema_name="demo_sales", name=name, kind="table", columns=columns
            )
        )
    checked = []
    for case in dataset["cases"]:
        if case["expected_action"] != "answer":
            continue
        numeric = [case["columns"].index(c) for c in case["numeric_columns"]]
        expected = normalized(case["expected_rows"], numeric, case["ordered"])
        cursor = db.execute(case["reference_sql"])
        assert [c[0] for c in cursor.description] == case["columns"], case["id"]
        assert normalized(cursor.fetchall(), numeric, case["ordered"]) == expected, (
            case["id"]
        )
        # Also compare the actual semantic compiler against the independent oracle.
        compiled = compile_plan(
            definition,
            tables,
            "postgresql",
            QueryPlan.model_validate(case["reference_plan"]),
        )
        sql = re.sub(r"%\((\w+)\)s", r":\1", compiled.sql.replace("%%", "%"))
        sqlite_sql = sqlglot.transpile(sql, read="postgres", write="sqlite")[0]
        rows = db.execute(
            sqlite_sql, {k: str(v) for k, v in compiled.parameters.items()}
        ).fetchall()
        # Executor consumes at most plan.limit; compiler fetches one extra to detect truncation.
        rows = rows[: case["reference_plan"].get("limit", 100)]
        assert [c.id for c in compiled.columns] == case["columns"], case["id"]
        assert normalized(rows, numeric, case["ordered"]) == expected, (
            case["id"],
            rows,
            case["expected_rows"],
        )
        checked.append(case["id"])
    db.close()
    return {
        "evidence": "synthetic_sqlite_reference_and_translated_semantic_sql_no_model",
        "reference_sql_passed": len(checked),
        "semantic_plan_passed": len(checked),
        "case_ids": checked,
    }


def verify_local_demo(dataset):
    """Opt-in read of the fixed synthetic endpoint, with full snapshot comparison."""
    import psycopg
    from module1_demo import configure

    cfg = configure()
    with psycopg.connect(
        host="127.0.0.1",
        port=15432,
        dbname="lightsql_demo",
        user="light_reader",
        password=cfg["reader_password"],
        connect_timeout=5,
        sslmode="disable",
        options="-c default_transaction_read_only=on -c statement_timeout=15000",
    ) as db:
        db.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
        customers = [
            list(r)
            for r in db.execute(
                "SELECT tenant_id,customer_id,customer_name,region FROM demo_sales.m03_customers ORDER BY tenant_id,customer_id"
            )
        ]
        orders = [
            list(r)
            for r in db.execute(
                "SELECT id,tenant_id,customer_id,order_date,channel,status,gross_amount,refund_amount FROM demo_sales.m03_orders ORDER BY id"
            )
        ]
        for row in orders:
            row[3] = row[3].isoformat()
        assert customers == CUSTOMERS and orders == ORDERS, (
            "Local synthetic snapshot has changed; refusing to certify references"
        )
        count = 0
        for case in dataset["cases"]:
            if case["expected_action"] != "answer":
                continue
            cursor = db.execute(case["reference_sql"])
            assert [c.name for c in cursor.description] == case["columns"], case["id"]
            numeric = [case["columns"].index(c) for c in case["numeric_columns"]]
            assert normalized(
                cursor.fetchall(), numeric, case["ordered"]
            ) == normalized(case["expected_rows"], numeric, case["ordered"]), case["id"]
            count += 1
        return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "docs/examples/sales-acceptance"
    )
    parser.add_argument(
        "--verify-local-demo",
        action="store_true",
        help="Also read and verify the fixed local PostgreSQL M03 snapshot; never write source data",
    )
    args = parser.parse_args()
    args.output = args.output.resolve()
    # Only satisfy imports used by the offline compiler; never read demo secrets.
    os.environ.update(
        SECRET_KEY="synthetic-offline-reference-only-2026",
        PROJECT_NAME="offline-reference",
        DATABASE_URL="postgresql://unused:unused@127.0.0.1:1/unused",
        FIRST_SUPERUSER="offline@example.com",
        FIRST_SUPERUSER_PASSWORD="synthetic-offline-only",
    )
    dataset, snapshot = build()
    evidence = verify(dataset)
    if args.verify_local_demo:
        evidence["postgresql_reference_sql_passed"] = verify_local_demo(dataset)
    args.output.mkdir(parents=True, exist_ok=True)
    for name, value in (
        ("questions.json", dataset),
        ("snapshot.json", snapshot),
        ("reference-check.json", evidence),
    ):
        (args.output / name).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf8"
        )
    sql = []
    lines = [
        "# 销售经营合成120题",
        "",
        "合成数据，非真实业务金标。100道可回答、10道澄清、10道不支持；开发/留出各60题。50组可回答场景各有两个问法，同类筛选和改写不跨集合。留出答案随仓库公开，不是保密业务盲测。",
        "",
        "| ID | 集合 | 问题与历史 | 预期动作 |",
        "|---|---|---|---|",
    ]
    for case in dataset["cases"]:
        prompt = " → ".join([*case["history"], case["question"]])
        lines.append(
            f"| {case['id']} | {case['split']} | {prompt} | {case['expected_action']} |"
        )
        if case["reference_sql"]:
            sql.append(f"-- {case['id']}\n-- {prompt}\n{case['reference_sql']};")
    (args.output / "questions.md").write_text("\n".join(lines) + "\n", encoding="utf8")
    (args.output / "reference.sql").write_text(
        "-- Read-only PostgreSQL reference queries over the frozen M03 sample.\n\n"
        + "\n\n".join(sql)
        + "\n",
        encoding="utf8",
    )
    print(
        json.dumps(
            {
                "questions": len(dataset["cases"]),
                "reference_checks": evidence["reference_sql_passed"],
                "output": str(args.output),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
