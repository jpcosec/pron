"""`set_field` (spec 11 §7): "add a note saying: birthday" / "set the notes to X" — a field
alias plus a literal, the subject by referent or phrase, else the implicit "it".
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.item import Item
from pron.kernel.parts.part import Part
from pron.surface.interpret import _field_word, _implicit_it, _kernel
from pron.surface.nouns import find_noun_phrases

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class SetFieldConstruction:
    name = "set_field"

    def __call__(self, items: list[Item], lex: "Lexicon") -> Part | None:
        found = _field_word(items)
        lit = next((i for i in items if i.kind == "literal"), None)
        if found is None or lit is None:
            return None
        nps = find_noun_phrases(items, lex)
        w = found[1]
        subject = (
            next((n for n in nps if n.referent is not None or n.model), None)
            or _implicit_it()
        )
        verb = _kernel(items, "change") or _kernel(items, "add") or w
        return Part(
            "action",
            subject=subject,
            verb=verb,
            field_name=w.field_name,
            value=lit.meta.get("value", lit.text),
            payload={"verb": "change", "model": w.model},
        )
