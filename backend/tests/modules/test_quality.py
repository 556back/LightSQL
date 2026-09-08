# ruff: noqa: F811
import copy
import uuid
from datetime import timedelta
from decimal import Decimal

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlmodel import Session, select

from app.modules.assistant.models import AssistantTurn, Conversation
from app.modules.assistant.service import purge
from app.modules.datasources.models import now
from app.modules.quality import operations
from app.modules.quality.evaluation import equal_rows, score
from app.modules.quality.models import (
    DatasetInput,
    GoldCase,
    Observation,
    QualityAudit,
    QualityFeedback,
    RunInput,
)
from tests.modules.test_assistant import ask, assistant_env, topic_env  # noqa: F401

BASE = "/api/v1/quality"


def dataset(topic_id=None):
    return {
        "name": "合成回归",
        "topic_id": str(topic_id or uuid.uuid4()),
        "semantic_version": 1,
        "source_snapshot": "synthetic-v1",
        "as_of": "2026-09-07",
        "timezone": "Asia/Shanghai",
        "provenance": "synthetic",
        "owner": "测试",
        "cases": [
            {
                "id": "net",
                "group": "net",
                "split": "dev",
                "question": "净销售额",
                "actor_role": "admin",
                "expected_action": "answer",
                "columns": ["revenue"],
                "numeric_columns": ["revenue"],
                "expected_rows": [["4000.00"]],
                "reference_sql": "SELECT SUM(amount) FROM synthetic",
            },
            {
                "id": "clarify",
                "group": "ambiguous",
                "split": "dev",
                "question": "业绩怎么样",
                "actor_role": "admin",
                "expected_action": "clarify",
            },
        ],
    }


def run_body(dataset_id=None, digest="a" * 64):
    return {
        "dataset_id": str(dataset_id or uuid.uuid4()),
        "dataset_digest": digest,
        "model": "replay",
        "configuration": "fixture-v1",
        "context_variant": "C",
        "evidence": "protocol_replay",
        "split": "dev",
        "observations": [
            {
                "case_id": "net",
                "action": "answer",
                "columns": ["revenue"],
                "rows": [["4000"]],
                "elapsed_ms": 12,
            },
            {"case_id": "clarify", "action": "clarify", "elapsed_ms": 4},
        ],
    }


def test_feedback_survives_conversation_expiry_and_requires_admin(assistant_env):
    client, engine, actor, _, url, _ = assistant_env
    turn = ask(client, url).json()["turns"][-1]
    assert (
        client.put(
            url + f"/turns/{turn['id']}/feedback",
            json={"rating": "incorrect", "category": "metric", "comment": "秘密反馈"},
        ).status_code
        == 200
    )
    with Session(engine) as session:
        record = session.exec(select(QualityFeedback)).one()
        assert "秘密反馈" not in record.encrypted_payload
        conversation = session.get(Conversation, uuid.UUID(url.split("/")[-1]))
        conversation.expires_at = now() - timedelta(seconds=1)
        session.add(conversation)
        session.commit()
        purge(session)
        session.commit()
        assert not session.get(AssistantTurn, uuid.UUID(turn["id"])).encrypted_payload
    data = client.get(BASE + "/feedback").json()
    assert data[0]["snapshot"]["feedback"]["comment"] == "秘密反馈"
    assert data[0]["snapshot"]["question"] == "按区域统计销售额"
    actor.is_superuser = False
    for endpoint in ("/feedback", "/datasets", "/runs", "/operations"):
        assert client.get(BASE + endpoint).status_code == 403


def test_review_link_revision_audit_and_resubmit(assistant_env):
    client, engine, _, topic_url, url, _ = assistant_env
    turn = ask(client, url).json()["turns"][-1]
    endpoint = url + f"/turns/{turn['id']}/feedback"
    client.put(endpoint, json={"rating": "helpful"})
    record = client.get(BASE + "/feedback").json()[0]
    review_url = BASE + "/feedback/" + record["id"]
    body = {"expected_revision": 1, "status": "resolved", "note": "核对完成"}
    assert client.put(review_url, json=body).status_code == 422
    created = client.post(BASE + "/datasets", json=dataset(topic_url.split("/")[-1]))
    assert created.status_code == 201, created.text
    body.update(dataset_id=created.json()["id"], case_id="net")
    response = client.put(review_url, json=body)
    assert response.status_code == 200, response.text
    assert response.json()["revision"] == 2
    assert client.put(review_url, json=body).status_code == 409
    client.put(endpoint, json={"rating": "incorrect", "category": "filter"})
    assert client.get(BASE + "/feedback").json()[0]["status"] == "pending"
    with Session(engine) as session:
        assert len(session.exec(select(QualityAudit)).all()) == 3
        record = session.exec(select(QualityFeedback)).one()
        record.expires_at = now() - timedelta(seconds=1)
        session.add(record)
        session.commit()
    assert client.get(BASE + "/feedback").json() == []


