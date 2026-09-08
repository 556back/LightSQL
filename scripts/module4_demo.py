"""M04 verification on the five isolated local synthetic databases only."""

import json
import sys
import threading
import time
import uuid
from contextlib import contextmanager
from decimal import Decimal

from module1_demo import LOCAL, configure

TOPIC_ID = "7d5c849d-6148-4140-ae23-fa70c2fc847b"


def seed(cfg):
    import dmPython
    import oracledb
    import psycopg
    import pymysql

    for kind in ("postgresql", "mysql", "oracle", "dameng", "kingbase"):
        if kind in ("postgresql", "kingbase"):
            conn = psycopg.connect(host="127.0.0.1", port=15432 if kind == "postgresql" else 15421, dbname="lightsql_demo" if kind == "postgresql" else "sales_demo", user="postgres" if kind == "postgresql" else "system", password=cfg["pg_password" if kind == "postgresql" else "kingbase_password"], client_encoding="utf8")
            schema = "demo_sales" if kind == "postgresql" else "light_demo"
        elif kind == "mysql":
            conn = pymysql.connect(host="127.0.0.1", port=13306, database="sales_demo", user="root", password=cfg["mysql_password"], charset="utf8mb4")
            schema = "sales_demo"
        elif kind == "oracle":
            conn = oracledb.connect(user="system", password=cfg["oracle_password"], dsn="127.0.0.1:11521/FREEPDB1")
            schema = "LIGHT_DEMO"
        else:
            conn = dmPython.connect(user="SYSDBA", password=cfg["dameng_password"], server="127.0.0.1", port=15236, login_timeout=5000)
            schema = "LIGHT_DEMO"
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM {schema}.m02_customers")
                customers = cur.fetchone()[0]
                cur.execute(f"SELECT COUNT(*) FROM {schema}.m02_orders")
                orders = cur.fetchone()[0]
                if (customers, orders) not in ((0, 0), (3, 4)):
                    raise RuntimeError(f"{kind}: fixture data differs; refusing to overwrite")
                if customers == 0:
                    cur.execute(f"INSERT INTO {schema}.m02_customers VALUES (1,101,'华东示例客户')")
                    cur.execute(f"INSERT INTO {schema}.m02_customers VALUES (1,102,'华南示例客户')")
                    cur.execute(f"INSERT INTO {schema}.m02_customers VALUES (2,101,'华北示例客户')")
                    for values in ("1,1,101,1200.10", "2,1,102,800.20", "3,2,101,1500.30", "4,1,101,NULL"):
                        cur.execute(f"INSERT INTO {schema}.m02_orders VALUES ({values})")
                conn.commit()
            print(kind, "synthetic M04 rows ready", flush=True)
        finally:
            conn.close()


def cross_definition(tables):
    from app.modules.semantic.models import SemanticDefinition
    orders = next(t for t in tables if t.name.lower() == "m02_orders")
    customers = next(t for t in tables if t.name.lower() == "m02_customers")
    physical = lambda table, name: next(c.name for c in table.columns if c.name.lower() == name)
    base = {"model_id": "orders", "allowed_dimensions": ["customer", "tenant"], "description": "M04 跨库合成金额校验", "unit": "元"}
    return SemanticDefinition.model_validate({"owner": "M04 本地验收", "models": [{"id": id, "label": id, "relation": {"schema_name": t.schema_name, "name": t.name, "kind": t.kind}, "grain": "一行一笔订单" if id == "orders" else "一行一个租户客户", "primary_key": [c.name for c in t.columns if c.primary_key]} for id, t in (("orders", orders), ("customers", customers))], "dimensions": [{"id": "customer", "label": "客户", "model_id": "customers", "column": physical(customers, "customer_name"), "value_type": "string"}, {"id": "tenant", "label": "租户", "model_id": "orders", "column": physical(orders, "tenant_id"), "value_type": "number"}], "metrics": [{**base, "id": "amount", "label": "订单金额", "aggregation": "sum", "column": physical(orders, "amount")}, {**base, "id": "orders_count", "label": "订单数", "aggregation": "count", "unit": "笔"}, {**base, "id": "average", "label": "单均金额", "aggregation": "ratio", "numerator": "amount", "denominator": "orders_count", "additivity": "non_additive"}], "relations": [{"id": "customer_join", "label": "复合租户客户键", "from_model": "orders", "to_model": "customers", "from_columns": [physical(orders, "tenant_id"), physical(orders, "customer_id")], "to_columns": [physical(customers, "tenant_id"), physical(customers, "customer_id")], "description": "租户与客户编码必须同时匹配"}]})


