"""When a part cannot be planned, what the session says back (spec 06).

Three answers, none of which writes anything: a `choice` when a noun named more than one
document, `data` when a create still needs a required field, and `missing` when a noun
named nothing. The first two open a pending question the next turn answers; the third
closes the turn but keeps the hole it left, so a verbless fragment in the next turn can
correct it (spec 06 §Corrección).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.part import Part
from pron.kernel.parts.response import Response
from pron.sexpr.execution.listing import numbered
from pron.sexpr.dialogue.pending import Pending
from pron.sexpr.resolving.resolution import Resolution

if TYPE_CHECKING:
    from pron.kernel.display import Display
    from pron.sexpr.dialogue.dialogue import Dialogue
    from pron.sexpr.turn.move_context import MoveContext


class Asker:
    """Opens the pending question a part needs answered, or reports what it did not find."""

    def __init__(self, display: Display, dialogue: Dialogue):
        self.display, self.dialogue = display, dialogue

    def choice(self, part: Part, role: str, res: Resolution, ctx: MoveContext) -> Response:
        """A noun that named more than one document: the session asks which one."""
        labels = self.display.names(res.candidates)
        self.dialogue.open(self._choice_pending(part, role, res, labels, ctx.sentence))
        ctx.record["candidates"] = list(res.candidates)
        return Response(f"Which one? {numbered(labels)}", "ambiguo")

    @staticmethod
    def _choice_pending(
        part: Part, role: str, res: Resolution, labels: list[str], sentence: str
    ) -> Pending:
        return Pending(
            "choice",
            "",
            part.items and " ".join(i.text for i in part.items) or sentence,
            candidates=list(res.candidates),
            labels=labels,
            slot=role,
            state={"part": part},
        )

    def data(self, part: Part, field_name: str, ctx: MoveContext) -> Response:
        """A create whose required field nobody said: the session asks for it."""
        assert part.subject is not None
        self.dialogue.open(_data_pending(part, field_name, ctx.sentence))
        ctx.record["missing_field"] = field_name
        return Response(f"{field_name.replace('_', ' ').capitalize()}?", "ambiguo")

    def missing(self, res: Resolution, ctx: MoveContext) -> Response:
        """A noun that named nothing: what was looked for, and what to offer instead."""
        ctx.record["missing"] = {"note": res.note, "candidates": res.candidates}
        if res.phrase.unknown_values:
            self._keep_the_hole(res, ctx.sentence)
        if not res.candidates:
            return Response(res.note + ".", "missing")
        return Response(f"{res.note}. Did you mean {self._offers(res)}?", "missing")

    def _keep_the_hole(self, res: Resolution, sentence: str) -> None:
        """Spec 06: the hole a missing turn left, for a correction in the next turn."""
        model, fld, text = res.phrase.unknown_values[0]
        self.dialogue.last_missing = {
            "sentence": sentence,
            "model": model,
            "field": fld,
            "text": text,
        }

    def _offers(self, res: Resolution) -> str:
        """Values are offered as said; documents are offered by their natural name."""
        if res.phrase.unknown_values:
            return " or ".join(f"*{c}*" for c in res.candidates)
        return " or ".join(self.display.names(res.candidates))


def _data_pending(part: Part, field_name: str, sentence: str) -> Pending:
    assert part.subject is not None
    return Pending(
        "data",
        "",
        " ".join(i.text for i in part.items) or sentence,
        field_name=field_name,
        model=part.subject.model,
        state={"part": part},
    )
