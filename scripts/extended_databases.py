"""Seed and verify only the synthetic databases in compose.demo.yml."""

import json
import re
import sys
from decimal import Decimal
from pathlib import PurePosixPath

from module1_demo import LOCAL, configure


def quoted_password(value: str) -> str:
    # Generated local passwords only. Database DDL cannot bind password values.
    if not re.fullmatch(r"[A-Za-z0-9_!\-]+", value):
        raise ValueError("Unsupported character in generated demo password")
    return '"' + value + '"'


def register_source(kind, port, database, password, description):
    from sqlmodel import Session, select

    from app.core.config import settings
    from app.core.db import engine
    from app.models import User
    from app.modules.datasources.models import DataSource, DataSourceAudit, DataSourceInput, now
    from app.modules.datasources.service import encrypt_password, probe

    names = {"oracle": "Oracle 经营演示库", "dameng": "达梦 DM8 演示库", "kingbase": "人大金仓演示库"}
    body = DataSourceInput(
        name=names[kind], database_type=kind, host="127.0.0.1", port=port,
        database=database, username="LIGHT_READER" if kind != "kingbase" else "light_reader",
        description=description, tls_mode="disable",
    )
    result = probe(body, password)
    if not result.success:
        raise RuntimeError(f"{kind} application connector probe failed: {result.message}")
    with Session(engine) as session:
        source = session.exec(select(DataSource).where(DataSource.name == body.name)).first()
        if source is None and kind == "oracle":
            source = session.exec(select(DataSource).where(DataSource.name == "Oracle 待接入示例")).first()
        if source is None:
            source = DataSource(**body.model_dump(), name_key=body.name.casefold(), encrypted_password=encrypt_password(password))
        else:
            if source.host != "127.0.0.1" or source.port != port:
                raise RuntimeError("Demo source was customized; refusing to replace it")
            source.sqlmodel_update(body.model_dump())
            source.name_key = body.name.casefold()
            source.encrypted_password = encrypt_password(password)
            source.revision += 1
        source.status = "connected"
        source.last_tested_at = result.tested_at
        source.latency_ms = result.latency_ms
        source.last_error = None
        source.updated_at = now()
        session.add(source)
        actor = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER)).one()
        session.add(DataSourceAudit(actor_id=actor.id, datasource_id=source.id, action="demo_seeded"))
        session.commit()


