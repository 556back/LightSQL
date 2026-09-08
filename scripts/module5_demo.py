"""M05 synthetic acceptance. fixture-api uses an isolated metadata copy and NO LLM."""
import copy
import json
import sys
import threading
import time
import uuid

from module1_demo import LOCAL, configure

TOPIC_NAME = "M05 合成销售问答"


def seed(client):
    response = client.post("/api/v1/login/access-token", data={"username": "admin@lightsql.example.com", "password": "LightSQL-Demo-2026!"})
    response.raise_for_status()
    client.headers["Authorization"] = "Bearer " + response.json()["access_token"]
    topics = client.get("/api/v1/topics/").json()
    existing = next((t for t in topics if t["name"] == TOPIC_NAME), None)
    if existing and existing["availability"] == "ready":
        return existing["id"]
    original = next(t for t in topics if t["name"] == "销售经营分析")
    origin_url = "/api/v1/topics/" + original["id"]
    original = client.get(origin_url).json()
    definition = copy.deepcopy(original["definition"])
    definition["external_allowed"] = True
    for item in definition["metrics"] + definition["dimensions"]:
        item["external_allowed"] = True
    # This is a separate, explicitly synthetic topic; the accepted M03 topic's
    # sensitive customer dimension remains unchanged.
    for dimension in definition["dimensions"]:
        dimension["sensitive"] = False
    # Same alias in two entity dimensions, a valid published ambiguity.
    for entity in definition["entities"]:
        if entity["id"] in ("channel_online", "customer_east"):
            entity["aliases"] = list(dict.fromkeys([*entity["aliases"], "示例渠道"]))
    if existing:
        topic = client.get("/api/v1/topics/" + existing["id"]).json()
        assert topic["current_version"] == 0 and topic["description"] == "仅使用已有合成销售数据；M05 模型与实体解析验收主题。", "Preserving an existing customized topic"
    else:
        response = client.post("/api/v1/topics/", json={"name": TOPIC_NAME, "description": "仅使用已有合成销售数据；M05 模型与实体解析验收主题。", "source_id": original["source_id"], "owner": "本地演示"})
        response.raise_for_status()
        topic = response.json()
    url = "/api/v1/topics/" + topic["id"]
    response = client.put(url + "/draft", json={"expected_revision": topic["revision"], "name": TOPIC_NAME, "description": topic["description"], "enabled": True, "definition": definition})
    response.raise_for_status()
    topic = response.json()
    response = client.put(url + "/members", json={"expected_revision": topic["revision"], "user_ids": original["member_ids"]})
    response.raise_for_status()
    topic = client.get(url).json()
    response = client.post(url + "/releases", json={"expected_revision": topic["revision"], "note": "M05 合成主题，允许逻辑语义外发；实体值继续仅保留本地。"})
    response.raise_for_status()
    policy = client.get("/api/v1/queries/topics/" + original["id"] + "/policy").json()
    response = client.put("/api/v1/queries/topics/" + topic["id"] + "/policy", json={"expected_revision": 0, "grants": policy["grants"]})
    response.raise_for_status()
    return topic["id"]


