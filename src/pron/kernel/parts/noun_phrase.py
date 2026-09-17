"""A noun phrase (spec 02): a head (a model word, an alias for a model, or a referent) with
a determiner before it and the modifiers after it already turned into sldb predicates, plus
the complements resolution still has to decide.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pron.kernel.parts.item import Item


@dataclass
class NounPhrase:
    model: str | None  # head model; None for a bare referent
    determiner: str | None  # the | a | any | all | none
    number: str  # singular | plural
    predicates: list[str] = field(default_factory=list)
    proper: list[str] = field(
        default_factory=list
    )  # proper names to resolve by key/name/doc
    referent: Item | None = None
    interrogated: bool = False
    items: list[Item] = field(default_factory=list)
    captures: dict[str, Any] = field(
        default_factory=dict
    )  # field literals seen inside the phrase (for compose $literals)
    unknown_values: list[tuple[str, str, str]] = field(
        default_factory=list
    )  # (model, field, text) missing enum values
    complements: list[Any] = field(
        default_factory=list
    )  # after "of" / genitive: a run of proper-name tokens (list[str]) or a nested NounPhrase
    given: list[str] = field(
        default_factory=list
    )  # addresses a form gave directly, (doc "Model:name"): nothing to resolve
    hint: str | None = None  # the class a referent form names, (it "her" Client)
    alternatives: list[str] = field(
        default_factory=list
    )  # the other documents an "any" could have taken, kept so the answer can say so

    @property
    def scope(self) -> str:
        return f"st.{{{self.model}+}}" if self.model else ""

    def describe(self) -> str:
        head = self.model or (self.referent.text if self.referent else "?")
        comps = " ".join(
            "of " + (c.describe() if isinstance(c, NounPhrase) else " ".join(c))
            for c in self.complements
        )
        return f"{self.determiner or ''} {head} [{'; '.join(self.predicates)}]{' ' + ','.join(self.proper) if self.proper else ''}{' ' + comps if comps else ''}".strip()
