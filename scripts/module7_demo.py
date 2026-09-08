"""Copy clearly labeled, verified replay evidence into the local demo dashboard."""

import json

import httpx

from module1_demo import LOCAL


def login(client):
    result = client.post(
        "/api/v1/login/access-token",
        data={
            "username": "admin@lightsql.example.com",
            "password": "LightSQL-Demo-2026!",
        },
    )
    result.raise_for_status()
    client.headers["Authorization"] = "Bearer " + result.json()["access_token"]


def main():
    fixture = json.loads((LOCAL / "module5-fixture.json").read_text(encoding="utf-8"))
    evidence = json.loads((LOCAL / "module7-browser.json").read_text(encoding="utf-8"))
    with (
        httpx.Client(base_url=fixture["url"], timeout=30) as source,
        httpx.Client(base_url="http://127.0.0.1:8000", timeout=30) as target,
    ):
        login(source)
        login(target)
        data = source.get("/api/v1/quality/datasets/" + evidence["datasetId"]).json()
        topic = target.get("/api/v1/topics/" + data["definition"]["topic_id"]).json()
        assert topic["current_version"] == data["definition"]["semantic_version"]
        assert data["definition"]["provenance"] == "synthetic"
        existing = target.get("/api/v1/quality/datasets").json()
        created = next((d for d in existing if d["digest"] == data["digest"]), None)
        if created is None:
            response = target.post("/api/v1/quality/datasets", json=data["definition"])
            response.raise_for_status()
            created = response.json()
        runs = source.get(
            "/api/v1/quality/runs", params={"dataset_id": data["id"]}
        ).json()
        previous = target.get(
            "/api/v1/quality/runs", params={"dataset_id": created["id"]}
        ).json()
        for run in runs:
            assert run["evidence"] == "protocol_replay"
            if any(
                r["model"] == run["model"]
                and r["split"] == run["split"]
                and r["evidence"] == run["evidence"]
                for r in previous
            ):
                continue
            payload = source.get("/api/v1/quality/runs/" + run["id"]).json()[
                "definition"
            ]
            payload["dataset_id"] = created["id"]
            payload["configuration"] += "; imported from isolated synthetic fixture"
            response = target.post("/api/v1/quality/runs", json=payload)
            response.raise_for_status()
        operations = target.get("/api/v1/quality/operations")
        operations.raise_for_status()
        report = {
            "dataset_id": created["id"],
            "replay_only": True,
            "workers": operations.json()["workers"],
            "backup": operations.json()["backup"],
        }
        (LOCAL / "module7-main.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
