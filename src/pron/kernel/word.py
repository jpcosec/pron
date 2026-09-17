"""One word of the lexicon (spec 05): its form, what it names as a form (pron.sexpr.refs,
spec 13), why it exists and where it came from. Nothing in it is written in code except
pron's function words; a word of a world comes from a model, a field, an enum value, a
relation type, or an alias.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

SLOT_RE = re.compile(r"\b(N|X|Z|DAY|TIME)\b")


@dataclass
class Word:
    form: str
    kind: str  # model | field | value | relation | action | alias
    ref: str  # what the word names, as a form (pron.sexpr.refs, spec 13): (model M), (relation R), …
    motive: str
    source: str  # where it comes from, for the trace
    model: str | None = None
    field_name: str | None = None
    relation: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)

    @property
    def slots(self) -> list[str]:
        return SLOT_RE.findall(self.form)

    def describe(self) -> str:
        return f"{self.form!r} → {self.ref} · {self.motive}"
