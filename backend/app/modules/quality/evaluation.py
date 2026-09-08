"""Deterministic scoring: missing answers count as failures, never as exclusions."""

from collections import Counter
from decimal import (
    MAX_EMAX,
    MIN_EMIN,
    ROUND_CEILING,
    Decimal,
    DecimalException,
    localcontext,
)
from math import ceil

from fastapi import HTTPException

from app.modules.quality.models import DatasetInput, GoldCase, Observation, RunInput


def percentile(values: list[int], fraction: float) -> int | None:
    return sorted(values)[max(0, ceil(len(values) * fraction) - 1)] if values else None


def numeric_equal(left: Decimal, right: Decimal, tolerance: Decimal) -> bool:
    if left == right:
        return True
    if not tolerance:
        return False
    # Round the nonnegative distance upwards. Since tolerance is exactly
    # representable at this precision, rounding cannot change <= tolerance.
    # Precision depends on input digits, never on the gap between exponents.
    with localcontext() as ctx:
        ctx.prec = max(len(v.as_tuple().digits) for v in (left, right, tolerance)) + 2
        ctx.Emax, ctx.Emin, ctx.rounding = MAX_EMAX, MIN_EMIN, ROUND_CEILING
        try:
            return max(left, right) - min(left, right) <= tolerance
        except DecimalException:
            return False


def row_difference(case: GoldCase, observation: Observation) -> dict | None:
    """Return structural diagnostics only; never copy cell values to summaries."""
    if observation.truncated:
        return {"code": "truncated"}
    if observation.columns != case.columns:
        return {"code": "columns"}
    if len(observation.rows) != len(case.expected_rows):
        return {
            "code": "row_count",
            "expected_count": len(case.expected_rows),
            "actual_count": len(observation.rows),
        }

    numeric = {i for i, name in enumerate(case.columns) if name in case.numeric_columns}

    def normalize(rows):
        normalized = []
        for row_index, row in enumerate(rows):
            if len(row) != len(case.columns):
                return None, {"code": "row_width", "row": row_index + 1}
            cells = []
            for index, value in enumerate(row):
                if (
                    index in numeric
                    and value is not None
                    and not isinstance(value, bool)
                ):
                    try:
                        value = Decimal(value)
                        if not value.is_finite():
                            raise ValueError("non-finite")
                    except DecimalException, ValueError:
                        return None, {
                            "code": "numeric_value",
                            "row": row_index + 1,
                            "column": index + 1,
                        }
                cells.append((type(value), value))
            normalized.append(tuple(cells))
        return normalized, None

    expected, error = normalize(case.expected_rows)
    if error:
        return {**error, "side": "expected"}
    actual, error = normalize(observation.rows)
    if error:
        return {**error, "side": "actual"}
    assert expected is not None and actual is not None

    def equal(left, right):
        return all(
            a[0] is b[0]
            and (
                numeric_equal(a[1], b[1], case.tolerance)
                if a[0] is Decimal
                else a[1] == b[1]
            )
            for a, b in zip(left, right, strict=True)
        )

    if case.ordered:
        for index, (left, right) in enumerate(zip(expected, actual, strict=True)):
            if not equal(left, right):
                return {"code": "ordered_rows", "row": index + 1}
        return None
    # The usual exact comparison is linear and preserves duplicate counts.
    if Counter(expected) == Counter(actual):
        return None
    if not case.tolerance or not numeric:
        return {"code": "unordered_rows"}
    # Bipartite matching avoids greedy failures for overlapping numeric tolerances,
    # and retains duplicate row multiplicity.
    edges = [
        [j for j, row in enumerate(actual) if equal(wanted, row)] for wanted in expected
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
            return {"code": "unordered_rows"}
        reverse = {left: right for right, left in matched.items()}
        while destination is not None:
            left = parent[destination]
            previous = reverse.get(left)
            matched[destination] = left
            destination = previous
    return None


def equal_rows(case: GoldCase, observation: Observation) -> bool:
    return row_difference(case, observation) is None


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
        difference = None
        if observed.critical:
            difference = {"code": "critical"}
        elif observed.error_category != "none":
            difference = {"code": "reported_error"}
        elif observed.action != case.expected_action:
            difference = {"code": "action"}
        elif case.expected_action == "answer":
            difference = row_difference(case, observed)
        correct = difference is None
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
                "difference": difference,
            }
        )
    answerable = [r for r in results if r["expected_action"] == "answer"]
    answered = [r for r in results if r["action"] == "answer"]

    def ratio(numerator, denominator):
        return round(numerator / denominator, 4) if denominator else None

    return {
        "scoring_version": 2,
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
