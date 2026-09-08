"""M03 acceptance using synthetic local fixtures and the real HTTP API."""

import json
import sys
import time

from module1_demo import LOCAL, ROOT, configure

TOPIC_NAME = "销售经营分析"
MEMBER_EMAIL = "analyst@lightsql.example.com"


def business_definition():
    from app.modules.semantic.models import SemanticDefinition

    dims = [
        (
            "order_day",
            "订单日期",
            "orders",
            "order_date",
            "date",
            "按业务自然日期统计，时区为上海。",
        ),
        (
            "channel",
            "销售渠道",
            "orders",
            "channel",
            "entity",
            "线上直营、合作渠道、门店销售。",
        ),
        (
            "order_status",
            "订单状态",
            "orders",
            "status",
            "string",
            "paid 表示已支付；cancelled 表示已取消。",
        ),
        (
            "region",
            "客户区域",
            "customers",
            "region",
            "string",
            "订单通过租户与客户复合键关联到客户区域。",
        ),
        (
            "customer",
            "客户",
            "customers",
            "customer_name",
            "entity",
            "合成客户名称，仅用于本地演示。",
        ),
    ]
    allowed = ["order_day", "channel", "region", "customer"]
    metrics = []
    for id, label, agg, col, unit, desc in [
        (
            "gross_sales",
            "销售总额",
            "sum",
            "gross_amount",
            "元",
            "已支付订单的含税销售金额合计，退款前口径。",
        ),
        (
            "refund_amount",
            "退款金额",
            "sum",
            "refund_amount",
            "元",
            "已支付订单截至当前的退款金额合计，按原订单日期归属。",
        ),
        (
            "net_sales",
            "净销售额",
            "sum",
            "net_amount",
            "元",
            "已支付订单净金额合计；净金额为销售总额减累计退款金额，按原订单日期归属。",
        ),
        (
            "order_count",
            "支付订单数",
            "count",
            None,
            "笔",
            "已支付订单行数，一行一单，排除取消订单。",
        ),
        (
            "max_order",
            "最高订单金额",
            "max",
            "net_amount",
            "元",
            "已支付订单中最大的单笔净金额，不可跨组直接相加。",
        ),
        (
            "min_order",
            "最低订单金额",
            "min",
            "net_amount",
            "元",
            "已支付订单中最小的单笔净金额，不可跨组直接相加。",
        ),
        (
            "avg_refund",
            "单均退款金额",
            "avg",
            "refund_amount",
            "元/笔",
            "已支付订单的平均退款金额，包括退款为零的订单。",
        ),
        (
            "channel_count",
            "成交渠道数",
            "count_distinct",
            "channel",
            "个",
            "已支付订单涉及的不同渠道编码数量，忽略空值，不可跨组累加。",
        ),
    ]:
        metrics.append(
            {
                "id": id,
                "label": label,
                "aggregation": agg,
                "column": col,
                "model_id": "orders",
                "description": desc,
                "unit": unit,
                "time_dimension": "order_day",
                "allowed_dimensions": allowed,
                "filter_ids": ["paid_only"],
                "additivity": "additive" if agg in ("sum", "count") else "non_additive",
            }
        )
    for id, label, numerator, denominator, unit, desc in [
        (
            "avg_order",
            "客单价",
            "net_sales",
            "order_count",
            "元/笔",
            "净销售额除以支付订单数，在相同日期、渠道及客户范围内先聚合再相除；分母为零返回空值。",
        ),
        (
            "refund_rate",
            "退款金额占比",
            "refund_amount",
            "gross_sales",
            "比例",
            "退款金额除以退款前销售总额，结果为 0–1 比例，按原订单日期归属；分母为零返回空值。",
        ),
    ]:
        metrics.append(
            {
                "id": id,
                "label": label,
                "aggregation": "ratio",
                "model_id": "orders",
                "description": desc,
                "unit": unit,
                "time_dimension": "order_day",
                "allowed_dimensions": allowed,
                "filter_ids": ["paid_only"],
                "additivity": "non_additive",
                "numerator": numerator,
                "denominator": denominator,
            }
        )
    metrics[2]["aliases"] = ["净营收", "扣退销售额"]
    return SemanticDefinition.model_validate(
        {
            "owner": "经营分析组",
            "timezone": "Asia/Shanghai",
            "models": [
                {
                    "id": "orders",
                    "label": "销售订单",
                    "relation": {
                        "schema_name": "demo_sales",
                        "name": "m03_orders",
                        "kind": "table",
                    },
                    "grain": "每行一笔订单；订单主键在全表唯一。",
                    "primary_key": ["id"],
                },
                {
                    "id": "customers",
                    "label": "客户档案",
                    "relation": {
                        "schema_name": "demo_sales",
                        "name": "m03_customers",
                        "kind": "table",
                    },
                    "grain": "每行一个租户下的客户；不同租户可以使用同一客户编号。",
                    "primary_key": ["tenant_id", "customer_id"],
                },
            ],
            "dimensions": [
                {
                    "id": id,
                    "label": label,
                    "model_id": model,
                    "column": col,
                    "value_type": kind,
                    "description": desc,
                    "sensitive": id == "customer",
                }
                for id, label, model, col, kind, desc in dims
            ],
            "metrics": metrics,
            "filters": [
                {
                    "id": "paid_only",
                    "label": "仅已支付订单",
                    "dimension_id": "order_status",
                    "operator": "eq",
                    "values": ["paid"],
                }
            ],
            "relations": [
                {
                    "id": "order_customer",
                    "label": "订单归属客户",
                    "from_model": "orders",
                    "to_model": "customers",
                    "from_columns": ["tenant_id", "customer_id"],
                    "to_columns": ["tenant_id", "customer_id"],
                    "cardinality": "many_to_one",
                    "join_type": "left",
                    "description": "租户编号与客户编号同时匹配，左连接保留客户未匹配的订单。",
                }
            ],
            "entities": [
                {
                    "id": "channel_online",
                    "dimension_id": "channel",
                    "label": "线上直营",
                    "aliases": ["官网", "自营网店"],
                    "value": "online",
                },
                {
                    "id": "channel_partner",
                    "dimension_id": "channel",
                    "label": "合作渠道",
                    "aliases": ["代理", "经销渠道"],
                    "value": "partner",
                },
                {
                    "id": "channel_store",
                    "dimension_id": "channel",
                    "label": "门店",
                    "aliases": ["线下门店"],
                    "value": "store",
                },
                {
                    "id": "customer_east",
                    "dimension_id": "customer",
                    "label": "华东示例客户",
                    "aliases": ["华东样例"],
                    "value": "华东示例客户",
                },
            ],
        }
    ).model_dump(mode="json")


