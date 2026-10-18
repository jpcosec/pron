"""The port to whatever holds the documents, and the overlay the search runs over.

This layer is deliberately thin: four questions (which documents, of what class, what
payload, which edges) plus one predicate test. A real store implements them; MemoryWorld
implements them over dicts so the search can be tested without one.

The overlay is the important half. Search backtracks, and a document store with no
transactions must not be written to while a plan is still being looked for, so every
assertion a plan makes lands in an Overlay: a read sees the pending value, the base world
never moves. Committing is somebody else's job, outside this package.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Mapping
from typing import Any, Protocol, runtime_checkable

from plnr.sexp import Sym

Edge = tuple[str, str, str]  # relation, source, target


@runtime_checkable
class World(Protocol):
    """What the goal engine needs from a store."""

    def docs(self, model: str | None = None) -> Iterable[str]: ...

    def model_of(self, doc: str) -> str | None: ...

    def payload(self, doc: str) -> Mapping[str, Any]: ...

    def edges(
        self,
        relation: str | None = None,
        source: str | None = None,
        target: str | None = None,
    ) -> Iterable[Edge]: ...

    def matches(self, doc: str, predicate: str) -> bool: ...


PRED_RE = re.compile(
    r"""^\s*(?:
        has\(\s*(?P<has>[A-Za-z_]\w*)\s*\)
      | (?P<field>[A-Za-z_]\w*)\s*(?P<op>>=|<=|!=|=|>|<|~)\s*(?P<value>.+?)
    )\s*$""",
    re.X,
)


def _cast(text: str) -> Any:
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    for c in (int, float):
        try:
            return c(text)
        except ValueError:
            pass
    return text


def _compare(op: str, left: Any, right: Any) -> bool:
    if op == "~":
        return str(right).lower() in str(left).lower()
    if op in ("=", "!="):
        same = str(left) == str(right)
        return same if op == "=" else not same
    try:
        lt, rt = float(left), float(right)
    except (TypeError, ValueError):
        return False
    return {">": lt > rt, "<": lt < rt, ">=": lt >= rt, "<=": lt <= rt}[op]


def payload_matches(payload: Mapping[str, Any], predicate: str) -> bool:
    """A stand-in for the store's own `--where`: `field op value` or `has(field)`.

    A real store evaluates its own predicates; this exists so the engine can be exercised
    without one. Keep it dumb on purpose: anything cleverer here would be a second
    dialect of a language that belongs to the store.
    """
    if not predicate.strip():
        return True
    m = PRED_RE.match(predicate)
    if m is None:
        raise ValueError(f"cannot parse predicate: {predicate!r}")
    if m.group("has"):
        v = payload.get(m.group("has"))
        return v is not None and v != [] and v != ""
    field = m.group("field")
    if field not in payload:
        return False
    return _compare(m.group("op"), payload[field], _cast(m.group("value")))


class MemoryWorld:
    """Documents and authored edges in memory."""

    def __init__(
        self,
        documents: Mapping[str, tuple[str, Mapping[str, Any]]] | None = None,
        edges: Iterable[Edge] = (),
    ):
        self._docs: dict[str, tuple[str, dict[str, Any]]] = {
            name: (model, dict(payload)) for name, (model, payload) in (documents or {}).items()
        }
        self._edges: list[Edge] = [tuple(e) for e in edges]  # type: ignore[misc]

    def add(self, doc: str, model: str, payload: Mapping[str, Any]) -> None:
        self._docs[doc] = (model, dict(payload))

    def link(self, relation: str, source: str, target: str) -> None:
        self._edges.append((relation, source, target))

    def docs(self, model: str | None = None) -> Iterator[str]:
        for name, (m, _) in self._docs.items():
            if model is None or m == model:
                yield name

    def model_of(self, doc: str) -> str | None:
        entry = self._docs.get(doc)
        return entry[0] if entry else None

    def payload(self, doc: str) -> Mapping[str, Any]:
        entry = self._docs.get(doc)
        return entry[1] if entry else {}

    def edges(
        self,
        relation: str | None = None,
        source: str | None = None,
        target: str | None = None,
    ) -> Iterator[Edge]:
        for r, s, t in self._edges:
            if relation is not None and r != relation:
                continue
            if source is not None and s != source:
                continue
            if target is not None and t != target:
                continue
            yield (r, s, t)

    def matches(self, doc: str, predicate: str) -> bool:
        return payload_matches(self.payload(doc), predicate)


class Overlay:
    """A world plus what a plan would leave: new documents, changed fields, new edges.

    Reads go through the overlay, so a later goal of the same plan sees what an earlier
    step asserted, and nothing here touches the world underneath.

    An overlay chains to another overlay, not only to a world, and that is what makes
    backtracking correct: a branch that fails is simply an overlay nobody reads again,
    so its pending writes disappear with it. Searching forks one layer per branch instead
    of writing and rewinding, which a store without transactions cannot offer.
    """

    def __init__(self, base: World):
        self.base = base
        self.new_docs: dict[str, str] = {}  # doc -> model
        self.fields: dict[str, dict[str, Any]] = {}  # doc -> field -> value
        self.new_edges: list[Edge] = []
        self.log: list[Any] = []  # this layer's assertions, in order

    # -- reading ---------------------------------------------------------------------

    def docs(self, model: str | None = None) -> Iterator[str]:
        seen: set[str] = set()
        for name in self.base.docs(model):
            seen.add(name)
            yield name
        for name, m in self.new_docs.items():
            if name not in seen and (model is None or m == model):
                yield name

    def model_of(self, doc: str) -> str | None:
        return self.new_docs.get(doc) or self.base.model_of(doc)

    def payload(self, doc: str) -> Mapping[str, Any]:
        out = dict(self.base.payload(doc))
        out.update(self.fields.get(doc, {}))
        return out

    def edges(
        self,
        relation: str | None = None,
        source: str | None = None,
        target: str | None = None,
    ) -> Iterator[Edge]:
        yield from self.base.edges(relation, source, target)
        for r, s, t in self.new_edges:
            if relation is not None and r != relation:
                continue
            if source is not None and s != source:
                continue
            if target is not None and t != target:
                continue
            yield (r, s, t)

    def matches(self, doc: str, predicate: str) -> bool:
        if doc in self.new_docs or doc in self.fields:
            return payload_matches(self.payload(doc), predicate)
        return self.base.matches(doc, predicate)

    # -- writing, pending ------------------------------------------------------------

    # The log is written as forms, so names are symbols and a string value stays a string:
    # whoever commits the plan has to tell a string value from a symbol of the same name.

    def create(self, doc: str, model: str) -> None:
        self.new_docs[doc] = model
        self.log.append([Sym("create"), Sym(model), Sym(doc)])

    def set_field(self, doc: str, field: str, value: Any) -> None:
        self.fields.setdefault(doc, {})[field] = value
        self.log.append([Sym("change"), Sym(doc), Sym(field), value])

    def link(self, relation: str, source: str, target: str) -> None:
        self.new_edges.append((relation, source, target))
        self.log.append([Sym("assert"), Sym(relation), Sym(source), Sym(target)])

    def wrote(self) -> bool:
        return bool(self.all_writes())

    def all_writes(self) -> list[Any]:
        """Every pending write of the chain, outermost first: what a committer replays."""
        parent = self.base.all_writes() if isinstance(self.base, Overlay) else []
        return [*parent, *self.log]
