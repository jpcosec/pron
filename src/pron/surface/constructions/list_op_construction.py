"""`list_op` (spec 11 §7): `add`, `remove` or `clean` on a list field — "add the tag
system:pron to them" — with the value the first item outside every noun phrase.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.item import Item
from pron.kernel.parts.part import Part
from pron.kernel.parts.word import Word
from pron.surface.interpret import _field_word, _implicit_it, _in_np, _kernel
from pron.surface.nouns import find_noun_phrases

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon

LIST_VERBS = ("add", "remove", "clean")


class ListOpConstruction:
    name = "list_op"

    def __call__(self, items: list[Item], lex: "Lexicon") -> Part | None:
        """The first list verb said decides; without a field word there is no part."""
        for verb in LIST_VERBS:
            w = _kernel(items, verb)
            if w is not None:
                return self._part(items, lex, verb, w)
        return None

    @staticmethod
    def _part(items: list[Item], lex: "Lexicon", verb: str, w: Word) -> Part | None:
        nps = find_noun_phrases(items, lex)
        subject = next((n for n in nps if n.referent is not None), None) or (
            nps[-1] if nps else None
        )
        found = _field_word(items)
        value_item = next(
            (
                i
                for i in items
                if i.kind in ("unknown", "literal", "number") and not _in_np(i, nps)
            ),
            None,
        )
        if found is None:
            return None
        fw = found[1]
        return Part(
            "action",
            subject=subject or _implicit_it(),
            verb=w,
            field_name=fw.field_name,
            value=value_item.meta.get("value", value_item.text) if value_item else None,
            payload={"verb": verb, "model": fw.model},
        )
