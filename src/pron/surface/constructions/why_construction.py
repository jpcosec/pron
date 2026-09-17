"""`why` (spec 11 §7): a sentence that starts by asking why; what follows it is kept as
leftovers for the explanation to read.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.item import Item
from pron.kernel.parts.part import Part

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.lexicon import Lexicon


class WhyConstruction:
    name = "why"

    def __call__(self, items: list[Item], lex: "Lexicon") -> Part | None:
        if items and items[0].kind == "wh" and items[0].meta.get("question") == "why":
            return Part(
                "why",
                leftovers=[
                    i for i in items[1:] if i.kind not in ("punct", "wh", "referent")
                ],
            )
        return None
