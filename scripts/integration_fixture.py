"""Local-only embed host + isolated metadata + replay model + real synthetic SQL."""
import asyncio
import json
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from module1_demo import LOCAL, configure


def main():
    configure()
    import httpx
    import uvicorn
    from fastapi.testclient import TestClient
    from sqlmodel import SQLModel, Session, create_engine, select

    from app.api.deps import get_db
    from app.core.db import engine
    from app.main import app
    from app.models import User
    from app.modules.assistant import gateway
    from app.modules.assistant.models import GatewayState, ModelGateway
    from app.modules.catalog.models import CatalogState
    from app.modules.datasources.models import DataSource
    from app.modules.datasources.service import encrypt_password
    from app.modules.integration.worker import advance, claim as integration_claim
    from app.modules.query.models import QueryPolicy
    from app.modules.query.worker import claim, run_job
    from app.modules.semantic.models import SemanticRelease, Topic, TopicMember
    from module5_demo import replay, seed

    target = LOCAL / f"integration-fixture-{uuid.uuid4().hex}.db"
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
            member = session.exec(select(User).where(User.email == "analyst@lightsql.example.com")).one()
            member_id = str(member.id)
        created = client.post("/api/v1/integrations/", json={"name": "本地嵌入验证", "ceiling_user_id": member_id, "topic_ids": [topic_id], "origins": ["http://127.0.0.1:8007"], "scopes": ["ask", "query", "analysis", "embed"], "requests_per_minute": 300})
        created.raise_for_status()
        application = created.json()
    with Session(isolated) as session:
        model = ModelGateway(name="集成协议回放（非真实模型）", provider="zhipu", base_url=gateway.PRESETS[0]["base_url"], model="integration-replay", encrypted_key=encrypt_password("local-only"))
        session.add(model)
        session.add(GatewayState(active_id=model.id))
        session.commit()
    gateway.complete = replay
    stop = threading.Event()

    def query_worker():
        while not stop.is_set():
            job = claim(isolated)
            if job:
                run_job(isolated, *job)
            stop.wait(0.5)

    def orchestration_worker():
        while not stop.is_set():
            task = integration_claim(isolated)
            if task:
                asyncio.run(advance(isolated, *task))
            stop.wait(0.5)

    class Host(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_GET(self):
            html = '''<!doctype html><html lang="zh"><meta charset="utf-8"><title>业务系统 · 嵌入问数演示</title><style>body{font:16px system-ui;background:#f3f5f7;margin:0;padding:24px}h1{font-size:22px}#chat{height:760px;border:1px solid #dce0e5;border-radius:16px;background:white;max-width:1000px;margin:20px auto}header{max-width:1000px;margin:auto}button{padding:8px 16px}</style><header><h1>业务系统 · 销售工作台</h1><p>本机合成验证：固定模型响应，真实合成库查询；不代表真实模型质量。</p><button id="logout">退出问数会话</button></header><div id="chat"></div><script src="http://127.0.0.1:8006/lightsql-embed.js"></script><script>
            window.widget=LightSQL.mount({container:document.querySelector('#chat'),baseUrl:'http://127.0.0.1:8006',clientId:CLIENT_ID,topicId:TOPIC_ID,title:'经营问数',getTicket: async body=>{const r=await fetch('/ticket',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});if(!r.ok)throw Error('获取票据失败');return r.json()},revokeSession:async id=>{const r=await fetch('/session/'+id,{method:'DELETE'});if(!r.ok)throw Error('撤销失败')},onError:e=>console.error(e.message)});document.querySelector('#logout').onclick=async()=>{await widget.destroy();document.querySelector('#chat').textContent='会话已退出'};
            </script></html>'''.replace("CLIENT_ID", json.dumps(application["id"])).replace("TOPIC_ID", json.dumps(topic_id))
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers(); self.wfile.write(html.encode())

        def proxy(self, method, path, body=None):
            # This synthetic host has no real user accounts. Production hosts
            # must authorize their own logged-in user before issuing tickets.
            with httpx.Client(base_url="http://127.0.0.1:8006", timeout=15, trust_env=False) as client:
                auth = client.post("/api/integration/v1/token", json={"client_id": application["id"], "client_secret": application["client_secret"]})
                auth.raise_for_status()
                response = client.request(method, "/api/integration/v1" + path, json=body, headers={"Authorization": "Bearer " + auth.json()["access_token"]})
                self.send_response(response.status_code); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(response.content)

        def do_POST(self):
            if self.path != "/ticket":
                self.send_error(404); return
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
            self.proxy("POST", "/embed/tickets", data)

        def do_DELETE(self):
            if not self.path.startswith("/session/"):
                self.send_error(404); return
            self.proxy("DELETE", "/embed/sessions/" + str(uuid.UUID(self.path.rsplit("/", 1)[1])))

    host = ThreadingHTTPServer(("127.0.0.1", 8007), Host)
    for target_fn in (query_worker, orchestration_worker, host.serve_forever):
        threading.Thread(target=target_fn, daemon=True).start()
    (LOCAL / "integration-fixture.json").write_text(json.dumps({"url": "http://127.0.0.1:8006", "host_url": "http://127.0.0.1:8007", "client_id": application["id"], "topic_id": topic_id, "metadata": str(target), "model": "replay-only"}), encoding="utf-8")
    try:
        uvicorn.run(app, host="127.0.0.1", port=8006, log_level="warning")
    finally:
        stop.set(); host.shutdown()


if __name__ == "__main__":
    main()
