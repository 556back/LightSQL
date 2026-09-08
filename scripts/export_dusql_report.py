"""Export local DuSQL evidence and a reviewable model payload; never calls a model."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from evaluate_dusql import ROOT, audit
from evaluate_dusql_live import prepare_messages

from app.modules.assistant.models import PlanDecision


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    assert report["completed"]
    schemas, contents, _, inventory = audit(ROOT / "docs/DuSQL")
    assert inventory["sha256"] == report["inventory"]["sha256"]
    args.output.mkdir(parents=True, exist_ok=False)
    summary = {
        k: v for k, v in report.items() if k not in ("cases", "mixed_numeric_columns")
    }
    summary["mixed_numeric_column_count"] = len(report["mixed_numeric_columns"])
    summary["postgres_reference_errors"] = dict(
        Counter(
            c["postgres_reference_error"]
            for c in report["cases"]
            if c.get("postgres_reference_error")
        )
    )
    summary["parse_errors"] = dict(
        Counter(c["parse_error"] for c in report["cases"] if c.get("parse_error"))
    )
    (args.output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (args.output / "dev-results.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "题号",
                "数据库",
                "问题",
                "解析或绑定错误",
                "SQLite参考错误",
                "PostgreSQL参考错误",
                "PostgreSQL编译错误",
                "SQLite结果一致",
                "PostgreSQL结果一致",
            ]
        )
        for c in sorted(report["cases"], key=lambda c: c["id"]):
            outcome = c["dialects"].get("postgresql", {})
            writer.writerow(
                [
                    c["id"],
                    c["db_id"],
                    c["question"],
                    c.get("parse_error", ""),
                    c.get("sqlite_reference_error", ""),
                    c.get("postgres_reference_error", ""),
                    outcome.get("compile_error", ""),
                    outcome.get("sqlite_match", ""),
                    c.get("postgres_match", ""),
                ]
            )
    selected = {}
    for c in sorted(report["cases"], key=lambda c: c["id"]):
        if c.get("postgres_match"):
            selected.setdefault(c["db_id"], c)
    preview = {
        "status": "not_sent_awaiting_external_payload_approval",
        "model_calls": 0,
        "selection": "one first PostgreSQL-verifiable dev case per database",
        "json_schema": PlanDecision.model_json_schema(),
        "requests": [],
    }
    for db_id, case in selected.items():
        _, _, _, messages = prepare_messages(
            schemas[db_id], contents[db_id], case["question"]
        )
        preview["requests"].append(
            {"case_id": case["id"], "db_id": db_id, "messages": messages}
        )
    (args.output / "live-request-preview.json").write_text(
        json.dumps(preview, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "cases": len(report["cases"]),
                "preview_requests": len(preview["requests"]),
                "model_calls": 0,
            }
        )
    )


if __name__ == "__main__":
    main()
