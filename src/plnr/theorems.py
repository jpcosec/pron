"""Theorems as data: how to prove a goal, and what to do when something is asserted.

Two kinds, the two of MicroPlanner:

    (theorem NAME consequent PATTERN BODY ...)   how to prove a goal that matches PATTERN
    (theorem NAME antecedent PATTERN BODY ...)   what follows once PATTERN is asserted

A theorem is a document of the world, not a function of this package: the engine never
holds a rule of its own, and a world that declares no theorems can still be searched with
primitive goals alone. Which theorems a goal may use is the caller's or the goal's
decision (`use`), the way THUSE is explicit in MicroPlanner.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from typing import Any

from plnr.sexp import Sym, read_all, write

CONSEQUENT = "consequent"
ANTECEDENT = "antecedent"


class TheoremError(ValueError):
    """A theorem that is not well formed."""


@dataclass(frozen=True)
class Theorem:
    """One rule: its name, its kind, the pattern it is about, and its body."""

    name: str
    kind: str
    pattern: Any
    body: tuple[Any, ...]
    source: str = ""

    def __post_init__(self) -> None:
        if self.kind not in (CONSEQUENT, ANTECEDENT):
            raise TheoremError(f"{self.name}: unknown kind {self.kind!r}")
        if not isinstance(self.pattern, list) or not self.pattern:
            raise TheoremError(f"{self.name}: pattern must be a non-empty form")

    @property
    def head(self) -> str:
        """The first symbol of the pattern: what the rule is about."""
        return str(self.pattern[0])

    def as_form(self) -> list[Any]:
        return [
            Sym("theorem"),
            Sym(self.name),
            Sym(self.kind),
            self.pattern,
            *self.body,
        ]

    def __repr__(self) -> str:
        return f"Theorem({self.name} {self.kind} {write(self.pattern)})"


def read_theorem(form: Any, source: str = "") -> Theorem:
    """One `(theorem NAME kind PATTERN BODY …)` form as a Theorem."""
    if not isinstance(form, list) or len(form) < 4 or str(form[0]) != "theorem":
        raise TheoremError(f"not a theorem: {write(form)}")
    _, name, kind, pattern, *body = form
    return Theorem(str(name), str(kind), pattern, tuple(body), source)


@dataclass
class Theorems:
    """The theorems of a world, indexed by the head of their pattern."""

    items: list[Theorem] = field(default_factory=list)

    def add(self, theorem: Theorem) -> None:
        if any(t.name == theorem.name for t in self.items):
            raise TheoremError(f"duplicate theorem name: {theorem.name}")
        self.items.append(theorem)

    def load(self, text: str, source: str = "") -> Theorems:
        """Every theorem in a text, in order; anything else in it is an error."""
        for form in read_all(text):
            self.add(read_theorem(form, source))
        return self

    def by_name(self, name: str) -> Theorem:
        for t in self.items:
            if t.name == name:
                return t
        raise TheoremError(f"no theorem named {name!r}")

    def consequents(self, head: str, use: Iterable[str] | None = None) -> Iterator[Theorem]:
        """The consequent theorems that could prove a goal with this head.

        `use` is THUSE: when given, only those names are tried, in the order given, so a
        goal can say exactly how it wants to be proved.
        """
        if use is not None:
            for name in use:
                t = self.by_name(name)
                if t.kind == CONSEQUENT:
                    yield t
            return
        for t in self.items:
            if t.kind == CONSEQUENT and t.head == head:
                yield t

    def antecedents(self, head: str) -> Iterator[Theorem]:
        for t in self.items:
            if t.kind == ANTECEDENT and t.head == head:
                yield t

    def names(self) -> list[str]:
        return [t.name for t in self.items]

    def __len__(self) -> int:
        return len(self.items)
