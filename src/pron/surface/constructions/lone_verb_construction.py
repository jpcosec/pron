"""`undo` and `refresh` (spec 11 §1, §7): the kernel verb alone in its sentence, with
nothing but punctuation around it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.item import Item
from pron.kernel.parts.part import Part
from pron.surface.interpret import _kernel

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class LoneVerbConstruction:
    def __init__(self, verb: str) -> None:
        self.name = verb

    def __call__(self, items: list[Item], lex: "Lexicon") -> Part | None:
        w = _kernel(items, self.name)
        return (
            Part(self.name, verb=w)
            if w and len([i for i in items if i.kind != "punct"]) == 1
            else None
        )
