"""When a part cannot be planned, what the session says back (spec 06).

Three answers, none of which writes anything: a `choice` when a noun named more than one
document, `data` when a create still needs a required field, and `missing` when a noun
named nothing. The first two open a pending question the next turn answers; the third
closes the turn but keeps the hole it left, so a verbless fragment in the next turn can
correct it (spec 06 §Corrección).
"""

from __future__ import annotations

from typing import Any

from pron.kernel.part import Part
from pron.kernel.response import Response
from pron.sexpr.collaborator import Collaborator
from pron.sexpr.listing import numbered
from pron.sexpr.pending import Pending
from pron.sexpr.resolution import Resolution


class Asker(Collaborator):
    """Opens the pending question a part needs answered, or reports what it did not find."""

    def choice(
        self, part: Part, role: str, res: Resolution, record: dict[str, Any]
    ) -> Response:
        """A noun that named more than one document: the session asks which one."""
        labels = self.s.display.names(res.candidates)
        self.s.dialogue.open(self._choice_pending(part, role, res, labels))
        record["candidates"] = list(res.candidates)
        return Response(f"Which one? {numbered(labels)}", "ambiguo")

    def _choice_pending(
        self, part: Part, role: str, res: Resolution, labels: list[str]
    ) -> Pending:
        return Pending(
            "choice",
            "",
            part.items and " ".join(i.text for i in part.items) or self.s._sentence,
            candidates=list(res.candidates),
            labels=labels,
            slot=role,
            state={"part": part},
        )

    def data(self, part: Part, field_name: str, record: dict[str, Any]) -> Response:
        """A create whose required field nobody said: the session asks for it."""
        assert part.subject is not None
        self.s.dialogue.open(self._data_pending(part, field_name))
        record["missing_field"] = field_name
        return Response(f"{field_name.replace('_', ' ').capitalize()}?", "ambiguo")

    def _data_pending(self, part: Part, field_name: str) -> Pending:
        assert part.subject is not None
        return Pending(
            "data",
            "",
            " ".join(i.text for i in part.items) or self.s._sentence,
            field_name=field_name,
            model=part.subject.model,
            state={"part": part},
        )

    def missing(self, res: Resolution, record: dict[str, Any]) -> Response:
        """A noun that named nothing: what was looked for, and what to offer instead."""
        record["missing"] = {"note": res.note, "candidates": res.candidates}
        if res.phrase.unknown_values:
            self._keep_the_hole(res)
        if not res.candidates:
            return Response(res.note + ".", "missing")
        return Response(f"{res.note}. Did you mean {self._offers(res)}?", "missing")

    def _keep_the_hole(self, res: Resolution) -> None:
        """Spec 06: the hole a missing turn left, for a correction in the next turn."""
        model, fld, text = res.phrase.unknown_values[0]
        self.s.dialogue.last_missing = {
            "sentence": self.s._sentence,
            "model": model,
            "field": fld,
            "text": text,
        }

    def _offers(self, res: Resolution) -> str:
        """Values are offered as said; documents are offered by their natural name."""
        if res.phrase.unknown_values:
            return " or ".join(f"*{c}*" for c in res.candidates)
        return " or ".join(self.s.display.names(res.candidates))
