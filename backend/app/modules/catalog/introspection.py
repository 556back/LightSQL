"""Fixed catalog queries only. Never sample rows or execute supplied SQL."""

from collections.abc import Callable
from typing import Any

from app.modules.catalog.models import ColumnMeta, ForeignKeyMeta, ObjectRef, TableMeta
from app.modules.datasources.connection import readonly_cursor
from app.modules.datasources.models import DataSourceInput


class CatalogReadError(Exception):
    pass


PG_OBJECTS = """SELECT n.nspname, c.relname, CASE WHEN c.relkind='v' THEN 'view' ELSE 'table' END
FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
WHERE c.relkind IN ('r','p','v') AND n.nspname NOT IN ('pg_catalog','information_schema','sys_catalog','sysmac')
AND n.nspname NOT LIKE 'pg_toast%%' AND n.nspname NOT LIKE 'pg_temp_%%'
AND has_schema_privilege(n.oid, 'USAGE') AND has_table_privilege(c.oid, 'SELECT')
"""
MYSQL_OBJECTS = """
SELECT TABLE_SCHEMA, TABLE_NAME, CASE WHEN TABLE_TYPE='VIEW' THEN 'view' ELSE 'table' END
FROM information_schema.TABLES
WHERE TABLE_SCHEMA NOT IN ('mysql','sys','information_schema','performance_schema')
AND TABLE_TYPE IN ('BASE TABLE','VIEW')
"""
ORACLE_OBJECTS = """
SELECT OWNER, TABLE_NAME, 'table' FROM ALL_TABLES
WHERE OWNER NOT IN ('SYS','SYSTEM','SYSDBA','SYSAUDITOR','SYSSSO','CTXSYS','MDSYS','XDB','DBSNMP','OUTLN','ORDDATA','ORDSYS')
UNION ALL
SELECT OWNER, VIEW_NAME, 'view' FROM ALL_VIEWS
WHERE OWNER NOT IN ('SYS','SYSTEM','SYSDBA','SYSAUDITOR','SYSSSO','CTXSYS','MDSYS','XDB','DBSNMP','OUTLN','ORDDATA','ORDSYS')
"""


def query(cursor: Any, sql: str, params: tuple = (), *, limit: int = 5000) -> list:
    cursor.execute(sql, params) if params else cursor.execute(sql)
    rows = cursor.fetchmany(limit + 1)
    if len(rows) > limit:
        raise CatalogReadError("元数据超过单次读取上限，请缩小数据库账号可见范围")
    return rows


def object_query(source: DataSourceInput) -> str:
    if source.database_type in ("postgresql", "kingbase"):
        return PG_OBJECTS
    if source.database_type == "mysql":
        return MYSQL_OBJECTS
    return ORACLE_OBJECTS


def placeholder(source: DataSourceInput, index: int) -> str:
    if source.database_type == "oracle":
        return f":{index}"
    return "?" if source.database_type == "dameng" else "%s"


def schemas(source: DataSourceInput, password: str) -> list[str]:
    with readonly_cursor(source, password) as cursor:
        # Alias the union so schema discovery doesn't materialize every object.
        column = (
            "nspname"
            if source.database_type in ("postgresql", "kingbase")
            else "TABLE_SCHEMA"
            if source.database_type == "mysql"
            else "OWNER"
        )
        rows = query(
            cursor,
            f"SELECT DISTINCT {column} FROM ({object_query(source)}) obj ORDER BY {column}",
            limit=500,
        )
        return [str(row[0]) for row in rows]


def discover_on(
    cursor: Any, source: DataSourceInput, schema_name: str
) -> list[ObjectRef]:
    column = (
        "nspname"
        if source.database_type in ("postgresql", "kingbase")
        else "TABLE_SCHEMA"
        if source.database_type == "mysql"
        else "OWNER"
    )
    rows = query(
        cursor,
        f"SELECT * FROM ({object_query(source)}) obj WHERE {column}={placeholder(source, 1)} ORDER BY 2",
        (schema_name,),
        limit=2000,
    )
    return [ObjectRef(schema_name=str(s), name=str(n), kind=k) for s, n, k in rows]


def discover(
    source: DataSourceInput, password: str, schema_name: str
) -> list[ObjectRef]:
    with readonly_cursor(source, password) as cursor:
        return discover_on(cursor, source, schema_name)


