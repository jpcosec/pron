"""`change_to` (spec 11 §7): the kernel verb `change` with a subject phrase and a field of
its family with a value ("change it to 9 people").
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.item import Item
from pron.kernel.parts.part import Part
from pron.surface.constructions.field_and_value import FieldAndValue
from pron.surface.interpret import _kernel
from pron.surface.nouns import find_noun_phrases

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class ChangeToConstruction:
    name = "change_to"

    def __call__(self, items: list[Item], lex: "Lexicon") -> Part | None:
        w = _kernel(items, "change")
        if w is None:
            return None
        nps = find_noun_phrases(items, lex)
        if not nps:
            return None
        subject = nps[0]
        fld, value = FieldAndValue(lex)(items, subject)
        if fld is None:
            return None
        return Part(
            "action",
            subject=subject,
            verb=w,
            field_name=fld,
            value=value,
            payload={"verb": "change"},
        )
