"""The world of pron seen by the goal engine (plnr.World, spec 02, 03).

Five questions, and every one of them goes to sldb or to kgdb — never to Python over the
documents. `matches` is sldb's own `--where`; `edges` is pron's EdgeReader, which decides
between the typed graph and the RelationDocs in sldb and says which door answered.

Documents are named by export id (`Model:name`, `A:Model:name`), the same as everywhere else
in pron, so a goal and a form name the same thing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator

from pron.kernel.ids import is_local, join_id
from pron.world.doc_id import DocId

if TYPE_CHECKING:
    from pron.sexpr.resolving.verbs import Verbs
    from pron.world.lexicon import Lexicon

Edge = tuple[str, str, str]


class PronWorld:
    """plnr's four reads over one pron world, in the stores of one projection."""

    def __init__(self, lex: Lexicon, verbs: Verbs):
        self.lex, self.verbs = lex, verbs
        self.store, self.stores = lex.world.store, list(lex.stores)
        self.queries: list[str] = []  # what the reads asked, for record["queries"]

    def docs(self, model: str | None = None) -> Iterator[str]:
        for s in self.stores:
            for m in [model] if model else self.lex.world.model_names(s):
                self.asked(f"docs {m} in {s}")
                for d in self.store.docs_of(m, s):
                    yield join_id(None if is_local(s) else s, m, d.name)

    def model_of(self, doc: str) -> str | None:
        return DocId.parse(doc).model

    def payload(self, doc: str) -> dict[str, Any]:
        self.asked(f"get {doc}")
        return dict(self.store.payload(DocId.parse(doc)))

    def matches(self, doc: str, predicate: str) -> bool:
        """sldb's evaluator, never a Python one: the grammar of a predicate is sldb's."""
        self.asked(f"where {doc} --where '{predicate}'")
        return self.store.matches(DocId.parse(doc), predicate)

    def asked(self, query: str) -> None:
        """Every read of the search, in order: what a MoveDoc keeps as its queries (spec 02)."""
        self.queries.append(query)

    def edges(
        self,
        relation: str | None = None,
        source: str | None = None,
        target: str | None = None,
    ) -> Iterator[Edge]:
        """The edges around one end. kgdb answers when it is fresh and holds the document;
        else the RelationDocs do, and the trace keeps the query either way."""
        if source is not None:
            return self._edges("edges_from", source, relation)
        if target is not None:
            return self._edges("edges_to", target, relation)
        return self._all(relation)

    def _edges(self, side: str, end: str, relation: str | None) -> Iterator[Edge]:
        """The edges around one end, always written source → target, whichever end was given:
        a goal that binds the far end must find it in the place the pattern has it."""
        read = getattr(self.verbs, side)(end, relation)
        self.queries.extend(read.queries)
        if not read.queries:
            self.asked(f"edges {side}({end}, {relation or '*'}) → {len(read.edges)}")
        for e in read.edges:
            source, target = str(e["source"]), str(e["target"])
            yield (str(e["relation"]), source, target)

    def _all(self, relation: str | None) -> Iterator[Edge]:
        """An edge with neither end given: read from the RelationDocs, the only place where
        an edge exists on its own."""
        for s in self.stores:
            for d in self.store.docs_of("RelationDoc", s):
                payload = d.payload
                if relation is not None and payload.get("relation_type") != relation:
                    continue
                self.queries.append(f"docs_of RelationDoc {s} → {d.name}")
                yield (
                    str(payload.get("relation_type")),
                    str(payload.get("source_id")),
                    str(payload.get("target_id")),
                )
