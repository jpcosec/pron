"""Reading edges (spec 03): from sldb's typed edge index, the one door — it already includes
the authored edges (RelationDocs, `origin: relation_doc`) and federates the stores of the
projection itself. Edges have one shape — source, target, relation, metadata — and the read
says the exact queries it took. pron never assembles edges.

`sldb()` is a second, narrower door kept on purpose: reading the RelationDocs straight,
without the index, for pre-validation of an edge that may not be written yet (state
machine guards, cardinality and uniqueness checks before `assert_edge` creates one).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.ids import is_local, qualify, relativize, scope as _scope
from pron.sexpr.resolving.edge_read import EdgeRead
from pron.world.doc_id import DocId
from pron.world.graph import doc_id

if TYPE_CHECKING:
    from pron.world.lexicon import Lexicon

# the RelationDoc field a read is keyed on
SIDES = {"from": "source_id", "to": "target_id"}


class EdgeReader:
    """The edges from and to a document, through sldb's edge index."""

    def __init__(self, lex: Lexicon, stores: list[str]):
        self.lex, self.world, self.store = lex, lex.world, lex.world.store
        self.stores = stores

    def edges_from(self, export_id: str, relation: str | None = None) -> EdgeRead:
        return self._read("from", export_id, relation)

    def edges_to(self, export_id: str, relation: str | None = None) -> EdgeRead:
        return self._read("to", export_id, relation)

    def _read(self, direction: str, export_id: str, relation: str | None) -> EdgeRead:
        read = getattr(self.world.graph, f"edges_{direction}")
        edges = read(doc_id(export_id), relation)
        query = f"sldb edges_{direction}({export_id}, {relation or '*'}) → {len(edges)}"
        return EdgeRead([_strip(e) for e in edges], [query])

    def sldb(self, side: str, export_id: str, relation: str | None) -> EdgeRead:
        """The authored edges as documents, in every store of the projection, read straight
        from their RelationDocs rather than the index (see module docstring)."""
        queries: list[str] = []
        found: list[str] = []
        for s in self.stores:
            found += self._in_store(s, side, export_id, relation, queries)
        edges = [e for e in (self._edge(a) for a in found) if e is not None]
        return EdgeRead(edges, queries)

    def _in_store(
        self,
        s: str,
        side: str,
        export_id: str,
        relation: str | None,
        queries: list[str],
    ) -> list[str]:
        sc = _scope(s, "RelationDoc", family=False)
        # a store's documents name their own documents without prefix
        local_id = relativize(export_id, None if is_local(s) else s)
        hits = self.store.find(sc, f'{side} = "{local_id}"')
        queries.append(
            f"find '{sc}' --where '{side} = \"{local_id}\"' → {len(hits)} (graph not fresh)"
        )
        if relation:
            by_rel = set(self.store.find(sc, f'relation_type = "{relation}"'))
            queries.append(
                f"find '{sc}' --where 'relation_type = \"{relation}\"' → {len(by_rel)}"
            )
            hits = [a for a in hits if a in by_rel]
        return hits

    def _edge(self, address: str) -> dict[str, Any] | None:
        name = address.split("}.", 1)[1]
        store = address.split(":", 1)[0] if ":st.{" in address else "local"
        d = self.store.doc(DocId.of("RelationDoc", name, store))
        if d is None:
            return None
        p = d.payload
        rt = self.lex.relation_types.get(p["relation_type"], {})
        here = None if d.store_name == "local" else d.store_name
        return {
            "source": qualify(p["source_id"], here),
            "target": qualify(p["target_id"], here),
            "relation": p["relation_type"],
            "metadata": {
                "origin": "relation_doc",
                "relation_doc": name,
                "relation_store": d.store_name,
                "condition": p.get("condition") or rt.get("condition", ""),
                "axis": rt.get("axis", ""),
            },
        }


def _strip(e: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": e["source"].replace("sldb://document/", ""),
        "target": e["target"].replace("sldb://document/", ""),
        "relation": e["relation"],
        "metadata": e.get("metadata", {}),
    }
