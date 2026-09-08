"""M02 fixtures only in the five isolated local demo databases. No business rows."""

import json
import sys
import time

from module1_demo import LOCAL, configure


def seed(cfg):
    import psycopg
    import pymysql
    import oracledb
    import dmPython

    for kind, port, database, schema, user, secret in (
        ("postgresql",15432,"lightsql_demo","demo_sales","postgres","pg_password"),
        ("kingbase",15421,"sales_demo","light_demo","system","kingbase_password"),
    ):
        with psycopg.connect(host="127.0.0.1",port=port,dbname=database,user=user,password=cfg[secret],client_encoding="utf8") as conn:
            conn.execute(f"CREATE TABLE IF NOT EXISTS {schema}.m02_customers (tenant_id int, customer_id int, customer_name varchar(100) NOT NULL, PRIMARY KEY (tenant_id,customer_id))")
            conn.execute(f"CREATE TABLE IF NOT EXISTS {schema}.m02_orders (id int PRIMARY KEY, tenant_id int NOT NULL, customer_id int NOT NULL, amount numeric(12,2), CONSTRAINT m02_customer_fk FOREIGN KEY (tenant_id,customer_id) REFERENCES {schema}.m02_customers(tenant_id,customer_id))")
            conn.execute(f"COMMENT ON TABLE {schema}.m02_orders IS '销售订单 · 元数据验收'")
            conn.execute(f"COMMENT ON COLUMN {schema}.m02_orders.amount IS '订单金额（元）'")
            conn.execute(f"CREATE OR REPLACE VIEW {schema}.m02_order_summary AS SELECT customer_id, SUM(amount) AS total_amount FROM {schema}.m02_orders GROUP BY customer_id")
            conn.execute(f"GRANT SELECT ON {schema}.m02_orders, {schema}.m02_customers, {schema}.m02_order_summary TO light_reader")
        print(f"{kind}: fixtures ready")
    with pymysql.connect(host="127.0.0.1",port=13306,database="sales_demo",user="root",password=cfg["mysql_password"],charset="utf8mb4") as conn, conn.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS m02_customers (tenant_id int, customer_id int, customer_name varchar(100) NOT NULL, PRIMARY KEY (tenant_id,customer_id))")
        cur.execute("CREATE TABLE IF NOT EXISTS m02_orders (id int PRIMARY KEY, tenant_id int NOT NULL, customer_id int NOT NULL, amount decimal(12,2) COMMENT '订单金额（元）', CONSTRAINT m02_customer_fk FOREIGN KEY (tenant_id,customer_id) REFERENCES m02_customers(tenant_id,customer_id)) COMMENT='销售订单 · 元数据验收'")
        cur.execute("CREATE OR REPLACE VIEW m02_order_summary AS SELECT customer_id, SUM(amount) AS total_amount FROM m02_orders GROUP BY customer_id")
        conn.commit()
    print("mysql: fixtures ready")
    for kind in ("oracle", "dameng"):
        if kind == "oracle":
            conn = oracledb.connect(user="system",password=cfg["oracle_password"],dsn="127.0.0.1:11521/FREEPDB1")
        else:
            conn = dmPython.connect(user="SYSDBA",password=cfg["dameng_password"],server="127.0.0.1",port=15236,login_timeout=5000)
        try:
            with conn.cursor() as cur:
                for name, ddl in (
                    ("M02_CUSTOMERS", "TENANT_ID INT, CUSTOMER_ID INT, CUSTOMER_NAME VARCHAR(100) NOT NULL, PRIMARY KEY (TENANT_ID,CUSTOMER_ID)"),
                    ("M02_ORDERS", "ID INT PRIMARY KEY, TENANT_ID INT NOT NULL, CUSTOMER_ID INT NOT NULL, AMOUNT DECIMAL(12,2), CONSTRAINT M02_CUSTOMER_FK FOREIGN KEY (TENANT_ID,CUSTOMER_ID) REFERENCES LIGHT_DEMO.M02_CUSTOMERS(TENANT_ID,CUSTOMER_ID)"),
                ):
                    cur.execute(f"SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER='LIGHT_DEMO' AND TABLE_NAME='{name}'")
                    if not cur.fetchone():
                        cur.execute(f"CREATE TABLE LIGHT_DEMO.{name} ({ddl})")
                    cur.execute(f"GRANT SELECT ON LIGHT_DEMO.{name} TO LIGHT_READER")
                cur.execute("COMMENT ON TABLE LIGHT_DEMO.M02_ORDERS IS '销售订单 · 元数据验收'")
                cur.execute("COMMENT ON COLUMN LIGHT_DEMO.M02_ORDERS.AMOUNT IS '订单金额（元）'")
                cur.execute("CREATE OR REPLACE VIEW LIGHT_DEMO.M02_ORDER_SUMMARY AS SELECT CUSTOMER_ID, SUM(AMOUNT) AS TOTAL_AMOUNT FROM LIGHT_DEMO.M02_ORDERS GROUP BY CUSTOMER_ID")
                cur.execute("GRANT SELECT ON LIGHT_DEMO.M02_ORDER_SUMMARY TO LIGHT_READER")
            conn.commit()
        finally:
            conn.close()
        print(f"{kind}: fixtures ready")
    (LOCAL / "module2-fixtures.json").write_text(json.dumps({"ready": True}), encoding="utf-8")


