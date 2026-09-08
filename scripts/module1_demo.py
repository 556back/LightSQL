"""Synthetic local acceptance environment with isolated database credentials."""

import json
import os
from pathlib import Path
import secrets
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / ".local"
CONFIG = LOCAL / "demo.json"


def prepare():
    from cryptography.fernet import Fernet

    LOCAL.mkdir(exist_ok=True)
    cfg = json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
    for key in ("pg_password", "mysql_password", "reader_password", "secret_key"):
        cfg.setdefault(key, secrets.token_urlsafe(32))
    cfg.setdefault("encryption_key", Fernet.generate_key().decode())
    for key in ("oracle_password", "dameng_password", "kingbase_password", "domestic_reader_password"):
        cfg.setdefault(key, "Ls_" + secrets.token_hex(10) + "Aa9!")
    CONFIG.write_text(json.dumps(cfg), encoding="utf-8")
    (LOCAL / "demo.env").write_text(
        f"DEMO_POSTGRES_PASSWORD={cfg['pg_password']}\n"
        f"DEMO_MYSQL_PASSWORD={cfg['mysql_password']}\n"
        f"DEMO_ORACLE_PASSWORD={cfg['oracle_password']}\n"
        f"DEMO_DAMENG_PASSWORD={cfg['dameng_password']}\n"
        f"DEMO_KINGBASE_PASSWORD={cfg['kingbase_password']}\n",
        encoding="utf-8",
    )
    return cfg


def configure():
    cfg = prepare()
    os.environ.update({
        "DATABASE_URL": f"postgresql://postgres:{cfg['pg_password']}@127.0.0.1:15432/lightsql_demo",
        "PROJECT_NAME": "LightSQL",
        "SECRET_KEY": cfg["secret_key"],
        "FIRST_SUPERUSER": "admin@lightsql.example.com",
        "FIRST_SUPERUSER_PASSWORD": "LightSQL-Demo-2026!",
        "DATASOURCE_ENCRYPTION_KEY": cfg["encryption_key"],
        "DATASOURCE_ALLOWED_HOSTS": '["localhost","127.0.0.1"]',
        "FRONTEND_HOST": "http://localhost:5173",
        "ENABLE_PUBLIC_SIGNUP": "false",
        "SMTP_HOST": "",
        "FASTAPI_ENV": "development",
        "SENTRY_DSN": "",
    })
    sys.path.insert(0, str(ROOT / "backend"))
    os.chdir(ROOT / "backend")
    # Settings ignore empty environment values, so explicitly disable outbound
    # services for this isolated demo even if ../.env configures them.
    from app.core.config import settings
    settings.SMTP_HOST = None
    settings.EMAILS_FROM_EMAIL = None
    settings.SENTRY_DSN = None
    return cfg


def seed():
    cfg = configure()
    import psycopg
    from psycopg import sql
    import pymysql
    from sqlmodel import Session, select
    from app.core.db import engine, init_db
    from app.modules.datasources.models import DataSource, DataSourceCreate, DataSourceInput
    from app.modules.datasources.service import encrypt_password, probe

    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True)
    with Session(engine) as session:
        init_db(session)
    with psycopg.connect(host="127.0.0.1", port=15432, user="postgres", password=cfg["pg_password"], dbname="lightsql_demo") as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS demo_sales")
        conn.execute("CREATE TABLE IF NOT EXISTS demo_sales.orders (id int primary key, channel text, amount numeric(12,2))")
        conn.execute("INSERT INTO demo_sales.orders VALUES (1, '线上直营', 1280), (2, '合作渠道', 860) ON CONFLICT DO NOTHING")
        if not conn.execute("SELECT 1 FROM pg_roles WHERE rolname='light_reader'").fetchone():
            conn.execute(sql.SQL("CREATE ROLE light_reader LOGIN PASSWORD {}").format(sql.Literal(cfg["reader_password"])))
        conn.execute("GRANT USAGE ON SCHEMA demo_sales TO light_reader")
        conn.execute("GRANT SELECT ON ALL TABLES IN SCHEMA demo_sales TO light_reader")
    with pymysql.connect(host="127.0.0.1", port=13306, user="root", password=cfg["mysql_password"], database="sales_demo") as conn, conn.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS orders (id int primary key, channel varchar(100), amount decimal(12,2))")
        cur.execute("INSERT IGNORE INTO orders VALUES (1, '线上直营', 1280), (2, '合作渠道', 860)")
        cur.execute("CREATE USER IF NOT EXISTS 'light_reader'@'%%' IDENTIFIED BY %s", (cfg["reader_password"],))
        cur.execute("GRANT SELECT ON sales_demo.* TO 'light_reader'@'%'")
        conn.commit()
    fixtures = [
        ("经营分析演示库", "postgresql", 15432, "lightsql_demo", "合成数据 · PostgreSQL 本地只读演示连接"),
        ("销售业务演示库", "mysql", 13306, "sales_demo", "合成数据 · MySQL 本地只读演示连接"),
    ]
    with Session(engine) as session:
        for name, kind, port, database, description in fixtures:
            if session.exec(select(DataSource).where(DataSource.name == name)).first():
                continue
            body = DataSourceCreate(name=name, database_type=kind, host="127.0.0.1", port=port, database=database, username="light_reader", description=description, tls_mode="disable", password=cfg["reader_password"])
            source = DataSource(**body.model_dump(exclude={"password"}), name_key=name.casefold(), encrypted_password=encrypt_password(cfg["reader_password"]))
            if kind != "oracle":
                result = probe(DataSourceInput.model_validate(body), cfg["reader_password"])
                source.status = "connected" if result.success else "error"
                source.last_tested_at, source.latency_ms = result.tested_at, result.latency_ms
                source.last_error = None if result.success else result.message
            session.add(source)
        session.commit()
    print("Isolated demo prepared. No production data used.")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "prepare"
    if action == "prepare":
        prepare()
        print("Demo credentials prepared under .local (gitignored).")
    elif action == "seed":
        seed()
    elif action == "api":
        configure()
        import uvicorn
        uvicorn.run("app.main:app", host="127.0.0.1", port=8000)
    elif action == "worker":
        configure()
        from app.modules.catalog.worker import main
        main()
    elif action == "integration-worker":
        configure()
        from app.modules.integration.worker import main
        main()
    elif action == "query-worker":
        configure()
        from app.modules.query.worker import main
        main()
    elif action == "migrate":
        configure()
        subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True)
    elif action == "openapi":
        configure()
        from app.main import app
        (ROOT / "frontend/openapi.json").write_text(json.dumps(app.openapi()), encoding="utf-8")
    elif action == "test":
        configure()
        subprocess.run([sys.executable, "-m", "pytest", "--confcutdir=tests/modules", "tests/modules", "-q"], check=True)
