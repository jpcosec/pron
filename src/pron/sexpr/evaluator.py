"""Evaluating the forms of one move (spec 11, 13): compile, plan, check, run.

The forms are compiled to parts; every noun of every part is resolved before anything is
executed; the whole move is pre-validated over an overlay (spec 11 §7); hash_mundo is read
once more just before executing (spec 11 §5), and if the world moved while we were
understanding it, the move is understood again over the world as it is now — once, and
then it gives up rather than race forever. Only then do the parts run, in dependency order,
with a single graph refresh at the end if any of them wrote.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.part import Part
from pron.kernel.response import Response
from pron.kernel.sexp import write
from pron.sexpr.collaborator import Collaborator
from pron.sexpr.compiler import Compiler
from pron.sexpr.executor import Executor
from pron.sexpr.form_error import FormError
from pron.sexpr.move_order import dependency_order, pending_creates
from pron.sexpr.not_a_move import NotAMove
from pron.sexpr.planner import Planner
from pron.sexpr.unknown_word import UnknownWord
from pron.surface.render import resolved as resolved_forms

RELOADED = "the world changed while understanding: lexicon and projection reloaded, understanding again"

Plans = list[dict[str, Any]]


class Evaluator(Collaborator):
    """One move, from the forms that say it to the answer it leaves."""

    def __call__(
        self,
        expr: Any,
        trace: list[str],
        record: dict[str, Any],
        retry: bool = False,
        again: Any = None,
    ) -> Response:
        self.expr, self.trace, self.record = expr, trace, record
        self.retry, self.again = retry, again
        parts = self._compile()
        if isinstance(parts, Response):
            return parts
        plans = self._plan_all(parts)
        if isinstance(plans, Response):
            return plans
        stale = self._check(parts, plans)
        return stale if stale is not None else self._run(parts, plans)

    def _compile(self) -> list[Part] | Response:
        self.record.setdefault("forms", write(self.expr))
        self.trace.append("forms: " + write(self.expr))
        try:
            return Compiler(self.s).compile(self.expr)
        except FormError as e:
            return self._refused(e)

    def _refused(self, e: FormError) -> Response:
        """Forms that name a word the projection lacks, say a noun, or are malformed."""
        if isinstance(e, UnknownWord):
            self.record["missing"] = {"note": str(e), "candidates": []}
            return Response(f"{e}.", "missing")
        if isinstance(e, NotAMove):
            return Response(str(e), "error")
        return Response(f"Could not do that: {e}", "error")

    def _plan_all(self, parts: list[Part]) -> Plans | Response:
        """Every noun of every part resolved before anything is executed; the creates this
        move names resolve without reading the store (spec 06 §Coordinación)."""
        self.pending = pending_creates(parts, self.s.write_store)
        plans: Plans = []
        for part in parts:
            plan = Planner(self.s)(part, self.trace, self.record, self.pending)
            if isinstance(plan, Response):
                return plan
            plans.append(plan)
        return plans

    def _check(self, parts: list[Part], plans: Plans) -> Response | None:
        """What the move resolved to; every write of it validated before the first (spec
        11 §7); and the world read again, in case it moved meanwhile (spec 11 §5)."""
        self.record["resolved"] = write(resolved_forms(parts, plans, self.s))
        self.s._prevalidate(parts, plans, self.trace, self.record)
        return self._stale()

    def _stale(self) -> Response | None:
        current = self.s.world.hash_mundo()
        if current == self.s.hash:
            return None
        if self.retry:
            return Response("The world is changing under us; say it again.", "error")
        self._reload(current)
        if self.again is not None:
            return self.again()
        return self.s._eval(self.expr, self.trace, self.record, retry=True)

    def _reload(self, current: str) -> None:
        """The lexicon and projection as the world is now, before understanding it again."""
        self.trace.append(RELOADED)
        self.s.hash = current
        self.s._load()

    def _run(self, parts: list[Part], plans: Plans) -> Response:
        """In dependency order, one refresh at the end (spec 06 §Coordinación)."""
        texts: list[str] = []
        wrote = False
        order = dependency_order(parts, plans, self.pending, self.s.write_store)
        for j in order:
            text, did_write = Executor(self.s)(parts[j], plans[j], self.trace, self.record)
            texts.append(text)
            wrote = wrote or did_write
        if wrote:
            self.s._refresh(self.trace)
        return self._answer(texts)

    def _answer(self, texts: list[str]) -> Response:
        """What every part said, and whatever the writes left worth warning about."""
        warnings = list(dict.fromkeys(self.s.kernel.warnings))
        self.s.kernel.warnings = []
        text = " ".join(t for t in texts if t)
        if warnings:
            text += " Heads up: " + "; ".join(warnings) + "."
        return Response(text, "unico")