def test_scoring_decimal_refusal_and_missing_not_excluded():
    data = DatasetInput.model_validate(dataset())
    run = RunInput.model_validate(run_body())
    summary = score(data, run)
    assert summary["end_to_end_accuracy"] == 1 and summary["cost"] is None
    run.observations[0].action = "unsupported"
    summary = score(data, run)
    assert summary["end_to_end_accuracy"] == 0 and summary["coverage"] == 0
    assert summary["answer_precision"] is None
    run.observations.pop()
    with pytest.raises(HTTPException):
        score(data, run)


@pytest.mark.parametrize(
    "values, expected",
    [
        ([["4000.000"]], True),
        ([["4000.01"]], False),
        ([[None]], False),
        ([[True]], False),
        ([["NaN"]], False),
        ([["Infinity"]], False),
        ([["4000"], ["4000"]], False),
    ],
)
def test_result_comparison(values, expected):
    case = GoldCase.model_validate(dataset()["cases"][0])
    observed = Observation(
        case_id=case.id,
        action="answer",
        columns=case.columns,
        rows=values,
        elapsed_ms=1,
    )
    assert equal_rows(case, observed) is expected


def test_unordered_tolerance_matching_duplicates_and_order():
    case = GoldCase.model_validate(dataset()["cases"][0])
    case.expected_rows, case.tolerance = [["1"], ["2"]], Decimal("1")
    observed = Observation(
        case_id=case.id,
        action="answer",
        columns=case.columns,
        rows=[["1"], ["0"]],
        elapsed_ms=1,
    )
    assert equal_rows(case, observed)
    case.ordered = True
    assert not equal_rows(case, observed)
    case.ordered, case.tolerance = False, Decimal(0)
    case.expected_rows = [["1"], ["1"]]
    assert not equal_rows(case, observed)


def test_dataset_split_leakage_and_duplicate_ids():
    data = dataset()
    data["cases"].append(
        {**copy.deepcopy(data["cases"][0]), "id": "net-copy", "split": "blind"}
    )
    with pytest.raises(ValidationError):
        DatasetInput.model_validate(data)
    data["cases"][-1].update(split="dev", id="net")
    with pytest.raises(ValidationError):
        DatasetInput.model_validate(data)


def test_run_api_digest_score_and_no_payload_in_listing(assistant_env):
    client, _, _, topic_url, _, _ = assistant_env
    created = client.post(
        BASE + "/datasets", json=dataset(topic_url.split("/")[-1])
    ).json()
    body = run_body(created["id"], created["digest"])
    response = client.post(BASE + "/runs", json=body)
    assert response.status_code == 201, response.text
    assert response.json()["summary"]["correct"] == 2
    body["dataset_digest"] = "b" * 64
    assert client.post(BASE + "/runs", json=body).status_code == 409
    listing = client.get(BASE + "/runs").json()
    assert "encrypted_payload" not in listing[0]
    assert client.get(BASE + "/datasets/" + created["id"]).json()["definition"]["cases"]


def test_critical_error_never_counts_as_correct():
    run = RunInput.model_validate(run_body())
    run.observations[0].critical = True
    summary = score(DatasetInput.model_validate(dataset()), run)
    assert summary["critical_errors"] == 1 and summary["end_to_end_accuracy"] == 0


def test_operations_heartbeat_and_no_secrets(env):
    client, engine, _ = env
    operations.beat(engine, "query-test", "query")
    response = client.get(BASE + "/operations")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["workers"]["query"]["healthy"]
    assert not data["workers"]["catalog"]["healthy"]
    assert data["backup"] is None and data["alerts"]
    assert data["query_capacity"] == {
        "global_limit": 5,
        "source_limit": 2,
        "actor_limit": 1,
        "queue_timeout_seconds": 30,
        "occupied": 0,
    }
    assert "sql_text" not in response.text and "encrypted" not in response.text


def test_quality_validation_does_not_echo_payload(env):
    client, _, _ = env
    body = dataset()
    body["cases"][0]["question"] = "private" * 500
    response = client.post(BASE + "/datasets", json=body)
    assert response.status_code == 422 and "private" not in response.text