def seed(cfg):
    import psycopg

    with psycopg.connect(
        host="127.0.0.1",
        port=15432,
        user="postgres",
        password=cfg["pg_password"],
        dbname="lightsql_demo",
    ) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS demo_sales.m03_customers (tenant_id int, customer_id int, customer_name text NOT NULL, region text NOT NULL, PRIMARY KEY (tenant_id, customer_id))"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS demo_sales.m03_orders (id int PRIMARY KEY, tenant_id int NOT NULL, customer_id int NOT NULL, order_date date NOT NULL, channel text NOT NULL, status text NOT NULL, gross_amount numeric(14,2) NOT NULL, refund_amount numeric(14,2) NOT NULL DEFAULT 0, net_amount numeric(14,2) GENERATED ALWAYS AS (gross_amount-refund_amount) STORED, CONSTRAINT m03_customer_fk FOREIGN KEY (tenant_id, customer_id) REFERENCES demo_sales.m03_customers(tenant_id, customer_id))"
        )
        conn.execute(
            "COMMENT ON TABLE demo_sales.m03_orders IS '合成订单 · 语义层演示'"
        )
        conn.execute(
            "COMMENT ON COLUMN demo_sales.m03_orders.net_amount IS '净销售额：销售总额减累计退款，按原订单日期归属'"
        )
        conn.execute(
            "INSERT INTO demo_sales.m03_customers VALUES (1,101,'华东示例客户','华东'), (1,102,'华南示例客户','华南'), (2,101,'华北示例客户','华北') ON CONFLICT DO NOTHING"
        )
        conn.execute(
            "INSERT INTO demo_sales.m03_orders (id, tenant_id, customer_id, order_date, channel, status, gross_amount, refund_amount) VALUES (1,1,101,'2026-09-01','online','paid',1200,100), (2,1,102,'2026-09-01','partner','paid',800,0), (3,2,101,'2026-09-02','store','paid',1500,300), (4,1,101,'2026-09-03','online','cancelled',600,0), (5,1,102,'2026-09-03','online','paid',900,0) ON CONFLICT DO NOTHING"
        )
        conn.execute(
            "GRANT SELECT ON demo_sales.m03_orders, demo_sales.m03_customers TO light_reader"
        )
    print("M03: synthetic orders and customers ready", flush=True)


