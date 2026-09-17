"""`nominal` (spec 02): a sentence that is only a noun phrase ("the large tables on the
terrace"); what does not attach to it is left over.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.item import Item
from pron.kernel.parts.part import Part
from pron.surface.interpret import _unattached
from pron.surface.nouns import find_noun_phrases

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class NominalConstruction:
    name = "nominal"

    def __call__(self, items: list[Item], lex: "Lexicon") -> Part | None:
        nps = find_noun_phrases(items, lex)
        if not nps or nps[0].model is None:
            return None
        return Part("nominal", subject=nps[0], leftovers=_unattached(items, nps))
