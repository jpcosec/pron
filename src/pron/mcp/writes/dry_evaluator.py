"""A move's forms evaluated up to its pre-validation and no further (spec 11 §7, 14 §4): the
`dry_run` of a write tool. Compiled, planned and pre-validated over an overlay exactly as
`session.eval` does it; nothing runs, and what the move resolved to is the answer.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.parts.part import Part
from pron.kernel.parts.response import Response
from pron.sexpr.turn.evaluator import Evaluator


class DryEvaluator(Evaluator):
    """The Evaluator whose last step answers what it would do instead of doing it."""

    def _stale(self) -> Response | None:
        """Nothing is written, so a world that moved meanwhile races nothing."""
        return None

    def _run(self, parts: list[Part], plans: list[dict[str, Any]]) -> Response:
        resolved = self.ctx.record.get("resolved", "")
        return Response(f"Would do: {resolved}. Pre-validation passed.", "unico")
