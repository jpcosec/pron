"""A complement read through a relation (spec 02, 03): "the reservations of Luis" are the
heads related to what "of Luis" names. For each relation type between the head's family and
another class, the complement is resolved in that class and the edges are read from sldb's
typed edge index; the first relation and class that take the complement answer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Iterator

from pron.kernel.ids import address_of
from pron.kernel.parts.noun_phrase import NounPhrase
from pron.sexpr.resolving.resolution import Resolution
from pron.sexpr.resolving.verbs import Verbs

if TYPE_CHECKING:
    from pron.world.lexicon import Lexicon

Resolve = Callable[[NounPhrase, "Lexicon"], Resolution]


class ComplementLinks:
    """The heads a complement is related to, and what resolving it read on the way."""

    def __init__(
        self, lex: Lexicon, resolve: Resolve, queries: list[str], also_read: list[str]
    ):
        self.lex, self.resolve = lex, resolve
        self.queries, self.also_read = queries, also_read
        self.verbs = Verbs(lex)

    def __call__(self, np: NounPhrase, comp: Any) -> list[str] | None:
        """None when no relation and class take the complement."""
        assert np.model is not None
        family = set(self.lex.world.family_of(np.model))
        for rel, direction, other in self._sides(family):
            heads = self._through(comp, rel, direction, other)
            if heads is not None:
                return heads
        return None

    def _sides(self, family: set[str]) -> Iterator[tuple[str, str, str]]:
        """(relation, direction, other class) for every relation type the head's family is in:
        "to" when the head is the source, "from" when it is the target."""
        for rel, rt in self.lex.relation_types.items():
            sides = []
            if family & set(rt.get("source_types") or []):
                sides.append(("to", rt.get("target_types") or []))
            if family & set(rt.get("target_types") or []):
                sides.append(("from", rt.get("source_types") or []))
            yield from (
                (rel, direction, other)
                for direction, others in sides
                for other in others
            )

    def _through(
        self, comp: Any, rel: str, direction: str, other: str
    ) -> list[str] | None:
        inner = self._inner(comp, other)
        if inner is None:
            return None
        self.queries.extend("  " + q for q in inner.queries)
        if inner.outcome != "unico" or not inner.addresses:
            return None
        self.also_read.extend(inner.addresses + inner.also_read)
        heads: list[str] = []
        for eid in inner.export_ids():
            heads += self._heads(eid, rel, direction)
        return sorted({address_of(h) for h in heads})

    def _inner(self, comp: Any, other: str) -> Resolution | None:
        """The complement resolved in the other class; None when it is a phrase of another."""
        if not isinstance(comp, NounPhrase):
            return self.resolve(
                NounPhrase(other, "all", "plural", proper=list(comp)), self.lex
            )
        if comp.model is None or other not in self.lex.world.family_of(comp.model):
            return None
        return self.resolve(comp, self.lex)

    def _heads(self, eid: str, rel: str, direction: str) -> list[str]:
        to = direction == "to"
        read = self.verbs.edges_to(eid, rel) if to else self.verbs.edges_from(eid, rel)
        self.queries.extend(read.queries)
        return [e["source"] if to else e["target"] for e in read.edges]
