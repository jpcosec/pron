"""`@{doc}/{r1}/~{r2}/…` (spec 14 §2.2): from one document, one hop per relation over sldb's
edge index, `rel` forward (`edges_from`) and `~rel` backwards (`edges_to`). Only relations
the world declares walk; what the last hop reaches counts when it is a document the
projection names.
"""

from __future__ import annotations

from pron.mcp.found import Found
from pron.mcp.mount import Mount
from pron.world.doc_id import DocId
from pron.world.graph import bare, doc_id as node_of, kind


class Walk:
    """A chain of relations from a starting document."""

    def __init__(self, mount: Mount) -> None:
        self.mount = mount
        self.graph = mount.world.graph

    def __call__(self, start: str, relations: list[str]) -> Found:
        found = Found()
        undeclared = self.undeclared(relations)
        if undeclared:
            found.notes.append(f"relation {undeclared!r} is not declared in this world")
            return found
        frontier = {node_of(str(self.start(start)))}
        for relation in relations:
            frontier = self.hop(frontier, relation)
        for node in sorted(frontier):
            doc = DocId.parse(bare(node)) if kind(node) == "document" else None
            if doc is not None and self.mount.admits(doc):
                found.add(doc, "walk:" + "/".join(relations))
        return found

    def undeclared(self, relations: list[str]) -> str | None:
        declared = self.mount.world.relation_types()
        return next((r for r in relations if r.lstrip("~") not in declared), None)

    def start(self, ref: str) -> DocId:
        """`Model:doc` (or `A:Model:doc`), or a bare document name the projection holds once."""
        if ":" in ref:
            return self.mount.require(DocId.parse(ref))
        named = [
            DocId.of(r.model_name, r.name, r.store_name)
            for r in self.mount.world.store.docs()
            if r.name == ref
        ]
        named = [d for d in named if self.mount.admits(d)]
        if len(named) != 1:
            raise LookupError(
                f"@{ref}: {len(named)} documents of that name; use Model:doc"
            )
        return named[0]

    def hop(self, frontier: set[str], relation: str) -> set[str]:
        backwards, name = relation.startswith("~"), relation.lstrip("~")
        step = self.graph.sources if backwards else self.graph.targets
        return {n for node in frontier for n in step(node, name)}
