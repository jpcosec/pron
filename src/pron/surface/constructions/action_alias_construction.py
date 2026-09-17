"""`action_alias` (spec 05, 11 §7): an action alias ("confirm it") whose verb, field and value
come from the alias, and whose subject is the first noun phrase.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.item import Item
from pron.kernel.parts.part import Part
from pron.surface.interpret import _first
from pron.surface.nouns import find_noun_phrases

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class ActionAliasConstruction:
    name = "action_alias"

    def __call__(self, items: list[Item], lex: "Lexicon") -> Part | None:
        w = _first(items, "alias-action")
        if w is None:
            return None
        nps = find_noun_phrases(items, lex)
        subject = nps[0] if nps else None
        return Part(
            "action",
            subject=subject,
            verb=w,
            field_name=w.field_name,
            value=w.payload.get("value"),
            payload={"verb": w.payload.get("verb"), "alias": True},
        )
