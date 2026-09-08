import json
import uuid
from pathlib import Path

import pytest
from sqlmodel import Session, select

from app.core.config import settings
from app.modules.datasources import service
from app.modules.datasources.models import (
    ConnectionTestResult,
    DataSource,
    DataSourceAudit,
    DataSourceInput,
    now,
)

PASSWORD = "private-database-password-42"
BODY = {
    "name": "经营分析",
    "database_type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "analytics",
    "username": "reader",
    "password": PASSWORD,
    "tls_mode": "disable",
}


def create(client):
    response = client.post("/api/v1/datasources/", json=BODY)
    assert response.status_code == 201, response.text
    return response.json()


def update_body(source, **changes):
    return {
        **{k: source[k] for k in DataSourceInput.model_fields},
        "expected_revision": source["revision"],
        **changes,
    }


def test_encrypt_and_never_return_secret(env):
    client, engine, _ = env
    source = create(client)
    assert PASSWORD not in json.dumps(source)
    assert "encrypted_password" not in source
    with Session(engine) as session:
        stored = session.get(DataSource, uuid.UUID(source["id"]))
        assert stored.encrypted_password != PASSWORD
        assert service.decrypt_password(stored.encrypted_password) == PASSWORD
    assert PASSWORD not in client.get("/api/v1/datasources/").text


def test_credentials_not_echoed_on_validation_failure(env):
    client, _, _ = env
    secret = "sensitive" * 200
    response = client.post("/api/v1/datasources/", json={**BODY, "password": secret})
    assert response.status_code == 422
    assert secret not in response.text


def test_admin_required_for_every_operation(env):
    client, _, actor = env
    source = create(client)
    actor.is_superuser = False
    calls = [
        client.get("/api/v1/datasources/"),
        client.post("/api/v1/datasources/", json=BODY),
        client.post("/api/v1/datasources/test", json=BODY),
        client.post(f"/api/v1/datasources/{source['id']}/test"),
        client.put(f"/api/v1/datasources/{source['id']}", json=update_body(source)),
        client.delete(f"/api/v1/datasources/{source['id']}?expected_revision=1"),
    ]
    assert all(response.status_code == 403 for response in calls)


def test_host_allowlist_and_unknown_database_rejected(env):
    client, _, _ = env
    assert (
        client.post(
            "/api/v1/datasources/", json={**BODY, "host": "unknown.internal"}
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/datasources/test", json={**BODY, "host": "169.254.169.254"}
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/datasources/", json={**BODY, "database_type": "unknown"}
        ).status_code
        == 422
    )
    assert (
        client.post("/api/v1/datasources/", json={**BODY, "name": "   "}).status_code
        == 422
    )


def test_duplicate_name_and_missing_key(env, monkeypatch):
    client, _, _ = env
    create(client)
    assert (
        client.post(
            "/api/v1/datasources/", json={**BODY, "name": " 经营分析 "}
        ).status_code
        == 409
    )
    monkeypatch.setattr(settings, "DATASOURCE_ENCRYPTION_KEY", None)
    assert (
        client.post("/api/v1/datasources/", json={**BODY, "name": "新连接"}).status_code
        == 503
    )


def test_update_retains_password_invalidates_connection_and_blocks_stale_edit(
    env, monkeypatch
):
    client, engine, _ = env
    source = create(client)
    monkeypatch.setattr(
        service,
        "probe",
        lambda *_: ConnectionTestResult(
            success=True, message="ok", latency_ms=1, tested_at=now()
        ),
    )
    assert client.post(f"/api/v1/datasources/{source['id']}/test").json()["success"]
    changed = client.put(
        f"/api/v1/datasources/{source['id']}", json=update_body(source, port=5433)
    )
    assert changed.status_code == 200
    assert changed.json()["status"] == "untested"
    assert changed.json()["last_tested_at"] is None
    assert (
        client.put(
            f"/api/v1/datasources/{source['id']}", json=update_body(source)
        ).status_code
        == 409
    )
    with Session(engine) as session:
        stored = session.get(DataSource, uuid.UUID(source["id"]))
        assert service.decrypt_password(stored.encrypted_password) == PASSWORD


def test_disabled_and_delete_audit(env):
    client, engine, _ = env
    source = create(client)
    response = client.put(
        f"/api/v1/datasources/{source['id']}", json=update_body(source, enabled=False)
    )
    assert response.status_code == 200
    assert client.post(f"/api/v1/datasources/{source['id']}/test").status_code == 409
    assert (
        client.delete(
            f"/api/v1/datasources/{source['id']}?expected_revision=1"
        ).status_code
        == 409
    )
    assert (
        client.delete(
            f"/api/v1/datasources/{source['id']}?expected_revision=2"
        ).status_code
        == 200
    )
    assert client.get("/api/v1/datasources/").json()["count"] == 0
    with Session(engine) as session:
        assert [row.action for row in session.exec(select(DataSourceAudit)).all()] == [
            "created",
            "updated",
            "deleted",
        ]