def inspect():
    from sqlmodel import Session, select
    from app.core.db import engine
    from app.modules.datasources.models import DataSource
    from app.modules.catalog import introspection, service

    with Session(engine) as session:
        for source in session.exec(select(DataSource)).all():
            config, password = service.source_config(source)
            schema = {"postgresql":"demo_sales","mysql":"sales_demo","oracle":"LIGHT_DEMO","dameng":"LIGHT_DEMO","kingbase":"light_demo"}[config.database_type]
            try:
                assert schema in introspection.schemas(config,password)
                refs = [r for r in introspection.discover(config,password,schema) if r.name.lower().startswith("m02_")]
                tables = introspection.read_snapshot(config,password,refs,lambda: None)
                print(config.database_type, json.dumps([t.model_dump() for t in tables],ensure_ascii=False))
            except Exception as exc:
                # Local diagnosis reports type only; no raw connection errors.
                print(config.database_type, type(exc).__name__)
                raise


def acceptance(cfg):
    """Exercise the real HTTP API and separately running worker; leave history."""
    import httpx
    import psycopg

    with httpx.Client(base_url="http://127.0.0.1:8000/api/v1", timeout=30) as client:
        login = client.post("/login/access-token", data={"username":"admin@lightsql.example.com","password":"LightSQL-Demo-2026!"})
        login.raise_for_status()
        client.headers["Authorization"] = "Bearer " + login.json()["access_token"]
        sources = client.get("/datasources/").json()["data"]
        pg_source = None
        def sync(source):
            url = f"/catalog/{source['id']}"
            queued = client.post(url+"/sync")
            queued.raise_for_status()
            job_id = queued.json()["id"]
            for _ in range(45):
                job = next(j for j in client.get(url+"/jobs").json() if j["id"]==job_id)
                if job["status"] not in ("queued","running"):
                    assert job["status"]=="succeeded", job["message"]
                    return job
                time.sleep(1)
            raise RuntimeError("Demo worker did not finish in time")
        records=[]
        for source in sources:
            kind=source["database_type"]
            schema={"postgresql":"demo_sales","mysql":"sales_demo","oracle":"LIGHT_DEMO","dameng":"LIGHT_DEMO","kingbase":"light_demo"}[kind]
            port={"postgresql":15432,"mysql":13306,"oracle":11521,"dameng":15236,"kingbase":15421}[kind]
            assert source["host"]=="127.0.0.1" and source["port"]==port, "Not an isolated demo connection"
            url=f"/catalog/{source['id']}"
            catalog=client.get(url).json()
            refs=client.get(url+"/discover",params={"schema_name":schema})
            refs.raise_for_status()
            refs=[r for r in refs.json() if r["name"].lower().startswith("m02_")]
            assert len(refs)==3
            if not catalog["scope"]:
                saved=client.put(url+"/scope",json={"expected_revision":catalog["revision"],"expected_source_revision":source["revision"],"objects":refs})
                saved.raise_for_status()
            else:
                assert all(r in catalog["scope"] for r in refs), "M02 objects missing from customized scope; preserving it"
            job=sync(source)
            records.append({"database":kind,"objects":job["table_count"],"status":job["status"]})
            print(kind,job["status"],job["table_count"],flush=True)
            if kind=="postgresql": pg_source=source
        assert pg_source
        with psycopg.connect(host="127.0.0.1",port=15432,user="postgres",password=cfg["pg_password"],dbname="lightsql_demo",autocommit=True) as conn:
            exists=conn.execute("SELECT 1 FROM information_schema.columns WHERE table_schema='demo_sales' AND table_name='m02_orders' AND column_name='m02_acceptance_note'").fetchone()
            assert not exists, "Acceptance field already exists; preserving it"
            try:
                conn.execute("ALTER TABLE demo_sales.m02_orders ADD COLUMN m02_acceptance_note varchar(60)")
                conn.execute("COMMENT ON COLUMN demo_sales.m02_orders.amount IS '含税订单金额（元）'")
                changed=sync(pg_source)
                assert any(c["action"]=="added" and c["path"].endswith("m02_acceptance_note") for c in changed["changes"])
                assert any(c["action"]=="changed" and c["path"].endswith("amount") for c in changed["changes"])
            finally:
                conn.execute("ALTER TABLE demo_sales.m02_orders DROP COLUMN IF EXISTS m02_acceptance_note")
                conn.execute("COMMENT ON COLUMN demo_sales.m02_orders.amount IS '订单金额（元）'")
            restored=sync(pg_source)
            assert any(c["action"]=="removed" for c in restored["changes"])
            print("postgresql: live add/comment/remove diff verified; fixture restored",flush=True)
        (LOCAL/"module2-verification.json").write_text(json.dumps({"databases":records,"live_schema_diff":True},ensure_ascii=False,indent=2),encoding="utf8")


if __name__ == "__main__":
    cfg = configure()
    if len(sys.argv)>1 and sys.argv[1]=="seed":
        seed(cfg)
    elif len(sys.argv)>1 and sys.argv[1]=="acceptance":
        acceptance(cfg)
    else:
        inspect()
