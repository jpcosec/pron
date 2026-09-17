"""What a sentence turned out to be (spec 06): its items, its parts, the words it used that
the lexicon does not have, and the notes the interpretation left for the trace and the
MoveDoc record.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pron.kernel.parts.item import Item
from pron.kernel.parts.part import Part


@dataclass
class Interpretation:
    sentence: str
    items: list[Item]
    parts: list[Part]
    unknown: list[Item] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def forma(self) -> str:
        return "+".join(p.kind for p in self.parts) if self.parts else "none"

    def to_record(self) -> dict[str, Any]:
        return {
            "forma": self.forma,
            "items": [repr(i) for i in self.items],
            "parts": [p.describe() for p in self.parts],
            "unknown": [i.text for i in self.unknown],
            "notes": self.notes,
        }
