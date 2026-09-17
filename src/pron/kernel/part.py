"""One part of a move (spec 06): what a construction recognised in a sentence, or what a
form compiled to — a kind, its subject and object, the verb word, a field and a value.
A sentence coordinated with "and" is one move with several parts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pron.kernel.item import Item
from pron.kernel.noun_phrase import NounPhrase
from pron.kernel.word import Word


@dataclass
class Part:
    kind: str  # nominal | read | assert | action | compose | why | undo | refresh
    subject: NounPhrase | None = None
    object: NounPhrase | None = None
    verb: Word | None = None  # relation word, action word or alias
    field_name: str | None = None
    value: Any = None
    payload: dict[str, Any] = field(
        default_factory=dict
    )  # for create / compose $literals
    items: list[Item] = field(default_factory=list)
    leftovers: list[Item] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def describe(self) -> str:
        bits = [self.kind]
        if self.verb:
            bits.append(self.verb.ref)
        if self.subject:
            bits.append("subject=" + self.subject.describe())
        if self.object:
            bits.append("object=" + self.object.describe())
        if self.field_name:
            bits.append(f"{self.field_name}={self.value!r}")
        if self.payload:
            bits.append(f"payload={self.payload}")
        return " · ".join(bits)
