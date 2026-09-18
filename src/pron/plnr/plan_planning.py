"""Searching the goal of one part (spec 13 §El diálogo, spec 11 §7).

The search happens while planning, not while running: a plan that does not hold is answered
the way an unresolved noun is — `missing` when the world had nothing to say, `error` when the
goal itself was malformed or the budget ran out — and nothing is executed. What holds is kept
in the plan of the part, ready for the executor.

The search reads sldb and kgdb and writes nothing: it works over an overlay.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plnr import Plan, run, write

from pron.kernel.parts.response import Response
from pron.plnr.pron_world import PronWorld
from pron.plnr.theorem_load import load_theorems

if TYPE_CHECKING:
    from pron.kernel.parts.part import Part
    from pron.sexpr.turn.move_context import MoveContext
    from pron.sexpr.turn.turn_tools import TurnTools

BUDGET = 10_000  # MicroPlanner's TIMID: a search that does not finish is an answer


class PlanPlanner:
    """One `(goal …)` part: the plan it holds, or the answer that stops the move."""

    def __init__(self, tools: TurnTools, write_store: str | None):
        self.t, self.write_store = tools, write_store
        self.world = PronWorld(tools.lex, tools.verbs)

    def __call__(self, part: Part, ctx: MoveContext) -> dict[str, Any] | Response:
        goal = part.payload["goal"]
        ctx.trace.append("goal: " + write(goal))
        plan = run(
            goal,
            self.world,
            load_theorems(self.t.world, self.write_store),
            budget=BUDGET,
        )
        self._record(plan, ctx)
        return {"plan": plan, "world": self.world} if plan else self._refuse(plan)

    def _record(self, plan: Plan, ctx: MoveContext) -> None:
        ctx.record["plan"] = {
            "holds": bool(plan),
            "goals": plan.spent,
            "writes": plan.as_forms(),
            "reason": plan.reason,
            "failure": plan.failure,
        }
        ctx.trace.extend("plan: " + line for line in plan.trace)
        ctx.record["queries"].extend(self.world.queries)
        self.world.queries = []

    def _refuse(self, plan: Plan) -> Response:
        """What pron calls missing is a world that has nothing for the goal, or a name it
        does not know; a malformed goal, a search out of budget and a store that refused are
        errors."""
        if plan.failure == "absent":
            return Response(
                f"Nothing in this world answers that: {plan.reason}", "missing"
            )
        if plan.failure in ("malformed", "budget", "world"):
            return Response(f"Could not do that: {plan.reason}", "error")
        return Response("Nothing in this world answers that.", "missing")
