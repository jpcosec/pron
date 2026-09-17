"""One segment of a classified sentence (spec 06 steps 1–2): a `det`, `referent`, `wh`,
`conj`, `punct`, `number`, `literal`, `word` (one or more lexicon words sharing the matched
form, ambiguity kept), or `unknown`, with whatever slots the matched form captured.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pron.kernel.parts.word import Word


@dataclass
class Item:
    kind: str  # det | referent | wh | conj | punct | number | literal | word | unknown
    text: str  # surface text as written
    words: list[Word] = field(default_factory=list)  # candidates when kind == word
    slots: dict[str, Any] = field(
        default_factory=dict
    )  # captured N / X / Z / DAY / TIME
    number: str | None = None  # singular | plural for det/referent/word
    meta: dict[str, Any] = field(default_factory=dict)

    def refs(self) -> set[str]:
        return {w.ref for w in self.words}

    def __repr__(self) -> str:
        return f"{self.kind}({self.text!r}{'→' + ','.join(sorted(self.refs())) if self.words else ''}{' ' + str(self.slots) if self.slots else ''})"