def oracle(cfg):
    import oracledb

    dsn = "127.0.0.1:11521/FREEPDB1"
    password = cfg["domestic_reader_password"]
    with oracledb.connect(user="system", password=cfg["oracle_password"], dsn=dsn) as conn:
        conn.call_timeout = 10000
        with conn.cursor() as cur:
            cur.execute("SELECT BANNER_FULL FROM V$VERSION")
            version = cur.fetchone()[0]
            cur.execute("SELECT TABLESPACE_NAME FROM DBA_TABLESPACES WHERE TABLESPACE_NAME='LIGHTSQL_DEMO'")
            if cur.fetchone() is None:
                cur.execute("SELECT FILE_NAME FROM DBA_DATA_FILES WHERE TABLESPACE_NAME='SYSTEM'")
                datafile = str(PurePosixPath(cur.fetchone()[0]).parent / "lightsql_demo.dbf").replace("'", "''")
                cur.execute(f"CREATE TABLESPACE LIGHTSQL_DEMO DATAFILE '{datafile}' SIZE 20M AUTOEXTEND ON NEXT 5M MAXSIZE 100M")
            for user in ("LIGHT_DEMO", "LIGHT_READER"):
                cur.execute("SELECT USERNAME FROM ALL_USERS WHERE USERNAME=:name", name=user)
                if cur.fetchone() is None:
                    quota = " QUOTA 10M ON LIGHTSQL_DEMO" if user == "LIGHT_DEMO" else ""
                    cur.execute(f"CREATE USER {user} IDENTIFIED BY {quoted_password(password)} DEFAULT TABLESPACE LIGHTSQL_DEMO{quota}")
            cur.execute("SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER='LIGHT_DEMO' AND TABLE_NAME='ORDERS'")
            if cur.fetchone() is None:
                cur.execute("CREATE TABLE LIGHT_DEMO.ORDERS (ID NUMBER(10) PRIMARY KEY, CHANNEL VARCHAR2(100 CHAR), AMOUNT NUMBER(12,2))")
            for row in [(1, "线上直营", 1280), (2, "合作渠道", 860)]:
                cur.execute("MERGE INTO LIGHT_DEMO.ORDERS t USING (SELECT :1 ID, :2 CHANNEL, :3 AMOUNT FROM DUAL) s ON (t.ID=s.ID) WHEN NOT MATCHED THEN INSERT (ID, CHANNEL, AMOUNT) VALUES (s.ID,s.CHANNEL,s.AMOUNT)", row)
            cur.execute("GRANT CREATE SESSION TO LIGHT_READER")
            cur.execute("GRANT SELECT ON LIGHT_DEMO.ORDERS TO LIGHT_READER")
            conn.commit()
    with oracledb.connect(user="LIGHT_READER", password=password, dsn=dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT ID, CHANNEL, AMOUNT FROM LIGHT_DEMO.ORDERS ORDER BY ID")
            rows = cur.fetchall()
            assert len(rows) == 2 and sum(Decimal(str(r[2])) for r in rows) == 2140
            assert [r[1] for r in rows] == ["线上直营", "合作渠道"]
            try:
                cur.execute("UPDATE LIGHT_DEMO.ORDERS SET AMOUNT=AMOUNT WHERE 1=0")
            except oracledb.DatabaseError as exc:
                if exc.args[0].code not in (1031, 41900):
                    raise RuntimeError(f"Unexpected Oracle UPDATE rejection: {exc.args[0].code}") from None
            else:
                raise RuntimeError("Demo reader unexpectedly has UPDATE permission")
            finally:
                conn.rollback()
    register_source("oracle", 11521, "FREEPDB1", password, "合成数据 · Oracle Free Docker 实库 · 专用只读账号 · LIGHT_DEMO.ORDERS")
    return {"database": "oracle", "version": version, "rows": len(rows), "total": "2140.00", "reader_update_denied": True}


def dameng(cfg):
    import dmPython

    password = cfg["domestic_reader_password"]
    kwargs = dict(server="127.0.0.1", port=15236, login_timeout=5000, connection_timeout=10, autoCommit=False)
    with dmPython.connect(user="SYSDBA", password=cfg["dameng_password"], **kwargs) as conn, conn.cursor() as cur:
        cur.execute("SELECT BANNER FROM V$VERSION")
        version = cur.fetchone()[0]
        for user in ("LIGHT_DEMO", "LIGHT_READER"):
            cur.execute("SELECT USERNAME FROM ALL_USERS WHERE USERNAME=?", (user,))
            if cur.fetchone() is None:
                cur.execute(f"CREATE USER {user} IDENTIFIED BY {quoted_password(password)}")
        cur.execute("SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER='LIGHT_DEMO' AND TABLE_NAME='ORDERS'")
        if cur.fetchone() is None:
            cur.execute("CREATE TABLE LIGHT_DEMO.ORDERS (ID INT PRIMARY KEY, CHANNEL VARCHAR(100), AMOUNT DECIMAL(12,2))")
        for row in [(1, "线上直营", 1280), (2, "合作渠道", 860)]:
            cur.execute("SELECT ID FROM LIGHT_DEMO.ORDERS WHERE ID=?", (row[0],))
            if cur.fetchone() is None:
                cur.execute("INSERT INTO LIGHT_DEMO.ORDERS (ID, CHANNEL, AMOUNT) VALUES (?, ?, ?)", row)
        cur.execute("GRANT CREATE SESSION TO LIGHT_READER")
        cur.execute("GRANT SELECT ON LIGHT_DEMO.ORDERS TO LIGHT_READER")
        conn.commit()
    with dmPython.connect(user="LIGHT_READER", password=password, **kwargs) as conn, conn.cursor() as cur:
        cur.execute("SELECT ID, CHANNEL, AMOUNT FROM LIGHT_DEMO.ORDERS ORDER BY ID")
        rows = cur.fetchall()
        assert len(rows) == 2 and sum(Decimal(str(r[2])) for r in rows) == 2140
        assert [r[1] for r in rows] == ["线上直营", "合作渠道"]
        try:
            cur.execute("UPDATE LIGHT_DEMO.ORDERS SET AMOUNT=AMOUNT WHERE 1=0")
        except dmPython.DatabaseError as exc:
            if "[CODE:-5503]" not in str(exc):
                raise RuntimeError("Expected DM insufficient-UPDATE-privilege error -5503") from None
        else:
            raise RuntimeError("Demo reader unexpectedly has UPDATE permission")
        finally:
            conn.rollback()
    register_source("dameng", 15236, "LIGHT_DEMO", password, "合成数据 · DM8 官方 Docker 实库 · 专用只读账号 · LIGHT_DEMO.ORDERS")
    return {"database": "dameng", "version": version, "rows": len(rows), "total": "2140.00", "reader_update_denied": True}


def kingbase(cfg):
    import psycopg
    from psycopg import sql

    password = cfg["domestic_reader_password"]
    kwargs = dict(host="127.0.0.1", port=15421, connect_timeout=5, sslmode="disable", client_encoding="utf8")
    with psycopg.connect(user="system", password=cfg["kingbase_password"], dbname="test", autocommit=True, **kwargs) as conn:
        version = conn.execute("SELECT version()").fetchone()[0]
        license_days = conn.execute("SELECT get_license_validdays()").fetchone()[0]
        if license_days <= 0 and license_days != -2:
            raise RuntimeError("Kingbase demo license is not currently valid")
        if conn.execute("SELECT 1 FROM pg_roles WHERE rolname='light_reader'").fetchone() is None:
            conn.execute(sql.SQL("CREATE ROLE light_reader LOGIN PASSWORD {}").format(sql.Literal(password)))
        if conn.execute("SELECT 1 FROM pg_database WHERE datname='sales_demo'").fetchone() is None:
            conn.execute("CREATE DATABASE sales_demo ENCODING 'UTF8' TEMPLATE template0 LC_COLLATE 'C' LC_CTYPE 'C'")
    with psycopg.connect(user="system", password=cfg["kingbase_password"], dbname="sales_demo", **kwargs) as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS light_demo")
        conn.execute("CREATE TABLE IF NOT EXISTS light_demo.orders (id int primary key, channel text, amount numeric(12,2))")
        conn.execute("INSERT INTO light_demo.orders VALUES (1, '线上直营', 1280), (2, '合作渠道', 860) ON CONFLICT DO NOTHING")
        conn.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
        conn.execute("GRANT CONNECT ON DATABASE sales_demo TO light_reader")
        conn.execute("GRANT USAGE ON SCHEMA light_demo TO light_reader")
        conn.execute("GRANT SELECT ON light_demo.orders TO light_reader")
    with psycopg.connect(user="light_reader", password=password, dbname="sales_demo", **kwargs) as conn:
        rows = conn.execute("SELECT id, channel, amount FROM light_demo.orders ORDER BY id").fetchall()
        assert len(rows) == 2 and sum(Decimal(str(r[2])) for r in rows) == 2140
        assert [r[1] for r in rows] == ["线上直营", "合作渠道"]
        try:
            conn.execute("UPDATE light_demo.orders SET amount=amount WHERE 1=0")
        except psycopg.errors.InsufficientPrivilege:
            pass
        else:
            raise RuntimeError("Demo reader unexpectedly has UPDATE permission")
        finally:
            conn.rollback()
    register_source("kingbase", 15421, "sales_demo", password, "合成数据 · KingbaseES V9 Docker 实库（PG 兼容模式）· 专用只读账号 · light_demo.orders")
    return {"database": "kingbase", "version": version, "rows": len(rows), "total": "2140.00", "reader_update_denied": True, "license_remaining_days": license_days}


if __name__ == "__main__":
    cfg = configure()
    try:
        action = sys.argv[1]
        result = {"oracle": oracle, "dameng": dameng, "kingbase": kingbase}[action](cfg)
        (LOCAL / f"{action}-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        message = str(exc)
        for value in cfg.values():
            if isinstance(value, str):
                message = message.replace(value, "[REDACTED]")
        print(f"Verification failed ({type(exc).__name__}): {message}")
        sys.exit(1)