async def replay(config, messages, schema):
    """Known response fixtures, not a natural-language engine or live model test."""
    if schema.get("properties", {}).get("ok"):
        return '{"ok":true}', {}, 1
    if schema.get("properties", {}).get("findings"):
        envelope = json.loads(messages[1]["content"])
        ids = [f["id"] for f in envelope["facts"]]
        return json.dumps({"findings":[{"fact_ids":ids[:3],"interpretation":"本次返回结果存在数值差异，具体范围见引用事实。","next_step":"建议结合订单量进一步核对差异来源，可能原因仍需验证。"}]}), {}, 1
    envelope = json.loads(messages[1]["content"])
    question = envelope["question"]
    if envelope.get("mode") == "explore":
        sql = "SELECT id AS 订单号, order_date AS 日期, channel AS 渠道, gross_amount AS 订单金额, refund_amount AS 退款金额 FROM orders ORDER BY order_date DESC, id DESC LIMIT 5"
        chart = "table"
        if "渠道统计" in question:
            sql = "SELECT channel AS 渠道, COUNT(*) AS 订单数, SUM(refund_amount) AS 退款金额 FROM orders GROUP BY channel ORDER BY 退款金额 DESC"
            chart = "bar"
        elif "日期统计" in question:
            sql = "WITH daily AS (SELECT order_date AS 日期, SUM(refund_amount) AS 退款金额 FROM orders GROUP BY order_date) SELECT 日期, 退款金额, LAG(退款金额) OVER (ORDER BY 日期) AS 上期退款金额 FROM daily ORDER BY 日期"
            chart = "line"
        return json.dumps({"action":"plan","sql_plan":{"kind":"sql","sql":sql},"chart":chart,"analysis_requested":"分析" in question}), {}, 1
    for secret in ("online", "华东示例客户", "m03_orders"):
        assert secret not in json.dumps(envelope, ensure_ascii=False)
    if "同比" in question or "环比" in question:
        return '{"action":"unsupported","message":"当前计划暂不支持同比或环比，请分别查询两个时间范围。"}', {}, 1
    if "情况" in question and "补充" not in question:
        return '{"action":"clarify","message":"请明确要统计的指标与日期范围。"}', {}, 1
    plan = envelope["previous_plan"] or {"metrics": ["net_sales"], "dimensions": [], "filters": [], "time_range": None, "order_by": [], "limit": 100, "timeout_seconds": 15}
    if "净销售额" in question:
        plan["metrics"] = ["net_sales"]
    if "客户区域" in question:
        plan["dimensions"] = [{"dimension_id": "region", "grain": "value"}]
    if "清除" in question:
        plan["filters"] = []
    for ref in envelope["reference_bindings"]:
        if "[" + ref["ref"] + "]" in question:
            plan["filters"] = [{"dimension_id": ref["dimension_id"], "operator": "eq", "values": [ref["ref"]]}]
    if "本月" in question:
        today = envelope["catalog"]["today"]
        year, month = int(today[:4]), int(today[5:7])
        plan["time_range"] = {"start": f"{year}-{month:02d}-01", "end": f"{year + (month == 12)}-{1 if month == 12 else month + 1:02d}-01"}
    return json.dumps({"action": "plan", "plan": plan}), {"prompt_tokens": 0, "completion_tokens": 0}, 1


def fixture_api():
    from fastapi.testclient import TestClient
    from sqlmodel import Session, SQLModel, create_engine, select
    from app.api.deps import get_db
    from app.core.db import engine
    from app.main import app
    from app.models import User
    from app.modules.assistant import gateway
    from app.modules.assistant.models import GatewayState, ModelGateway
    from app.modules.catalog.models import CatalogState
    from app.modules.datasources.models import DataSource
    from app.modules.datasources.service import encrypt_password
    from app.modules.query.models import QueryPolicy
    from app.modules.query.worker import claim, run_job
    from app.modules.semantic.models import SemanticRelease, Topic, TopicMember
    import uvicorn

    target = LOCAL / f"module5-fixture-{uuid.uuid4().hex}.db"
    isolated = create_engine("sqlite:///" + target.as_posix(), connect_args={"check_same_thread": False, "timeout": 30})
    SQLModel.metadata.create_all(isolated)
    with Session(engine) as source, Session(isolated) as destination:
        for cls in (User, DataSource, CatalogState, Topic, SemanticRelease, TopicMember, QueryPolicy):
            for record in source.exec(select(cls)).all():
                destination.add(cls(**record.model_dump()))
            destination.commit()

    def db():
        with Session(isolated) as session:
            yield session

    app.dependency_overrides[get_db] = db
    with TestClient(app) as client:
        topic_id = seed(client)
    with Session(isolated) as session:
        config = ModelGateway(name="协议回放（非真实模型）", provider="zhipu", base_url=gateway.PRESETS[0]["base_url"], model="m05-fixture-not-a-real-model", encrypted_key=encrypt_password("synthetic-fixture-key"))
        session.add(config)
        session.add(GatewayState(active_id=config.id))
        session.commit()
    gateway.complete = replay
    stop = threading.Event()

    def worker():
        while not stop.is_set():
            job = claim(isolated)
            if job:
                run_job(isolated, *job)
            else:
                stop.wait(0.3)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    (LOCAL / "module5-fixture.json").write_text(json.dumps({"topic_id": topic_id, "metadata": str(target), "url": "http://127.0.0.1:8005", "model": "fixture-only"}), encoding="utf8")
    print("Fixture API: isolated metadata, local response replay, real synthetic source queries only.", flush=True)
    try:
        uvicorn.run(app, host="127.0.0.1", port=8005)
    finally:
        stop.set()
        thread.join(timeout=40)


if __name__ == "__main__":
    configure()
    action = sys.argv[1] if len(sys.argv) > 1 else "seed"
    if action == "seed":
        from fastapi.testclient import TestClient
        from app.main import app
        with TestClient(app) as client:
            topic_id = seed(client)
        print("M05 synthetic topic ready:", topic_id)
        (LOCAL / "module5-topic.json").write_text(json.dumps({"topic_id": topic_id}), encoding="utf8")
    elif action == "fixture-api":
        fixture_api()
    else:
        raise SystemExit("Use seed or fixture-api")
