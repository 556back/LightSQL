"""Bounded DB-API execution in a disposable process with acknowledged cleanup."""

import json
import math
import ssl
import threading
import time
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from app.modules.datasources.models import DataSourceInput
from app.modules.datasources.service import check_host
from app.modules.query.compiler import CompiledQuery
from app.modules.query.models import QueryPlan, SqlPlan, parse_plan

MAX_RESULT_BYTES = 2_000_000
MAX_CELL_BYTES = 16_000


def open_connection(source: DataSourceInput, password: str, timeout: int):
    check_host(source.host)
    if source.database_type in ("postgresql", "kingbase"):
        import psycopg

        return psycopg.connect(
            host=source.host,
            port=source.port,
            dbname=source.database,
            user=source.username,
            password=password,
            connect_timeout=5,
            sslmode=source.tls_mode,
            client_encoding="utf8",
            options=f"-c statement_timeout={timeout * 1000} -c default_transaction_read_only=on",
        )
    if source.database_type == "mysql":
        import pymysql

        return pymysql.connect(
            host=source.host,
            port=source.port,
            database=source.database,
            user=source.username,
            password=password,
            connect_timeout=5,
            read_timeout=timeout + 5,
            write_timeout=5,
            charset="utf8mb4",
            ssl=ssl.create_default_context()
            if source.tls_mode == "verify-full"
            else None,
            ssl_disabled=source.tls_mode == "disable",
            local_infile=False,
        )
    if source.database_type == "oracle":
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
        conn.call_timeout = timeout * 1000
        return conn
    # dmPython 2.5.38 does not expose cancel or a statement timeout. Keep the
    # execution gate closed until a tested least-privilege adapter is available.
    raise ValueError("达梦查询执行尚未开放：当前驱动缺少已验证的取消/语句限时能力")


def serialize_cell(value: Any) -> str | bool | None:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("不支持非有限数值")
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("不支持非有限数值")
        return str(value)
    if isinstance(value, str):
        if len(value.encode("utf8")) > MAX_CELL_BYTES:
            raise ValueError("单元格超过 16 KB，请缩小查询范围")
        return value
    raise ValueError("结果包含暂不支持的二进制、大对象或复合类型")