def postgres_table(cursor: Any, ref: ObjectRef) -> TableMeta:
    params = (ref.schema_name, ref.name)
    rows = query(
        cursor,
        """
        SELECT a.attname, a.attnum, format_type(a.atttypid,a.atttypmod), NOT a.attnotnull,
          COALESCE(col_description(c.oid,a.attnum),''),
          EXISTS(SELECT 1 FROM pg_constraint p WHERE p.conrelid=c.oid AND p.contype='p' AND a.attnum=ANY(p.conkey))
        FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid
        JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname=%s AND c.relname=%s AND a.attnum>0 AND NOT a.attisdropped
        ORDER BY a.attnum
    """,
        params,
        limit=1600,
    )
    comments = query(
        cursor,
        "SELECT COALESCE(obj_description(c.oid,'pg_class'),'') FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname=%s AND c.relname=%s",
        params,
    )
    keys = query(
        cursor,
        """
        SELECT fk.conname, a.attname, tn.nspname, tc.relname, ta.attname, idx.i
        FROM pg_constraint fk JOIN pg_class c ON c.oid=fk.conrelid
        JOIN pg_namespace n ON n.oid=c.relnamespace
        JOIN pg_class tc ON tc.oid=fk.confrelid JOIN pg_namespace tn ON tn.oid=tc.relnamespace
        CROSS JOIN LATERAL generate_subscripts(fk.conkey,1) idx(i)
        JOIN pg_attribute a ON a.attrelid=c.oid AND a.attnum=fk.conkey[idx.i]
        JOIN pg_attribute ta ON ta.attrelid=tc.oid AND ta.attnum=fk.confkey[idx.i]
        WHERE n.nspname=%s AND c.relname=%s AND fk.contype='f'
        ORDER BY fk.conname,idx.i
    """,
        params,
    )
    return table_result(ref, rows, comments, keys)


def mysql_table(cursor: Any, ref: ObjectRef) -> TableMeta:
    params = (ref.schema_name, ref.name)
    rows = query(
        cursor,
        """
        SELECT COLUMN_NAME, ORDINAL_POSITION, COLUMN_TYPE, IS_NULLABLE='YES', COLUMN_COMMENT, COLUMN_KEY='PRI'
        FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s ORDER BY ORDINAL_POSITION
    """,
        params,
        limit=1600,
    )
    comments = query(
        cursor,
        "SELECT TABLE_COMMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s",
        params,
    )
    if ref.kind == "view":
        comments = [("",)]  # MySQL's TABLE_COMMENT='VIEW' is not a user comment.
    keys = query(
        cursor,
        """
        SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_SCHEMA, REFERENCED_TABLE_NAME,
          REFERENCED_COLUMN_NAME, ORDINAL_POSITION FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND REFERENCED_TABLE_NAME IS NOT NULL
        ORDER BY CONSTRAINT_NAME, ORDINAL_POSITION
    """,
        params,
    )
    return table_result(ref, rows, comments, keys)


