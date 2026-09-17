"""What `Session.eval` does inside its move (spec 13).

Forms are a move of their own: they never answer a pending question, so one that is still
open is dropped and the ledger says so. Forms that do not read as an s-expression are an
error before anything is resolved; forms that do are evaluated exactly as the forms a
sentence says, with the same permissions, pre-validation, writes, refresh and undo.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.parts.response import Response
from pron.kernel.sexp.read_write import SexpError, read_one
from pron.sexpr.turn.collaborator import Collaborator


class FormTurn(Collaborator):
    """One move written as forms, inside its move: the answer, and no move it refers to."""

    def __call__(
        self, forms: str, trace: list[str], record: dict[str, Any]
    ) -> tuple[Response, str]:
        self.s._sentence = forms
        self._drop_pending(trace, record)
        try:
            expr = read_one(forms)
        except SexpError as e:
            return Response(f"Could not read that: {e}", "error"), ""
        return self.s._eval(expr, trace, record), ""

    def _drop_pending(self, trace: list[str], record: dict[str, Any]) -> None:
        if self.s.dialogue.pending is not None:
            trace.append("pending dropped: a new move")
            record["dropped_pending"] = self.s.dialogue.pending.sentence
            self.s.dialogue.close()
