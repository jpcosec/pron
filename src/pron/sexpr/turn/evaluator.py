"""Evaluating the forms of one move (spec 11, 13): compile, plan, check, run.

The forms are compiled to parts; every noun of every part is resolved before anything is
executed; the whole move is pre-validated over an overlay (spec 11 §7); hash_mundo is read
once more just before executing (spec 11 §5), and if the world moved while we were
understanding it, the projection is loaded again and the move is understood again over the
world as it is now — by whoever said it (`again`), or else by evaluating the same forms once
more — once, and then it gives up rather than race forever. Only then do the parts run, in
dependency order, with a single graph refresh at the end if any of them wrote.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from pron.kernel.parts.part import Part
from pron.kernel.parts.response import Response
from pron.kernel.sexp.read_write import write
from pron.sexpr.forms.compiler import Compiler
from pron.sexpr.execution.executor import Executor
from pron.sexpr.forms.form_error import FormError
from pron.sexpr.turn.move_order import dependency_order, pending_creates
from pron.sexpr.forms.not_a_move import NotAMove
from pron.sexpr.planning.planner import Planner
from pron.sexpr.prevalidation.dry_runner import DryRunner
from pron.sexpr.prevalidation.prevalidator import Prevalidator
from pron.sexpr.forms.unknown_word import UnknownWord
from pron.surface.render import resolved as resolved_forms

if TYPE_CHECKING:
    from pron.sexpr.turn.move_context import MoveContext
    from pron.sexpr.turn.projection_state import ProjectionState

Plans = list[dict[str, Any]]
Again = Callable[[], Response]


class Evaluator:
    """One move, from the forms that say it to the answer it leaves."""

    def __init__(self, state: ProjectionState):
        self.state, self.tools = state, state.tools

    def __call__(
        self, expr: Any, ctx: MoveContext, again: Again | None = None
    ) -> Response:
        self.expr, self.ctx, self.again = expr, ctx, again
        parts = self._compile()
        if isinstance(parts, Response):
            return parts
        plans = self._plan_all(parts)
        if isinstance(plans, Response):
            return plans
        stale = self._check(parts, plans)
        return stale if stale is not None else self._run(parts, plans)

    def _compile(self) -> list[Part] | Response:
        self.ctx.record.setdefault("forms", write(self.expr))
        self.ctx.trace.append("forms: " + write(self.expr))
        try:
            return Compiler(self.tools.lex, self.tools.world).compile(self.expr)
        except FormError as e:
            return _refused(e, self.ctx.record)

    def _plan_all(self, parts: list[Part]) -> Plans | Response:
        """Every noun of every part resolved before anything is executed; the creates this
        move names resolve without reading the store (spec 06 §Coordinación)."""
        self.ctx.pending_creates = pending_creates(parts, self.tools.write_store)
        plans: Plans = []
        for part in parts:
            plan = Planner(self.tools)(part, self.ctx)
            if isinstance(plan, Response):
                return plan
            plans.append(plan)
        return plans

    def _check(self, parts: list[Part], plans: Plans) -> Response | None:
        """What the move resolved to; every write of it validated before the first (spec
        11 §7); and the world read again, in case it moved meanwhile (spec 11 §5)."""
        t = self.tools
        self.ctx.record["resolved"] = write(resolved_forms(parts, plans, t))
        dry = DryRunner(t.kernel, t.verbs, t.lex, t.write_store)
        Prevalidator(t.kernel, dry)(parts, plans, self.ctx)
        return self._stale()

    def _stale(self) -> Response | None:
        current = self.tools.world.hash_mundo()
        if current == self.state.hash:
            return None
        if self.ctx.retry:
            return Response("The world is changing under us; say it again.", "error")
        self.ctx.retry = True
        self.state.reload(current, self.ctx.trace)
        if self.again is not None:
            return self.again()
        return Evaluator(self.state)(self.expr, self.ctx)

    def _run(self, parts: list[Part], plans: Plans) -> Response:
        """In dependency order, one refresh at the end (spec 06 §Coordinación)."""
        texts: list[str] = []
        wrote = False
        run = Executor(self.tools, self.state.refresh)
        pending, store = self.ctx.pending_creates, self.tools.write_store
        for j in dependency_order(parts, plans, pending, store):
            text, did_write = run(parts[j], plans[j], self.ctx)
            texts.append(text)
            wrote = wrote or did_write
        if wrote:
            self.state.refresh(self.ctx.trace)
        return self._answer(texts)

    def _answer(self, texts: list[str]) -> Response:
        """What every part said, and whatever the writes left worth warning about."""
        kernel = self.tools.kernel
        warnings = list(dict.fromkeys(kernel.warnings))
        kernel.warnings = []
        text = " ".join(t for t in texts if t)
        if warnings:
            text += " Heads up: " + "; ".join(warnings) + "."
        return Response(text, "unico")


def _refused(e: FormError, record: dict[str, Any]) -> Response:
    """Forms that name a word the projection lacks, say a noun, or are malformed."""
    if isinstance(e, UnknownWord):
        record["missing"] = {"note": str(e), "candidates": []}
        return Response(f"{e}.", "missing")
    if isinstance(e, NotAMove):
        return Response(str(e), "error")
    return Response(f"Could not do that: {e}", "error")