def oracle_table(cursor: Any, source: DataSourceInput, ref: ObjectRef) -> TableMeta:
    # Only generated placeholders are formatted. Identifiers remain bind values.
    p1, p2 = placeholder(source, 1), placeholder(source, 2)
    params = (ref.schema_name, ref.name)
    native = query(
        cursor,
        f"""
        SELECT c.COLUMN_NAME,c.COLUMN_ID,c.DATA_TYPE,c.NULLABLE,cc.COMMENTS,
          c.DATA_PRECISION,c.DATA_SCALE,c.CHAR_LENGTH,c.CHAR_USED
        FROM ALL_TAB_COLUMNS c LEFT JOIN ALL_COL_COMMENTS cc
          ON cc.OWNER=c.OWNER AND cc.TABLE_NAME=c.TABLE_NAME AND cc.COLUMN_NAME=c.COLUMN_NAME
        WHERE c.OWNER={p1} AND c.TABLE_NAME={p2} ORDER BY c.COLUMN_ID
    """,
        params,
        limit=1600,
    )
    pk_rows = query(
        cursor,
        f"""
        SELECT cc.COLUMN_NAME FROM ALL_CONSTRAINTS c JOIN ALL_CONS_COLUMNS cc
          ON cc.OWNER=c.OWNER AND cc.CONSTRAINT_NAME=c.CONSTRAINT_NAME AND cc.TABLE_NAME=c.TABLE_NAME
        WHERE c.OWNER={p1} AND c.TABLE_NAME={p2} AND c.CONSTRAINT_TYPE='P'
    """,
        params,
    )
    pk = {r[0] for r in pk_rows}
    if source.database_type == "dameng":
        # DM8's ALL_CONS_COLUMNS may be empty for a SELECT-only user, even
        # while ALL_CONSTRAINTS/ALL_IND_COLUMNS expose the authorized keys.
        # Primary keys have a definite backing index; don't guess FK mappings.
        pk = {
            r[0]
            for r in query(
                cursor,
                """
            SELECT ic.COLUMN_NAME FROM ALL_CONSTRAINTS c JOIN ALL_IND_COLUMNS ic
              ON ic.INDEX_OWNER=c.INDEX_OWNER AND ic.INDEX_NAME=c.INDEX_NAME
              AND ic.TABLE_OWNER=c.OWNER AND ic.TABLE_NAME=c.TABLE_NAME
            WHERE c.OWNER=? AND c.TABLE_NAME=? AND c.CONSTRAINT_TYPE='P'
        """,
                params,
            )
        }
    rows = []
    for (
        name,
        position,
        dtype,
        nullable,
        comment,
        precision,
        scale,
        length,
        char_used,
    ) in native:
        if dtype in ("NUMBER", "DECIMAL", "NUMERIC") and precision is not None:
            dtype = f"{dtype}({int(precision)},{int(scale or 0)})"
        elif dtype in ("VARCHAR2", "VARCHAR", "CHAR", "NVARCHAR2", "NCHAR") and length:
            dtype = f"{dtype}({int(length)}{' CHAR' if char_used == 'C' else ' BYTE'})"
        rows.append((name, position, dtype, nullable == "Y", comment, name in pk))
    comments = query(
        cursor,
        f"SELECT COMMENTS FROM ALL_TAB_COMMENTS WHERE OWNER={p1} AND TABLE_NAME={p2}",
        params,
    )
    keys = query(
        cursor,
        f"""
        SELECT fk.CONSTRAINT_NAME,fc.COLUMN_NAME,pk.OWNER,pk.TABLE_NAME,pc.COLUMN_NAME,fc.POSITION
        FROM ALL_CONSTRAINTS fk JOIN ALL_CONS_COLUMNS fc
          ON fc.OWNER=fk.OWNER AND fc.CONSTRAINT_NAME=fk.CONSTRAINT_NAME AND fc.TABLE_NAME=fk.TABLE_NAME
        JOIN ALL_CONSTRAINTS pk ON pk.OWNER=fk.R_OWNER AND pk.CONSTRAINT_NAME=fk.R_CONSTRAINT_NAME
        JOIN ALL_CONS_COLUMNS pc ON pc.OWNER=pk.OWNER AND pc.CONSTRAINT_NAME=pk.CONSTRAINT_NAME
          AND pc.TABLE_NAME=pk.TABLE_NAME AND pc.POSITION=fc.POSITION
        WHERE fk.OWNER={p1} AND fk.TABLE_NAME={p2} AND fk.CONSTRAINT_TYPE='R'
        ORDER BY fk.CONSTRAINT_NAME,fc.POSITION
    """,
        params,
    )
    result = table_result(ref, rows, comments, keys)
    constraints = query(
        cursor,
        f"SELECT CONSTRAINT_NAME,CONSTRAINT_TYPE FROM ALL_CONSTRAINTS WHERE OWNER={p1} AND TABLE_NAME={p2} AND CONSTRAINT_TYPE IN ('P','R')",
        params,
    )
    fk_names = {fk.name for fk in result.foreign_keys}
    missing_fk = [
        name for name, kind in constraints if kind == "R" and name not in fk_names
    ]
    if missing_fk:
        result.warnings.append(
            f"数据库报告 {len(missing_fk)} 个外键，但当前账号的字典未提供完整字段映射；这些关联暂不可用于问数，请 DBA 核对元数据访问权限。"
        )
    if any(kind == "P" for _, kind in constraints) and not pk:
        result.warnings.append(
            "数据库报告主键，但当前账号未取得主键字段信息，请 DBA 核对元数据访问权限。"
        )
    return result


def table_result(ref: ObjectRef, rows: list, comments: list, keys: list) -> TableMeta:
    if not rows:
        raise CatalogReadError("选定对象已不可读取或已删除，请检查数据库授权与同步范围")
    grouped: dict[str, ForeignKeyMeta] = {}
    for name, column, schema, table, target, _ in keys:
        fk = grouped.setdefault(
            name,
            ForeignKeyMeta(
                name=name,
                columns=[],
                target_schema=schema,
                target_table=table,
                target_columns=[],
            ),
        )
        fk.columns.append(column)
        fk.target_columns.append(target)
    return TableMeta(
        **ref.model_dump(),
        comment=str(comments[0][0] or "") if comments else "",
        columns=[
            ColumnMeta(
                name=n,
                ordinal=int(o),
                data_type=t,
                nullable=bool(null),
                comment=str(c or ""),
                primary_key=bool(pk),
            )
            for n, o, t, null, c, pk in rows
        ],
        foreign_keys=list(grouped.values()),
    )


def read_snapshot(
    source: DataSourceInput,
    password: str,
    scope: list[ObjectRef],
    heartbeat: Callable[[], None],
) -> list[TableMeta]:
    tables = []
    with readonly_cursor(source, password) as cursor:
        visible = set()
        for schema in sorted({ref.schema_name for ref in scope}):
            visible.update(discover_on(cursor, source, schema))
            heartbeat()
        for ref in scope:
            heartbeat()
            if ref not in visible:
                # A real DROP is a removal, but SQL/connection failures abort the
                # whole sync. A successful catalog query is required first.
                continue
            if source.database_type in ("postgresql", "kingbase"):
                table = postgres_table(cursor, ref)
            elif source.database_type == "mysql":
                table = mysql_table(cursor, ref)
            else:
                table = oracle_table(cursor, source, ref)
            tables.append(table)
    present = {(t.schema_name, t.name) for t in tables}
    for table in tables:
        table.foreign_keys = [
            fk
            for fk in table.foreign_keys
            if (fk.target_schema, fk.target_table) in present
        ]
    return tables
