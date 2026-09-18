"""`kb_neighbors` (spec 14 §3, spec 10 §2.4): the edges of one document in sldb's edge index,
out, in or both, optionally of one relation, each with its origin and its condition, and the
literal address of the other end when it is a document.
"""

from __future__ import annotations

from typing import Any

from pron.mcp.doc_entries import DocEntries
from pron.mcp.mount import Mount
from pron.world.doc_id import DocId
from pron.world.graph import bare, doc_id as node_of, kind

DIRECTIONS = ("out", "in", "both")


class Neighbors:
    """The edges around one document."""

    def __init__(self, mount: Mount) -> None:
        self.mount = mount
        self.entries = DocEntries(mount)

    def __call__(self, id: str, relation: str | None, direction: str) -> dict[str, Any]:
        if direction not in DIRECTIONS:
            raise ValueError(f"direction is one of {', '.join(DIRECTIONS)}")
        self.mount.world.store.begin_operation()
        doc_id = self.mount.require(DocId.parse(id))
        node, graph = node_of(str(doc_id)), self.mount.world.graph
        edges = []
        if direction != "in":
            edges += [
                self._row(e, "out", e["target"])
                for e in graph.edges_from(node, relation)
            ]
        if direction != "out":
            edges += [
                self._row(e, "in", e["source"]) for e in graph.edges_to(node, relation)
            ]
        return {**self.entries.entry(doc_id), "edges": edges}

    def _row(self, edge: dict[str, Any], direction: str, other: str) -> dict[str, Any]:
        meta = edge.get("metadata") or {}
        return {
            "relation": edge["relation"],
            "direction": direction,
            "source": edge["source"],
            "target": edge["target"],
            "other": self._end(other),
            "origin": meta.get("origin", ""),
            "condition": meta.get("condition", ""),
        }

    def _end(self, node: str) -> dict[str, Any]:
        """The other end: a document row with its address, or the bare node id."""
        if kind(node) != "document":
            return {"node": node}
        doc_id = DocId.parse(bare(node))
        if not self.mount.admits(doc_id):
            return {"node": node, "id": str(doc_id)}
        return self.entries.entry(doc_id)
