"""Spec 06 §Corrección: a fragment that fills the hole the last missing turn left.

"book a table on the patio" → there is no patio; "on the terrace" → that is a verbless
fragment, and it fits the hole of the last turn (a value of `zone`), so the previous
sentence is said again whole, with the hole filled. It is not a pending question: that turn
ended and was recorded; this is a new move that says which one it corrects.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.interpretation import Interpretation
from pron.kernel.item import Item
from pron.sexpr.collaborator import Collaborator


class Corrector(Collaborator):
    """The corrected sentence, or None when this sentence is not a correction."""

    def __call__(self, sentence: str) -> str | None:
        hole = self.s.dialogue.last_missing
        if not hole or not hole.get("field"):
            return None
        interp = self.s.interpreter.interpret(sentence)
        if any(p.kind not in ("none", "nominal") for p in interp.parts):
            return None
        values = self._values(interp, hole)
        if len(values) != 1:
            return None
        return hole["sentence"].replace(hole["text"], values.pop())

    def _values(self, interp: Interpretation, hole: dict[str, Any]) -> set[str]:
        known = {w.form for w in self.s.lex.values_of(hole["model"], hole["field"])}
        values: set[str] = set()
        for it in interp.items:
            values |= _fits(it, hole, known)
        return values


def _fits(it: Item, hole: dict[str, Any], known: set[str]) -> set[str]:
    """The values of the hole's field this item says, directly or through a predicate alias."""
    found: set[str] = set()
    for w in it.words:
        if w.kind == "value" and (w.model, w.field_name) == (hole["model"], hole["field"]):
            found.add(w.form)
        elif w.kind == "alias-predicate" and w.model == hole["model"]:
            # "on the Z" with Z a value of the field
            found |= {str(v) for v in it.slots.values() if str(v) in known}
    return found
