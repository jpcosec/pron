"""`assert_relation` (spec 03, 11 §7): a relation word between two noun phrases, in a
sentence that asks nothing ("assign it to table 12").
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.item import Item
from pron.kernel.parts.part import Part
from pron.surface.interpret import _first, _unattached
from pron.surface.nouns import find_noun_phrases

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class AssertRelationConstruction:
    name = "assert_relation"

    def __call__(self, items: list[Item], lex: "Lexicon") -> Part | None:
        if any(i.kind == "wh" for i in items):
            return None
        w = _first(items, "relation", "alias-relation")
        if w is None:
            return None
        nps = find_noun_phrases(items, lex)
        if len(nps) < 2:
            return None
        return Part(
            "assert",
            subject=nps[0],
            object=nps[1],
            verb=w,
            leftovers=_unattached(items, nps),
        )
