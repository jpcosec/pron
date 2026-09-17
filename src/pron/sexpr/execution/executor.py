"""part.kind → what does it (spec 06, 11 §7), and whether it wrote.

One dispatcher over the eight kinds of part a move can have. Everything a kind needs to
know about itself lives in its own executor, so a new kind is a new class and a new line
here, not a longer ladder. What comes back is what to say and whether the world changed —
the move refreshes the graph once, at the end, if anything did.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from pron.kernel.parts.part import Part
from pron.sexpr.execution.action_executor import ActionExecutor
from pron.sexpr.execution.assert_executor import AssertExecutor
from pron.sexpr.execution.compose_executor import ComposeExecutor
from pron.sexpr.execution.listing import listing
from pron.sexpr.execution.read_executor import ReadExecutor
from pron.sexpr.execution.relation_write import EdgeWriter
from pron.sexpr.execution.undo_executor import UndoExecutor
from pron.sexpr.execution.why_executor import WhyExecutor

if TYPE_CHECKING:
    from pron.sexpr.turn.move_context import MoveContext
    from pron.sexpr.turn.turn_tools import TurnTools

Refresh = Callable[..., None]


class Executor:
    """One planned part, carried out."""

    def __init__(self, tools: TurnTools, refresh: Refresh):
        """refresh: the session's graph refresh, which the `(refresh)` verb runs in full."""
        self.t, self.refresh = tools, refresh

    def __call__(
        self, part: Part, plan: dict[str, Any], ctx: MoveContext
    ) -> tuple[str, bool]:
        fn = getattr(self, "_x_" + part.kind, None)
        return fn(part, plan, ctx) if fn is not None else ("", False)

    def _edges(self) -> EdgeWriter:
        return EdgeWriter(self.t.projection, self.t.verbs, self.t.write_store)

    def _x_nominal(self, part, plan, ctx) -> tuple[str, bool]:
        """A noun on its own is a question: which documents it names (spec 13)."""
        res = plan["subject"]
        self.t.dialogue.remember(res.addresses, res.phrase.model)
        return listing(self.t.display, res.addresses), False

    def _x_read(self, part, plan, ctx) -> tuple[str, bool]:
        t = self.t
        read = ReadExecutor(t.world, t.lex, t.verbs, t.dialogue, t.display)
        return read(part, plan, ctx), False

    def _x_assert(self, part, plan, ctx) -> tuple[str, bool]:
        t = self.t
        edges = AssertExecutor(t.lex, t.display, t.dialogue, self._edges())
        return edges(part, plan, ctx), True

    def _x_action(self, part, plan, ctx) -> tuple[str, bool]:
        return ActionExecutor(self.t.kernel, self.t.dialogue, self.t.display)(part, plan, ctx)

    def _x_compose(self, part, plan, ctx) -> tuple[str, bool]:
        t = self.t
        steps = ComposeExecutor(t.kernel, t.world, t.display, t.dialogue, self._edges())
        return steps(part, plan, ctx), True

    def _x_refresh(self, part, plan, ctx) -> tuple[str, bool]:
        self.refresh(ctx.trace, full=True)
        return "Refreshed.", False

    def _x_undo(self, part, plan, ctx) -> tuple[str, bool]:
        return UndoExecutor(self.t.kernel, self.t.ledger, self.t.dialogue)(ctx), True

    def _x_why(self, part, plan, ctx) -> tuple[str, bool]:
        why = WhyExecutor(self.t.ledger, self.t.dialogue, self.t.display, self.t.verbs)
        return why(part, ctx), False
