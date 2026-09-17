"""`compose` (spec 13): a compose alias said with its literals — the steps come from the
alias, the field values from the sentence, and the noun phrases ride along for the steps.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.item import Item
from pron.kernel.parts.part import Part
from pron.surface.constructions.field_literals import FieldLiterals
from pron.surface.interpret import _first, _unattached
from pron.surface.nouns import find_noun_phrases

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class ComposeConstruction:
    name = "compose"

    def __call__(self, items: list[Item], lex: "Lexicon") -> Part | None:
        w = _first(items, "alias-compose")
        if w is None:
            return None
        nps = find_noun_phrases(items, lex)
        part = Part("compose", verb=w, payload=FieldLiterals(lex)(items, nps))
        part.notes = [f"steps: {len(w.payload.get('steps', []))}"]
        part.leftovers = _unattached(items, nps)
        part.payload["_nps"] = nps
        return part
