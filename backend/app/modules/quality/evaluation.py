"""Deterministic scoring: missing answers count as failures, never as exclusions."""

from collections import Counter
from decimal import Decimal, InvalidOperation
from math import ceil

from fastapi import HTTPException

from app.modules.quality.models import DatasetInput, GoldCase, Observation, RunInput


def percentile(values: list[int], fraction: float) -> int | None:
    return sorted(values)[max(0, ceil(len(values) * fraction) - 1)] if values else None


def equal_rows(case: GoldCase, observation: Observation) -> bool:
    if observation.truncated or observation.columns != case.columns:
        return False
    if len(observation.rows) != len(case.expected_rows):
        return False

    def equal(left, right):
        if len(left) != len(case.columns) or len(right) != len(case.columns):
            return False
        for column, a, b in zip(case.columns, left, right, strict=True):
            if a is None or b is None or isinstance(a, bool) or isinstance(b, bool):
                if type(a) is not type(b) or a != b:
                    return False
            elif column in case.numeric_columns:
                try:
                    x, y = Decimal(a), Decimal(b)
                    if (
                        not x.is_finite()
                        or not y.is_finite()
                        or abs(x - y) > case.tolerance
                    ):
                        return False
                except InvalidOperation, ValueError:
                    return False
            elif a != b:
                return False
        return True

    if case.ordered:
        return all(
            equal(a, b)
            for a, b in zip(case.expected_rows, observation.rows, strict=True)
        )
    # Bipartite matching avoids greedy failures for overlapping numeric tolerances,
    # and retains duplicate row multiplicity.
    edges = [
        [j for j, actual in enumerate(observation.rows) if equal(expected, actual)]
        for expected in case.expected_rows
    ]
    matched = {}
    for root in range(len(edges)):
        queue, parent, seen = [root], {}, {root}
        destination = None
        for left in queue:
            for right in edges[left]:
                if right in parent:
                    continue
                parent[right] = left
                if right not in matched:
                    destination = right
                    break
                other = matched[right]
                if other not in seen:
                    seen.add(other)
                    queue.append(other)
            if destination is not None:
                break
        if destination is None:
            return False
        reverse = {left: right for right, left in matched.items()}
        while destination is not None:
            left = parent[destination]
            previous = reverse.get(left)
            matched[destination] = left
            destination = previous
    return True


def score(dataset: DatasetInput, run: RunInput) -> dict:
    cases = [c for c in dataset.cases if c.split == run.split]
    actual = {o.case_id: o for o in run.observations}
    if len(actual) != len(run.observations) or set(actual) != {c.id for c in cases}:
        raise HTTPException(
            422, "运行必须恰好覆盖所选集合的全部题目，不能遗漏、重复或混入其他题目"
        )
    results = []
    for case in cases:
        observed = actual[case.id]
        correct = observed.action == case.expected_action
        if correct and case.expected_action == "answer":
            correct = equal_rows(case, observed)
        if observed.critical or observed.error_category != "none":
            correct = False
        results.append(
            {
                "case_id": case.id,
                "correct": correct,
                "expected_action": case.expected_action,
                "action": observed.action,
                "tags": case.tags,
                "error_category": "none"
                if correct
                else (
                    observed.error_category
                    if observed.error_category != "none"
                    else "plan"
                ),
                "critical": observed.critical,
            }
        )
    answerable = [r for r in results if r["expected_action"] == "answer"]
    answered = [r for r in results if r["action"] == "answer"]

    def ratio(numerator, denominator):
        return round(numerator / denominator, 4) if denominator else None

    return {
        "total": len(results),
        "correct": sum(r["correct"] for r in results),
        "overall_accuracy": ratio(sum(r["correct"] for r in results), len(results)),
        "answerable": len(answerable),
        "end_to_end_accuracy": ratio(
            sum(r["correct"] for r in answerable), len(answerable)
        ),
        "coverage": ratio(
            sum(r["action"] == "answer" for r in answerable), len(answerable)
        ),
        "answer_precision": ratio(sum(r["correct"] for r in answered), len(answered)),
        "incorrect_answers": sum(not r["correct"] for r in answered),
        "critical_errors": sum(r["critical"] for r in results),
        "errors": dict(
            Counter(r["error_category"] for r in results if not r["correct"])
        ),
        "p50_ms": percentile([o.elapsed_ms for o in run.observations], 0.5),
        "p95_ms": percentile([o.elapsed_ms for o in run.observations], 0.95),
        "prompt_tokens": sum(o.prompt_tokens for o in run.observations)
        if all(o.usage_measured for o in run.observations)
        else None,
        "completion_tokens": sum(o.completion_tokens for o in run.observations)
        if all(o.usage_measured for o in run.observations)
        else None,
        "cost": str(
            sum((o.cost for o in run.observations if o.cost is not None), Decimal(0))
        )
        if all(o.cost is not None for o in run.observations)
        else None,
        "currency": run.currency,
        "cases": results,
    }