def test_changed_config_during_probe_cannot_publish_old_success(env, monkeypatch):
    client, engine, _ = env
    source = create(client)

    def racing_probe(*_):
        with Session(engine) as session:
            row = session.get(DataSource, uuid.UUID(source["id"]))
            row.revision += 1
            row.port = 9999
            session.add(row)
            session.commit()
        return ConnectionTestResult(
            success=True, message="old config", latency_ms=1, tested_at=now()
        )

    monkeypatch.setattr(service, "probe", racing_probe)
    assert client.post(f"/api/v1/datasources/{source['id']}/test").status_code == 409
    assert client.get("/api/v1/datasources/").json()["data"][0]["status"] == "untested"


@pytest.mark.usefixtures("env")
def test_oracle_error_is_sanitized_and_params_are_structured(monkeypatch):
    import oracledb

    captured = {}

    def failed_connection(**kwargs):
        captured.update(kwargs)
        raise RuntimeError(f"driver leaked {PASSWORD}")

    monkeypatch.setattr(oracledb, "connect", failed_connection)
    result = service.probe(
        DataSourceInput.model_validate(
            {
                k: v
                for k, v in {**BODY, "database_type": "oracle", "port": 1521}.items()
                if k != "password"
            }
        ),
        PASSWORD,
    )
    assert not result.success
    assert PASSWORD not in result.message
    assert captured["params"].service_name == "analytics"
    assert captured["params"].protocol == "tcp"
    assert result.readonly_verified is False


@pytest.mark.parametrize(
    "kind,port,database",
    [
        ("postgresql", 15432, "lightsql_demo"),
        ("mysql", 13306, "sales_demo"),
        ("oracle", 11521, "FREEPDB1"),
        ("dameng", 15236, "LIGHT_DEMO"),
        ("kingbase", 15421, "sales_demo"),
    ],
)
@pytest.mark.usefixtures("env")
def test_real_demo_connectors(kind, port, database):
    cfg_path = Path(__file__).resolve().parents[3] / ".local/demo.json"
    if not cfg_path.exists():
        pytest.skip("Start the isolated demo databases to run real-connector checks")
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    extended = kind in ("oracle", "dameng", "kingbase")
    if extended and not (cfg_path.parent / f"{kind}-verification.json").exists():
        pytest.skip(f"Seed and verify the optional {kind} demo to enable this check")
    password = cfg["domestic_reader_password" if extended else "reader_password"]
    config = DataSourceInput(
        name="demo",
        database_type=kind,
        host="127.0.0.1",
        port=port,
        database=database,
        username="LIGHT_READER" if kind in ("oracle", "dameng") else "light_reader",
        tls_mode="disable",
    )
    assert service.probe(config, password).success
    assert not service.probe(config, "deliberately-invalid-password").success
    # Local fixtures have no trusted server certificate. Required verified TLS
    # must fail, rather than silently downgrading or accepting an untrusted CA.
    verified_tls = config.model_copy(update={"tls_mode": "verify-full"})
    assert not service.probe(verified_tls, password).success
    if kind == "dameng":
        assert not service.probe(
            config.model_copy(update={"database": "MISSING_SCHEMA"}), password
        ).success


@pytest.mark.usefixtures("env")
def test_dameng_schema_timeouts_and_no_tls_downgrade(monkeypatch):
    import dmPython

    captured = {}

    def failed_connection(**kwargs):
        captured.update(kwargs)
        raise RuntimeError(f"driver leaked {PASSWORD}")

    monkeypatch.setattr(dmPython, "connect", failed_connection)
    config = DataSourceInput.model_validate(
        {
            k: v
            for k, v in {
                **BODY,
                "database_type": "dameng",
                "database": "LIGHT_DEMO",
                "port": 5236,
            }.items()
            if k != "password"
        }
    )
    result = service.probe(
        config.model_copy(update={"tls_mode": "verify-full"}), PASSWORD
    )
    assert not result.success and "证书校验" in result.message
    assert not captured, (
        "TLS verification must never fall back to an unencrypted connection"
    )
    result = service.probe(config, PASSWORD)
    assert not result.success and PASSWORD not in result.message
    assert captured["schema"] == "LIGHT_DEMO"
    assert captured["login_timeout"] == 5000
    assert captured["connection_timeout"] == 5
    assert captured["access_mode"] == dmPython.DSQL_MODE_READ_ONLY
    assert captured["autoCommit"] is False


def test_public_signup_disabled(env):
    client, _, _ = env
    assert (
        client.post(
            "/api/v1/users/signup",
            json={"email": "new@example.com", "password": "NoSignup123!"},
        ).status_code
        == 403
    )