def verify_drivers():
    from sqlmodel import Session, select
    from app.core.db import engine
    from app.modules.catalog.models import CatalogState, TableMeta
    from app.modules.datasources.connection import readonly_cursor
    from app.modules.datasources.models import DataSource, DataSourceInput
    from app.modules.datasources.service import decrypt_password
    from app.modules.query.compiler import CompiledQuery, compile_plan
    from app.modules.query.executor import execute
    from app.modules.query.models import QueryGrant, QueryPlan, ResultColumn
    from app.modules.semantic.validation import validate
    records = []
    with Session(engine) as session:
        sources = session.exec(select(DataSource)).all()
        for source in sources:
            assert source.host == "127.0.0.1" and source.port in (15432, 13306, 11521, 15236, 15421)
            state = session.get(CatalogState, source.id)
            tables = [TableMeta.model_validate(t) for t in state.snapshot]
            definition = cross_definition(tables)
            assert validate(definition, source, state).valid
            plan = QueryPlan(metrics=["amount", "orders_count", "average"], dimensions=[{"dimension_id": "customer"}])
            compiled = compile_plan(definition, tables, source.database_type, plan)
            config, password = DataSourceInput.model_validate(source), decrypt_password(source.encrypted_password)
            if source.database_type == "dameng":
                # Fixed four-row synthetic fixture only. This does not open the
                # public executor gate or claim production timeout guarantees.
                with readonly_cursor(config, password) as cur:
                    cur.execute(compiled.sql, compiled.parameters)
                    rows = cur.fetchmany(10)
                outcome = {"result": {"rows": rows}}
            else:
                outcome = execute(config, password, compiled, plan, threading.Event())
                assert outcome["status"] == "succeeded", (source.database_type, outcome)
            rows = outcome["result"]["rows"]
            assert len(rows) == 3 and sum(Decimal(str(r[1])) for r in rows) == Decimal("3500.60"), (source.database_type, rows)
            assert sum(Decimal(str(r[2])) for r in rows) == 4
            record = {"database": source.database_type, "binding_join_decimal": True, "rows": len(rows), "total": "3500.60", "execution_enabled": source.database_type != "dameng"}
            if source.database_type != "dameng":
                root = next(m for m in definition.models if m.id == "orders")
                root_table = next(t for t in tables if t.name == root.relation.name and t.schema_name == root.relation.schema_name)
                tenant = next(c.name for c in root_table.columns if c.name.lower() == "tenant_id")
                grant = QueryGrant(user_id=uuid.uuid4(), metric_ids=plan.metrics, dimension_ids=["customer"], rows=[{"model_id": "orders", "column": tenant, "values": ["1"]}])
                limited = execute(config, password, compile_plan(definition, tables, source.database_type, plan, grant), plan, threading.Event())
                assert sum(Decimal(r[1]) for r in limited["result"]["rows"]) == Decimal("2000.30")
                short = QueryPlan(metrics=["amount"], dimensions=[{"dimension_id": "customer"}], limit=1)
                truncated = execute(config, password, compile_plan(definition, tables, source.database_type, short), short, threading.Event())
                assert truncated["row_count"] == 1 and truncated["truncated"]
                empty = QueryPlan(metrics=["amount", "orders_count", "average"], filters=[{"dimension_id": "tenant", "operator": "eq", "values": ["999"]}])
                no_rows = execute(config, password, compile_plan(definition, tables, source.database_type, empty), empty, threading.Event())
                assert no_rows["result"]["rows"][0] == [None, "0", None], no_rows
                slow_sql = {"postgresql": "SELECT pg_sleep(8)", "kingbase": "SELECT pg_sleep(8)", "mysql": "SELECT SLEEP(8)", "oracle": "SELECT SUM(SQRT(LEVEL)) FROM DUAL CONNECT BY LEVEL <= 100000000"}[source.database_type]
                slow = CompiledQuery(slow_sql, {}, [ResultColumn(id="test", label="限时测试", value_type="number")], [])
                timed = execute(config, password, slow, QueryPlan(metrics=["amount"], timeout_seconds=1), threading.Event())
                assert timed["status"] == "timed_out" and timed["cleaned"], (source.database_type, timed)
                stop = threading.Event()
                timer = threading.Timer(1, stop.set)
                timer.start()
                cancelled = execute(config, password, slow, QueryPlan(metrics=["amount"], timeout_seconds=15), stop)
                timer.join()
                assert cancelled["status"] == "cancelled" and cancelled["cleaned"] and cancelled["elapsed_ms"] < 7000, (source.database_type, cancelled)
                record.update(row_scope=True, truncation=True, zero_denominator=True, timeout_ms=timed["elapsed_ms"], cancel_ms=cancelled["elapsed_ms"], cleanup_acknowledged=True)
            records.append(record)
            print(json.dumps(record, ensure_ascii=False), flush=True)
    (LOCAL / "module4-drivers.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf8")


