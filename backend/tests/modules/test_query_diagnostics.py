"""Child timing evidence must not change results or cleanup acknowledgement."""

import time

import pytest

from app.modules.query import executor
from app.modules.query.compiler import CompiledQuery
from tests.modules.test_datasources import BODY


@pytest.mark.parametrize("fails", [False, True])
def test_child_diagnostics_preserve_outcome_and_close_pipe(monkeypatch, fails):
    class Pipe:
        messages = []
        closed = False

        def send(self, value):
            self.messages.append(value)

        def close(self):
            self.closed = True

    def execute(*_args):
        if fails:
            raise RuntimeError("synthetic-secret-driver-error")
        return {
            "status": "succeeded",
            "cleaned": True,
            "elapsed_ms": 7,
            "result": {"rows": [["10.25"]]},
        }

    monkeypatch.setattr(executor, "execute", execute)
    pipe = Pipe()
    before = time.monotonic()
    executor.child_execute(
        {k: v for k, v in BODY.items() if k != "password"},
        "synthetic-secret",
        CompiledQuery("SELECT 1", {}, [], [], []),
        {"metrics": ["revenue"]},
        None,
        pipe,
    )
    assert pipe.closed and len(pipe.messages) == 1
    outcome = pipe.messages[0]
    assert before <= outcome.pop("_child_entered_at") <= time.monotonic()
    assert "synthetic-secret" not in str(outcome)
    if fails:
        assert outcome["status"] == "cleanup_pending" and not outcome["cleaned"]
    else:
        assert outcome == {
            "status": "succeeded",
            "cleaned": True,
            "elapsed_ms": 7,
            "result": {"rows": [["10.25"]]},
        }
