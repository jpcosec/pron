"""What `Session.eval` does inside its move (spec 13).

Forms are a move of their own: they never answer a pending question, so one that is still
open is dropped and the ledger says so. Forms that do not read as an s-expression are an
error before anything is resolved; forms that do are evaluated exactly as the forms a
sentence says, with the same permissions, pre-validation, writes, refresh and undo.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.response import Response
from pron.kernel.sexp.read_write import SexpError, read_one
from pron.sexpr.turn.evaluator import Evaluator

if TYPE_CHECKING:
    from pron.sexpr.turn.move_context import MoveContext
    from pron.sexpr.turn.projection_state import ProjectionState


class FormTurn:
    """One move written as forms, inside its move: the answer, and no move it refers to."""

    def __init__(self, state: ProjectionState):
        self.state = state

    def __call__(self, forms: str, ctx: MoveContext) -> tuple[Response, str]:
        ctx.sentence = forms
        self._drop_pending(ctx)
        try:
            expr = read_one(forms)
        except SexpError as e:
            return Response(f"Could not read that: {e}", "error"), ""
        return Evaluator(self.state)(expr, ctx), ""

    def _drop_pending(self, ctx: MoveContext) -> None:
        dialogue = self.state.dialogue
        if dialogue.pending is not None:
            ctx.trace.append("pending dropped: a new move")
            ctx.record["dropped_pending"] = dialogue.pending.sentence
            dialogue.close()
