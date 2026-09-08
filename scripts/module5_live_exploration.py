"""Actual configured model + local synthetic data; never changes model settings."""

import json
import time
import uuid

import httpx

from module1_demo import LOCAL


def run():
    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=180) as client:
        login = client.post("/api/v1/login/access-token", data={"username":"admin@lightsql.example.com", "password":"LightSQL-Demo-2026!"})
        login.raise_for_status()
        client.headers["Authorization"] = "Bearer " + login.json()["access_token"]
        status = client.get("/api/v1/assistant/status").json()
        assert status["configured"], "A real model must be configured"
        topics = client.get("/api/v1/topics/").json()
        topic = next(t for t in topics if t["name"] == "M05 合成销售问答")
        response = client.post("/api/v1/assistant/conversations", json={"topic_id":topic["id"]})
        response.raise_for_status()
        conversation = response.json()
        url = "/api/v1/assistant/conversations/" + conversation["id"]
        report = {"model":status["model"], "conversation_id":conversation["id"], "cases":[]}
        for question in ["我想看看订单明细，按日期倒序列出最近五笔，包含订单号、渠道、订单金额和退款金额。", "改成按渠道统计订单数和退款金额，画柱状图，并给我一些分析建议。", "按日期统计退款金额，并计算上一个有订单日期的退款金额，画折线图。"]:
            response = client.post(url + "/turns", json={"request_id":str(uuid.uuid4()), "expected_revision":conversation["revision"], "question":question, "mode":"explore"})
            response.raise_for_status()
            conversation = response.json()
            turn = conversation["turns"][-1]
            print(json.dumps({"question":question,"status":turn["status"],"message":turn["message"],"sql_plan":turn["sql_plan"]}, ensure_ascii=False), flush=True)
            assert turn["status"] == "ready", "Model did not produce a validated plan"
            response = client.post(url + f"/turns/{turn['id']}/execute")
            response.raise_for_status()
            job = response.json()
            deadline = time.monotonic() + 60
            while job["status"] in ("queued", "running", "cancelling") and time.monotonic() < deadline:
                time.sleep(0.5)
                job = client.get("/api/v1/queries/" + job["id"]).json()
            assert job["status"] == "succeeded", job
            result = client.get("/api/v1/queries/" + job["id"] + "/result").json()
            case = {"question":question, "sql":turn["sql_plan"]["sql"], "chart":turn["chart"], "job_id":job["id"], "rows":result["rows"]}
            if turn["analysis_requested"]:
                response = client.post(url + f"/turns/{turn['id']}/analysis")
                response.raise_for_status()
                case["analysis"] = response.json()
            report["cases"].append(case)
            (LOCAL / "module5-live-exploration.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf8")
            print(json.dumps({"executed":True,"row_count":len(result["rows"]),"chart":turn["chart"],"analysis":bool(case.get("analysis"))}), flush=True)
        assert len(report["cases"]) == 3


if __name__ == "__main__":
    run()
