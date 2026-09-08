"""Short-lived, read-only DB-API cursors shared by probes and catalog readers."""

import ssl
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from app.modules.datasources.models import DataSourceInput


@contextmanager
def readonly_cursor(source: DataSourceInput, password: str) -> Iterator[Any]:
    from app.modules.datasources.service import check_host

    check_host(source.host)
    if source.database_type in ("postgresql", "kingbase"):
        import psycopg

        conn = psycopg.connect(
            host=source.host,
            port=source.port,
            dbname=source.database,
            user=source.username,
            password=password,
            connect_timeout=5,
            sslmode=source.tls_mode,
            client_encoding="utf8",
            options="-c statement_timeout=5000 -c default_transaction_read_only=on",
        )
    elif source.database_type == "mysql":
        import pymysql

        conn = pymysql.connect(
            host=source.host,
            port=source.port,
            database=source.database,
            user=source.username,
            password=password,
            connect_timeout=5,
            read_timeout=5,
            write_timeout=5,
            charset="utf8mb4",
            ssl=ssl.create_default_context()
            if source.tls_mode == "verify-full"
            else None,
            ssl_disabled=source.tls_mode == "disable",
            local_infile=False,
        )
    elif source.database_type == "oracle":
        import oracledb

        params = oracledb.ConnectParams(
            host=source.host,
            port=source.port,
            service_name=source.database,
            protocol="tcps" if source.tls_mode == "verify-full" else "tcp",
            tcp_connect_timeout=5,
            retry_count=0,
            ssl_server_dn_match=True,
        )
        conn = oracledb.connect(user=source.username, password=password, params=params)
        conn.call_timeout = 5000
    else:
        if source.tls_mode == "verify-full":
            raise ValueError(
                "当前达梦连接器尚未适配证书校验；仅在可信本地测试环境中关闭 TLS 后连接"
            )
        import dmPython  # ty: ignore[unresolved-import]

        conn = dmPython.connect(
            server=f"[{source.host}]" if ":" in source.host else source.host,
            port=source.port,
            schema=source.database,
            user=source.username,
            password=password,
            login_timeout=5000,
            connection_timeout=5,
            access_mode=dmPython.DSQL_MODE_READ_ONLY,
            autoCommit=False,
        )
    try:
        with conn.cursor() as cursor:
            if source.database_type in ("mysql", "oracle"):
                cursor.execute("SET TRANSACTION READ ONLY")
            yield cursor
    finally:
        try:
            conn.rollback()
        finally:
            conn.close()