def api_acceptance():
    import httpx

    with httpx.Client(base_url="http://127.0.0.1:8000/api/v1", timeout=30) as client:
        login = client.post(
            "/login/access-token",
            data={
                "username": "admin@lightsql.example.com",
                "password": "LightSQL-Demo-2026!",
            },
        )
        login.raise_for_status()
        client.headers["Authorization"] = "Bearer " + login.json()["access_token"]
        sources = client.get("/datasources/").json()["data"]
        source = next(
            s
            for s in sources
            if s["database_type"] == "postgresql"
            and s["host"] == "127.0.0.1"
            and s["port"] == 15432
        )
        cat_url = f"/catalog/{source['id']}"
        catalog = client.get(cat_url).json()
        objects = list(catalog["scope"])
        for name in ("m03_orders", "m03_customers"):
            ref = {"schema_name": "demo_sales", "name": name, "kind": "table"}
            if ref not in objects:
                objects.append(ref)
        if objects != catalog["scope"]:
            response = client.put(
                cat_url + "/scope",
                json={
                    "expected_revision": catalog["revision"],
                    "expected_source_revision": source["revision"],
                    "objects": objects,
                },
            )
            response.raise_for_status()
        job = client.post(cat_url + "/sync")
        job.raise_for_status()
        for _ in range(45):
            state = next(
                j
                for j in client.get(cat_url + "/jobs").json()
                if j["id"] == job.json()["id"]
            )
            if state["status"] not in ("queued", "running"):
                assert state["status"] == "succeeded", "Catalog sync failed"
                break
            time.sleep(1)
        else:
            raise RuntimeError("Worker did not finish")
        print("M03: real catalog sync succeeded", flush=True)
        existing = next(
            (t for t in client.get("/topics/").json() if t["name"] == TOPIC_NAME), None
        )
        if existing:
            topic = client.get(f"/topics/{existing['id']}").json()
            assert topic["definition"] == business_definition(), (
                "Existing customized draft preserved; no overwrite performed"
            )
        else:
            response = client.post(
                "/topics/",
                json={
                    "name": TOPIC_NAME,
                    "description": "围绕销售、退款、渠道与客户区域，统一经营分析的十项核心指标。合成数据演示。",
                    "source_id": source["id"],
                    "owner": "经营分析组",
                },
            )
            response.raise_for_status()
            topic = response.json()
            response = client.put(
                f"/topics/{topic['id']}/draft",
                json={
                    "expected_revision": topic["revision"],
                    "name": topic["name"],
                    "description": topic["description"],
                    "enabled": True,
                    "definition": business_definition(),
                },
            )
            response.raise_for_status()
            topic = response.json()
        url = f"/topics/{topic['id']}"
        checked = client.post(
            url + "/validate", json={"expected_revision": topic["revision"]}
        )
        checked.raise_for_status()
        assert checked.json()["valid"], checked.json()["issues"]
        if not topic["current_version"] or topic["availability"] != "ready":
            release = client.post(
                url + "/releases",
                json={
                    "expected_revision": topic["revision"],
                    "note": "建立销售经营口径：10 项指标、5 个维度、完整租户客户复合键与渠道词典。",
                },
            )
            release.raise_for_status()
            topic = client.get(url).json()
        users = client.get("/users/", params={"limit": 10000}).json()["data"]
        member = next((u for u in users if u["email"] == MEMBER_EMAIL), None)
        if not member:
            response = client.post(
                "/users/",
                json={
                    "email": MEMBER_EMAIL,
                    "password": "LightSQL-Demo-2026!",
                    "full_name": "演示分析师",
                    "is_active": True,
                    "is_superuser": False,
                },
            )
            response.raise_for_status()
            member = response.json()
        if member["id"] not in topic["member_ids"]:
            response = client.put(
                url + "/members",
                json={
                    "expected_revision": topic["revision"],
                    "user_ids": [*topic["member_ids"], member["id"]],
                },
            )
            response.raise_for_status()
        exported = client.get(url + "/export", params={"format": "yaml"})
        exported.raise_for_status()
        (ROOT / "docs/examples").mkdir(exist_ok=True)
        (ROOT / "docs/examples/销售经营语义示例.yaml").write_text(
            exported.json()["content"], encoding="utf8"
        )
        member_login = client.post(
            "/login/access-token",
            data={"username": MEMBER_EMAIL, "password": "LightSQL-Demo-2026!"},
        )
        member_login.raise_for_status()
        client.headers["Authorization"] = (
            "Bearer " + member_login.json()["access_token"]
        )
        public = client.get(url + "/published")
        public.raise_for_status()
        assert len(public.json()["metrics"]) == 10
        assert (
            "schema_name" not in public.text
            and "model_id" not in public.text
            and "tenant_id" not in public.text
        )
        assert client.get(url + "/export").status_code == 403
        print(
            f"M03: published topic {topic['id']}; analyst access and private mappings verified",
            flush=True,
        )
        return {
            "topic_id": topic["id"],
            "metrics": 10,
            "dimensions": 5,
            "member_access": True,
        }


