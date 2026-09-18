"""A dry run of forms in a session (spec 11 §7, 14 §4): no MoveDoc, no write, and the
session's dialogue as it was — a dry run asks nothing and leaves no referent. The world is
read as a move would read it (`sync`), and a refused pre-validation is an answer.
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from pron.kernel.parts.response import Response
from pron.kernel.sexp.read_write import SexpError, read_one
from pron.mcp.writes.dry_evaluator import DryEvaluator
from pron.sexpr.turn.move_context import MoveContext
from pron.world.store_error import StoreError

if TYPE_CHECKING:
    from pron.session import Session


class DryMove:
    """The forms of one move, pre-validated and not run."""

    def __init__(self, session: Session):
        self.session = session

    def __call__(self, forms: str) -> Response:
        dialogue = self.session.dialogue
        saved = copy.deepcopy(vars(dialogue))
        ctx = MoveContext(sentence=forms)
        try:
            resp = self._evaluate(forms, ctx)
        finally:
            vars(dialogue).update(saved)
        resp.trace, resp.record = ctx.trace, ctx.record
        return resp

    def _evaluate(self, forms: str, ctx: MoveContext) -> Response:
        state = self.session.state
        state.sync(ctx.trace)
        try:
            return DryEvaluator(state)(read_one(forms), ctx)
        except SexpError as e:
            return Response(f"Could not read that: {e}", "error")
        except StoreError as e:
            ctx.record["error"] = str(e)
            return Response(f"Could not do that: {e}", "error")
