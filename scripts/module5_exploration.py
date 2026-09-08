"""Read-only exploration checks against the three local synthetic databases."""

import json
import threading
import uuid
from decimal import Decimal

from module1_demo import LOCAL, configure


def verify():
    from sqlmodel import Session, select
    from app.core.db import engine
    from app.modules.catalog.models import CatalogState, TableMeta
    from app.modules.datasources.models import DataSource, DataSourceInput
    from app.modules.datasources.service import decrypt_password
    from app.modules.query.exploration import compile_sql
    from app.modules.query.executor import execute
    from app.modules.query.models import QueryGrant, SqlPlan
    from module4_demo import cross_definition

    report = []
    with Session(engine) as session:
        for source in session.exec(select(DataSource)).all():
            if source.database_type not in ("postgresql", "mysql", "oracle"):
                continue
            if source.host != "127.0.0.1" or source.port not in (15432, 13306, 11521):
                continue
            state = session.get(CatalogState, source.id)
            tables = [TableMeta.model_validate(t) for t in state.snapshot]
            definition = cross_definition(tables)
            columns = {m.id: next(t.columns for t in tables if (t.schema_name, t.name) == (m.relation.schema_name, m.relation.name)) for m in definition.models}
            def c(model, name):
                return '"' + next(c.name for c in columns[model] if c.name.lower() == name) + '"'
            amount, tenant = c("orders", "amount"), c("orders", "tenant_id")
            config, password = DataSourceInput.model_validate(source), decrypt_password(source.encrypted_password)
            queries = [
                (f"SELECT SUM({amount}) AS total FROM orders", None, "3500.60"),
                (f"WITH scoped AS (SELECT * FROM orders) SELECT SUM({amount}) AS total FROM scoped", QueryGrant(user_id=uuid.uuid4(), exploration=[{"model_id":"orders", "columns":[col.name for col in columns["orders"]]}], rows=[{"model_id":"orders", "column":tenant.strip('"'), "values":["1"]}]), "2000.30"),
            ]
            for sql, grant, expected in queries:
                plan = SqlPlan(sql=sql)
                compiled = compile_sql(definition, tables, source.database_type, plan, grant)
                outcome = execute(config, password, compiled, plan, threading.Event())
                assert outcome["status"] == "succeeded", (source.database_type, outcome, compiled.sql)
                assert Decimal(outcome["result"]["rows"][0][0]) == Decimal(expected), outcome
                assert outcome["result"]["columns"][0]["value_type"] == "number"
            report.append({"database":source.database_type,"actual_sql_execution":True,"cte_row_scope":True,"exact_decimal":True})
    assert len(report) == 3, "Expected the three local synthetic sources"
    (LOCAL / "module5-exploration-verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    configure()
    verify()
