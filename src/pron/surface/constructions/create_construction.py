"""`create` (spec 11 §7): the kernel verb with a noun phrase naming a model, and the field
literals of the sentence for that model.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.item import Item
from pron.kernel.parts.part import Part
from pron.surface.constructions.field_literals import FieldLiterals
from pron.surface.interpret import _kernel
from pron.surface.nouns import find_noun_phrases

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class CreateConstruction:
    name = "create"

    def __call__(self, items: list[Item], lex: "Lexicon") -> Part | None:
        w = _kernel(items, "create")
        if w is None:
            return None
        nps = find_noun_phrases(items, lex)
        if not nps or nps[0].model is None:
            return None
        subject = nps[0]
        payload = FieldLiterals(lex)(items, nps, model=subject.model)
        return Part(
            "action",
            subject=subject,
            verb=w,
            payload={"verb": "create", "fields": payload},
        )