def five_catalog_validation():
    from sqlmodel import Session, select
    from app.core.db import engine
    from app.modules.catalog.models import CatalogState
    from app.modules.catalog.service import visible_tables
    from app.modules.datasources.models import DataSource
    from app.modules.semantic.models import SemanticDefinition
    from app.modules.semantic.validation import validate

    records = []
    with Session(engine) as session:
        for source in session.exec(select(DataSource)).all():
            assert source.host == "127.0.0.1" and source.port in (
                15432,
                13306,
                11521,
                15236,
                15421,
            )
            state = session.get(CatalogState, source.id)
            tables = visible_tables(state)
            orders = next(t for t in tables if t.name.lower() == "m02_orders")
            customers = next(t for t in tables if t.name.lower() == "m02_customers")

            def name(table, lower):
                return next(c.name for c in table.columns if c.name.lower() == lower)

            definition = SemanticDefinition.model_validate(
                {
                    "owner": "五库元数据验收",
                    "models": [
                        {
                            "id": id,
                            "label": id,
                            "relation": {
                                "schema_name": t.schema_name,
                                "name": t.name,
                                "kind": t.kind,
                            },
                            "grain": "合成对象粒度",
                            "primary_key": [c.name for c in t.columns if c.primary_key],
                        }
                        for id, t in [("orders", orders), ("customers", customers)]
                    ],
                    "dimensions": [
                        {
                            "id": "customer_name",
                            "label": "客户名称",
                            "model_id": "customers",
                            "column": name(customers, "customer_name"),
                            "value_type": "string",
                        }
                    ],
                    "metrics": [
                        {
                            "id": "amount",
                            "label": "订单金额",
                            "model_id": "orders",
                            "column": name(orders, "amount"),
                            "aggregation": "sum",
                            "unit": "元",
                            "description": "合成订单金额求和",
                            "allowed_dimensions": ["customer_name"],
                        }
                    ],
                    "relations": [
                        {
                            "id": "customer_join",
                            "label": "客户关联",
                            "from_model": "orders",
                            "to_model": "customers",
                            "from_columns": [
                                name(orders, "tenant_id"),
                                name(orders, "customer_id"),
                            ],
                            "to_columns": [
                                name(customers, "tenant_id"),
                                name(customers, "customer_id"),
                            ],
                            "description": "人工确认的完整租户客户复合键",
                        }
                    ],
                }
            )
            result = validate(definition, source, state)
            assert result.valid, result.issues
            records.append(
                {
                    "database": source.database_type,
                    "valid": True,
                    "warnings": sorted({i.code for i in result.issues}),
                }
            )
            print(
                f"{source.database_type}: semantic binding to real catalog valid",
                flush=True,
            )
    return records


if __name__ == "__main__":
    cfg = configure()
    if len(sys.argv) > 1 and sys.argv[1] == "seed":
        seed(cfg)
    else:
        result = api_acceptance()
        result["databases"] = five_catalog_validation()
        (LOCAL / "module3-verification.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf8"
        )
