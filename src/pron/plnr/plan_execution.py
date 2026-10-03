"""Carrying out the plan a part holds (spec 04, 11 §7): the kernel verbs, one refresh at the end.

The search already decided; this only writes, through the same verbs a sentence uses, and
keeps what happened — each write with its previous value, so the move can be undone — in the
record of the turn. A write the kernel refuses raises StoreError, and the move answers it like
any other refusal, with the writes already done reported as they are: pron does not undo by
itself.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plnr import Plan, write

from pron.plnr.commit import Commit

if TYPE_CHECKING:
    from pron.sexpr.turn.move_context import MoveContext
    from pron.sexpr.turn.turn_tools import TurnTools


class PlanExecutor:
    """One planned `(goal …)`: what to say, and whether the world changed."""

    def __init__(self, tools: TurnTools):
        self.t = tools

    def __call__(self, plan: dict[str, Any], ctx: MoveContext) -> tuple[str, bool]:
        found: Plan = plan["plan"]
        writes = Commit(self.t.kernel, plan["world"])(found)
        for w in writes:
            ctx.trace.append(
                f"{w.verb} {w.address}" + (f" {w.after!r}" if w.done else "")
            )
            ctx.record["writes"].append(w.record())
        return self._say(found, len(writes)), bool(writes)

    def _say(self, plan: Plan, written: int) -> str:
        if written:
            return f"Done ({written} writes)."
        return (
            " ".join(f"{k} = {write(v)}" for k, v in plan.answers().items()) or "Yes."
        )
