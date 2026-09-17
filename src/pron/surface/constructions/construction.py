"""What a construction is (spec 06, 11 §1): one fixed shape of sentence, listed by name in
patterns.yaml, that recognises a Part in a chunk of classified items or says it does not.
A world never adds one; it adds words.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from pron.kernel.parts.item import Item
from pron.kernel.parts.part import Part

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class Construction(Protocol):
    name: str

    def __call__(self, items: list[Item], lex: "Lexicon") -> Part | None:
        """The part these items make under this construction, or None."""
        ...