def execute(
    source: DataSourceInput,
    password: str,
    compiled: CompiledQuery,
    plan: QueryPlan | SqlPlan,
    stop,
    *,
    max_bytes: int = MAX_RESULT_BYTES,
) -> dict:
    conn = None
    canceller = None
    done = threading.Event()
    outcome: dict = {
        "status": "failed",
        "message": "查询执行失败，请管理员检查连接及字段兼容性",
        "cleaned": True,
    }
    started = time.monotonic()
    attempted = False
    try:
        conn = open_connection(source, password, plan.timeout_seconds)
        if source.database_type == "mysql":
            with conn.cursor() as setup:
                setup.execute(
                    "SET SESSION MAX_EXECUTION_TIME = %s",
                    (plan.timeout_seconds * 1000,),
                )
                setup.execute("SET TRANSACTION READ ONLY")
            import pymysql.cursors

            cursor = conn.cursor(pymysql.cursors.SSCursor)
        else:
            cursor = conn.cursor()
            if source.database_type == "oracle":
                cursor.execute("ALTER SESSION SET TIME_ZONE = '+00:00'")
                cursor.execute("SET TRANSACTION READ ONLY")
                cursor.arraysize = 50

        def interrupt():
            while not done.wait(0.1):
                if stop.is_set() or time.monotonic() - started >= plan.timeout_seconds:
                    try:
                        if source.database_type in ("postgresql", "kingbase"):
                            conn.cancel_safe(timeout=3)
                        elif source.database_type == "oracle":
                            conn.cancel()
                        else:
                            # Kill only this task's live connection, with the same user.
                            killer = open_connection(source, password, 3)
                            try:
                                with killer.cursor() as control:
                                    control.execute(
                                        "KILL QUERY %s", (conn.thread_id(),)
                                    )
                            finally:
                                killer.close()
                    except Exception:
                        pass  # Main path must still acknowledge rollback/cleanup.
                    return

        canceller = threading.Thread(target=interrupt, daemon=True)
        canceller.start()
        if stop.is_set():
            outcome.update(status="cancelled", message="查询已取消")
        else:
            attempted = True
            if source.database_type == "oracle":
                cursor.execute(compiled.sql, compiled.parameters, fetch_decimals=True)
            else:
                cursor.execute(compiled.sql, compiled.parameters)
            if not cursor.description or len(cursor.description) != len(
                compiled.columns
            ):
                raise ValueError("结果字段与查询计划不一致")
            rows, size, truncated = [], 0, False
            while True:
                if stop.is_set() or time.monotonic() - started >= plan.timeout_seconds:
                    break
                row = cursor.fetchone()
                if row is None:
                    break
                if len(rows) >= plan.limit:
                    truncated = True
                    break
                data = []
                for value, column in zip(row, compiled.columns, strict=True):
                    if column.value_type == "auto" and value is not None:
                        column.value_type = (
                            "boolean"
                            if isinstance(value, bool)
                            else "number"
                            if isinstance(value, (int, float, Decimal))
                            else "datetime"
                            if isinstance(value, datetime)
                            else "date"
                            if isinstance(value, date)
                            else "string"
                        )
                    if isinstance(value, datetime) and column.value_type == "date":
                        value = value.date()
                    elif (
                        isinstance(value, datetime)
                        and column.timezone
                        and value.tzinfo is None
                    ):
                        value = value.replace(tzinfo=ZoneInfo(column.timezone))
                    data.append(serialize_cell(value))
                row_bytes = len(json.dumps(data, ensure_ascii=False).encode("utf8"))
                if size + row_bytes > max_bytes:
                    truncated = True
                    break
                rows.append(data)
                size += row_bytes
            outcome.update(
                status="succeeded",
                message="查询完成" if not truncated else "查询完成，结果已截断",
                result={
                    "columns": [c.model_dump() for c in compiled.columns],
                    "rows": rows,
                    "truncated": truncated,
                    "notes": compiled.notes,
                },
                row_count=len(rows),
                result_bytes=size,
                truncated=truncated,
            )
    except ValueError as exc:
        outcome["message"] = str(exc)[:300]
    except Exception:
        pass  # Driver exceptions may contain passwords, SQL or private values.
    finally:
        done.set()
        if canceller:
            canceller.join(timeout=4)
        if conn is not None:
            try:
                # A successful rollback is a server acknowledgement, not merely
                # a local socket close. Never release quota on an uncertain stop.
                conn.rollback()
                conn.close()
            except Exception:
                outcome["cleaned"] = not attempted
                try:
                    conn.close()
                except Exception:
                    pass
        if stop.is_set():
            outcome.update(status="cancelled", message="查询已取消，源库操作已结束")
            outcome.pop("result", None)
        elif time.monotonic() - started >= plan.timeout_seconds:
            outcome.update(
                status="timed_out", message="查询超过执行时间限制，源库操作已结束"
            )
            outcome.pop("result", None)
        if not outcome["cleaned"] or (canceller and canceller.is_alive()):
            outcome.update(
                status="cleanup_pending",
                message="尚未确认源库清理完成，已暂停该数据源的新查询",
                cleaned=False,
            )
            outcome.pop("result", None)
        outcome["elapsed_ms"] = round((time.monotonic() - started) * 1000)
    return outcome


def child_execute(
    source: dict, password: str, compiled: CompiledQuery, plan: dict, stop, pipe
) -> None:
    entered_at = time.monotonic()
    try:
        outcome = execute(
            DataSourceInput.model_validate(source),
            password,
            compiled,
            parse_plan(plan),
            stop,
        )
        outcome["_child_entered_at"] = entered_at
        pipe.send(outcome)
    except BaseException:
        pipe.send(
            {
                "status": "cleanup_pending",
                "message": "执行进程异常退出，等待源库清理确认",
                "cleaned": False,
                "_child_entered_at": entered_at,
            }
        )
    finally:
        pipe.close()
