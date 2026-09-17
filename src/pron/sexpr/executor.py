"""part.kind → what does it (spec 06, 11 §7), and whether it wrote.

One dispatcher over the eight kinds of part a move can have. Everything a kind needs to
know about itself lives in its own executor, so a new kind is a new class and a new line
here, not a longer ladder. What comes back is what to say and whether the world changed —
the move refreshes the graph once, at the end, if anything did.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.part import Part
from pron.sexpr.action_executor import ActionExecutor
from pron.sexpr.assert_executor import AssertExecutor
from pron.sexpr.collaborator import Collaborator
from pron.sexpr.listing import listing
from pron.sexpr.read_executor import ReadExecutor
from pron.sexpr.undo_executor import UndoExecutor
from pron.sexpr.why_executor import WhyExecutor


class Executor(Collaborator):
    """One planned part, carried out."""

    def __call__(
        self,
        part: Part,
        plan: dict[str, Any],
        trace: list[str],
        record: dict[str, Any],
    ) -> tuple[str, bool]:
        fn = getattr(self, "_x_" + part.kind, None)
        return fn(part, plan, trace, record) if fn is not None else ("", False)

    def _x_nominal(self, part, plan, trace, record) -> tuple[str, bool]:
        """A noun on its own is a question: which documents it names (spec 13)."""
        res = plan["subject"]
        self.s.dialogue.remember(res.addresses, res.phrase.model)
        return listing(self.s.display, res.addresses), False

    def _x_read(self, part, plan, trace, record) -> tuple[str, bool]:
        return ReadExecutor(self.s)(part, plan, trace, record), False

    def _x_assert(self, part, plan, trace, record) -> tuple[str, bool]:
        return AssertExecutor(self.s)(part, plan, trace, record), True

    def _x_action(self, part, plan, trace, record) -> tuple[str, bool]:
        return ActionExecutor(self.s)(part, plan, trace, record)

    def _x_compose(self, part, plan, trace, record) -> tuple[str, bool]:
        return self.s._compose(part, plan, trace, record), True

    def _x_refresh(self, part, plan, trace, record) -> tuple[str, bool]:
        self.s._refresh(trace, full=True)
        return "Refreshed.", False

    def _x_undo(self, part, plan, trace, record) -> tuple[str, bool]:
        return UndoExecutor(self.s)(trace, record), True

    def _x_why(self, part, plan, trace, record) -> tuple[str, bool]:
        return WhyExecutor(self.s)(part, trace, record), False
