"""Run an exported gold dataset through the normal authorized question API.

Uses the current configured model without switching it. Authentication is read
from LIGHTSQL_EVAL_TOKEN. Each case gets its own conversation, including history.
"""

import argparse
import json
import os
import time
import uuid
from pathlib import Path

import httpx


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--split", choices=["dev", "blind"], default="dev")
    parser.add_argument(
        "--evidence", choices=["protocol_replay", "live_model"], required=True
    )
    args = parser.parse_args()
    exported = json.loads(args.dataset.read_text(encoding="utf-8"))
    definition = exported["definition"]
    if args.output.exists():
        raise RuntimeError("Choose a new output path")
    with httpx.Client(
        base_url=args.url.rstrip("/"),
        headers={"Authorization": "Bearer " + os.environ["LIGHTSQL_EVAL_TOKEN"]},
        timeout=180,
        follow_redirects=False,
    ) as client:

        def api(method, path, **kwargs):
            response = client.request(method, "/api/v1" + path, **kwargs)
            response.raise_for_status()
            return response.json()

        user = api("GET", "/users/me")
        configurations = api("GET", "/assistant/gateways")
        config = next(c for c in configurations if c["active"])
        if (
            "fixture" in config["model"] or "replay" in config["model"]
        ) and args.evidence != "protocol_replay":
            raise RuntimeError("Replay configurations must be labeled protocol_replay")
        topic = api("GET", "/topics/" + definition["topic_id"])
        if topic["current_version"] != definition["semantic_version"]:
            raise RuntimeError("Semantic version differs from gold dataset")
        selected = [c for c in definition["cases"] if c["split"] == args.split]
        if not selected:
            raise RuntimeError("No cases in the selected split")
        if any(
            c["actor_role"] != user["email"]
            and not (c["actor_role"] == "admin" and user["is_superuser"])
            for c in selected
        ):
            raise RuntimeError("Evaluation identity does not match the gold actor_role")
        report = {
            "dataset_id": exported["id"],
            "dataset_digest": exported["digest"],
            "model": config["model"],
            "configuration": f"gateway:{config['id']}@{config['revision']}; runner:v1; snapshot:{definition['source_snapshot']}",
            "context_variant": "C",
            "evidence": args.evidence,
            "split": args.split,
            "observations": [],
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        for case in selected:
            started = time.monotonic()
            observation = {
                "case_id": case["id"],
                "action": "error",
                "elapsed_ms": 0,
                "error_category": "model",
            }
            job_id = None
            try:
                conversation = api(
                    "POST",
                    "/assistant/conversations",
                    json={"topic_id": definition["topic_id"]},
                )
                path = "/assistant/conversations/" + conversation["id"]
                for question in [*case.get("history", []), case["question"]]:
                    conversation = api(
                        "POST",
                        path + "/turns",
                        json={
                            "request_id": str(uuid.uuid4()),
                            "expected_revision": conversation["revision"],
                            "question": question,
                            "mode": case.get("mode", "metrics"),
                        },
                    )
                turn = conversation["turns"][-1]
                if turn["status"] in ("clarification", "unsupported"):
                    observation.update(
                        action="clarify"
                        if turn["status"] == "clarification"
                        else "unsupported",
                        error_category="none",
                    )
                elif turn["status"] == "ready":
                    job = api("POST", path + f"/turns/{turn['id']}/execute")
                    job_id = job["id"]
                    deadline = time.monotonic() + 90
                    while (
                        job["status"] in ("queued", "running", "cancelling")
                        and time.monotonic() < deadline
                    ):
                        time.sleep(0.5)
                        job = api("GET", "/queries/" + job_id)
                    if job["status"] == "succeeded":
                        result = api("GET", "/queries/" + job_id + "/result")
                        observation.update(
                            action="answer",
                            error_category="none",
                            columns=[c["id"] for c in result["columns"]],
                            rows=result["rows"],
                            truncated=result["truncated"],
                        )
                        job_id = None
                    else:
                        observation["error_category"] = (
                            "performance"
                            if job["status"]
                            in (
                                "queued",
                                "running",
                                "cancelling",
                                "timed_out",
                                "cleanup_pending",
                            )
                            else "dialect"
                        )
                current = next(
                    c for c in api("GET", "/assistant/gateways") if c["active"]
                )
                if (
                    current != config
                    or api("GET", "/topics/" + definition["topic_id"])[
                        "current_version"
                    ]
                    != definition["semantic_version"]
                ):
                    raise RuntimeError(
                        "Configuration changed; partial run is not importable"
                    )
            except httpx.HTTPError:
                observation["error_category"] = "model"
            finally:
                if job_id:
                    try:
                        api("POST", "/queries/" + job_id + "/cancel")
                    except httpx.HTTPError:
                        observation["critical"] = True
            observation["elapsed_ms"] = round((time.monotonic() - started) * 1000)
            report["observations"].append(observation)
            args.output.write_text(
                json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(
                json.dumps(
                    {
                        "case_id": case["id"],
                        "action": observation["action"],
                        "elapsed_ms": observation["elapsed_ms"],
                    }
                ),
                flush=True,
            )
    print(
        "Saved all observations. Review the data snapshot, error classifications and costs before importing."
    )


if __name__ == "__main__":
    main()