def api_acceptance():
    import httpx
    @contextmanager
    def login(email):
        client = httpx.Client(base_url="http://127.0.0.1:8000/api/v1", timeout=40)
        response = client.post("/login/access-token", data={"username": email, "password": "LightSQL-Demo-2026!"})
        response.raise_for_status()
        client.headers["Authorization"] = "Bearer " + response.json()["access_token"]
        try:
            yield client
        finally:
            client.close()

    def run(client, plan):
        response = client.post("/queries/", json={"topic_id": TOPIC_ID, "request_id": str(uuid.uuid4()), "plan": plan})
        response.raise_for_status()
        job_id = response.json()["id"]
        for _ in range(100):
            job = client.get(f"/queries/{job_id}").json()
            if job["status"] not in ("queued", "running", "cancelling"):
                assert job["status"] == "succeeded", job
                result = client.get(f"/queries/{job_id}/result")
                result.raise_for_status()
                return job, result.json()
            time.sleep(0.25)
        raise RuntimeError("Query worker did not finish")

    with login("admin@lightsql.example.com") as admin:
        topic = admin.get(f"/topics/{TOPIC_ID}/published").json()
        users = admin.get("/users/", params={"limit": 1000}).json()["data"]
        member = next(u for u in users if u["email"] == "analyst@lightsql.example.com")
        policy = admin.get(f"/queries/topics/{TOPIC_ID}/policy").json()
        grant = {"user_id": member["id"], "metric_ids": [m["id"] for m in topic["metrics"]], "dimension_ids": [d["id"] for d in topic["dimensions"]], "unrestricted": False, "rows": [{"model_id": "orders", "column": "tenant_id", "values": ["1"]}]}
        others = [g for g in policy["grants"] if g["user_id"] != member["id"]]
        saved = admin.put(f"/queries/topics/{TOPIC_ID}/policy", json={"expected_revision": policy["revision"], "grants": [*others, grant]})
        saved.raise_for_status()
        plan = {"metrics": ["net_sales", "order_count", "avg_order"], "dimensions": [{"dimension_id": "region"}], "order_by": [{"field": "net_sales", "direction": "desc"}]}
        full_job, full = run(admin, plan)
        assert sum(Decimal(r[1]) for r in full["rows"]) == 4000 and sum(int(r[2]) for r in full["rows"]) == 4
        month_job, month = run(admin, {"metrics": ["net_sales"], "dimensions": [{"dimension_id": "order_day", "grain": "month"}], "time_range": {"start": "2026-09-01", "end": "2026-10-01"}})
        assert month["rows"] == [["2026-09", "4000.00"]], month
        with login("analyst@lightsql.example.com") as analyst:
            restricted_job, restricted = run(analyst, plan)
            assert sum(Decimal(r[1]) for r in restricted["rows"]) == 2800 and sum(int(r[2]) for r in restricted["rows"]) == 3
            assert restricted_job["sql"] is None
            assert analyst.get(f"/queries/{full_job['id']}/result").status_code == 404
            current = admin.get(f"/queries/topics/{TOPIC_ID}/policy").json()
            revoked = admin.put(f"/queries/topics/{TOPIC_ID}/policy", json={"expected_revision": current["revision"], "grants": others})
            revoked.raise_for_status()
            try:
                assert analyst.get(f"/queries/{restricted_job['id']}/result").status_code == 403
            finally:
                restored = admin.put(f"/queries/topics/{TOPIC_ID}/policy", json={"expected_revision": revoked.json()["revision"], "grants": [*others, grant]})
                restored.raise_for_status()
            restricted_job, restricted = run(analyst, plan)
        evidence = {"topic_id": TOPIC_ID, "semantic_version": topic["version"], "admin_job": full_job["id"], "admin_total": "4000.00", "member_job": restricted_job["id"], "member_total": "2800.00", "month_group": month["rows"], "revocation_checked": True, "cross_user_result_denied": True}
        (LOCAL / "module4-verification.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf8")
        print(json.dumps(evidence, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    cfg = configure()
    {"seed": lambda: seed(cfg), "drivers": verify_drivers, "acceptance": api_acceptance}[sys.argv[1]]()
