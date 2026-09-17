"""`forget` (spec 11 §7): the kernel verb with the phrase naming what to untrack."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.item import Item
from pron.kernel.parts.part import Part
from pron.surface.interpret import _kernel
from pron.surface.nouns import find_noun_phrases

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class ForgetConstruction:
    name = "forget"

    def __call__(self, items: list[Item], lex: "Lexicon") -> Part | None:
        w = _kernel(items, "forget")
        if w is None:
            return None
        nps = find_noun_phrases(items, lex)
        return Part(
            "action",
            subject=nps[0] if nps else None,
            verb=w,
            payload={"verb": "forget"},
        )
