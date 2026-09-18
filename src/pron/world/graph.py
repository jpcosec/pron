"""The typed graph of a world (spec 03, 10): sldb's own edge index, the one door to edges.

pron never writes to it and never assembles it: `sldb.api.load_edge_index` composes it from
per-document shards that every sldb write already keeps current (spec 11 §5). Reading never
rebuilds, and is memoized by the shards' own signature, not by anything this class remembers
— so every method here composes fresh and is still cheap on a warm store.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sldb.api import load_edge_index
from sldb.store.edge_index.edge_index import EdgeIndex

from pron.world.doc_kind import tags_outside_graph
from pron.world.graph_ids import (  # noqa: F401 - re-exported: callers import ids from here
    bare,
    doc_id,
    field_id,
    kind,
    model_id,
    relation_type_id,
    tag_id,
)


class Graph:
    """The typed graph of one store (and the stores it links): sldb's edge index, and the
    walks over it, each one parametrized by a relation name.

    Nothing here knows which relations a world declares; sldb's structural ones
    (semantic_parent, tagged_as, has_document, ...) are just the usual arguments.
    """

    def __init__(
        self, sp: str | Path, exclude_tags: tuple[str, ...] | None = None
    ) -> None:
        """`exclude_tags` defaults to `doc_kind.tags_outside_graph()`, resolved here rather
        than baked into the signature: a tuple built once at import time would not be a
        constant callers could reasonably override, and the registry it reads (spec 05, 07)
        is pron's own, not sldb's."""
        self.sp = sp
        self.exclude_tags = tags_outside_graph() if exclude_tags is None else exclude_tags

    def reload(self) -> None:
        """Kept for callers; the index invalidates itself by the shards' own signature, not
        by anything cached here."""

    def _idx(self) -> EdgeIndex:
        return load_edge_index(
            self.sp, include_linked=True, exclude_tags=self.exclude_tags
        )

    @property
    def stale(self) -> list[str]:
        """Export ids of tracked documents whose shard is missing or built from another
        hash_c: a write made outside sldb. Empty on a world where every write went through
        pron's own Store."""
        return self._idx().stale

    def available(self) -> bool:
        return True

    # -- the four primitives everything else below is written on --------------------------

    def has_node(self, node_id: str) -> bool:
        return self._idx().node(node_id) is not None

    def node(self, node_id: str) -> dict[str, Any]:
        found = self._idx().node(node_id)
        return found.model_dump() if found is not None else {}

    def node_type(self, node_id: str) -> str | None:
        found = self._idx().node(node_id)
        return found.node_type if found is not None else None

    def nodes_of_type(self, node_type: str) -> list[str]:
        """Ids of the nodes whose class is `node_type`; a document's type is its model name."""
        return [n.id for n in self._idx().nodes_of_type(node_type)]

    def edges_from(
        self, node_id: str, relation: str | None = None
    ) -> list[dict[str, Any]]:
        return [e.model_dump() for e in self._idx().edges_from(node_id, relation)]

    def edges_to(
        self, node_id: str, relation: str | None = None
    ) -> list[dict[str, Any]]:
        return [e.model_dump() for e in self._idx().edges_to(node_id, relation)]

    def exists(self, source: str, target: str, relation: str) -> dict[str, Any] | None:
        for e in self.edges_from(source, relation):
            if e["target"] == target:
                return e
        return None

    # -- navigation (spec 10 §2): every walk is parametrized by a relation name -------------

    def targets(self, node_id: str, relation: str) -> list[str]:
        return sorted({e["target"] for e in self.edges_from(node_id, relation)})

    def sources(self, node_id: str, relation: str) -> list[str]:
        return sorted({e["source"] for e in self.edges_to(node_id, relation)})

    def roots(self, node_type: str, relation: str) -> list[str]:
        """Nodes of that type with no outgoing edge of that relation: the tops of a
        `semantic_parent` DAG, the entry states of a `transitions_to` machine."""
        return [
            n for n in self.nodes_of_type(node_type) if not self.edges_from(n, relation)
        ]

    def children(self, node_id: str, relation: str = "semantic_parent") -> list[str]:
        """The nodes pointing at node_id through `relation` (a child tag points at its parent)."""
        return self.sources(node_id, relation)

    def parent(self, node_id: str, relation: str = "semantic_parent") -> str | None:
        found = self.targets(node_id, relation)
        return found[0] if found else None

    def descendants(
        self, node_id: str, relation: str = "semantic_parent", depth: int | None = None
    ) -> list[str]:
        """Everything reachable by following `relation` backwards from node_id, breadth first,
        at most `depth` levels (None: all), without node_id itself."""
        seen: set[str] = set()
        frontier = [node_id]
        level = 0
        while frontier and (depth is None or level < depth):
            frontier = self._next_level(frontier, relation, seen, node_id)
            level += 1
        return sorted(seen)

    def _next_level(
        self, frontier: list[str], relation: str, seen: set[str], origin: str
    ) -> list[str]:
        """The children of a frontier not seen yet (and never the origin), marked seen."""
        nxt: list[str] = []
        for n in frontier:
            for child in self.sources(n, relation):
                if child not in seen and child != origin:
                    seen.add(child)
                    nxt.append(child)
        return nxt

    def neighbors_via(
        self,
        node_id: str,
        out_relation: str,
        in_relation: str | None = None,
        exclude_prefixes: tuple[str, ...] = (),
        same_kind: bool = True,
    ) -> list[str]:
        """The nodes that share at least one `out_relation` target with node_id: documents
        tagged like it, reservations at the same table. `in_relation` (default: the same one)
        is how the shared target is read back; a target whose bare id starts with one of
        `exclude_prefixes` is left out of the comparison, so a caller can skip the axes that
        would make everything a neighbor of everything without pron knowing what they are.
        With `same_kind`, only nodes of node_id's kind (a document's neighbors are documents,
        not the model or the sections that carry the same tag)."""
        back = in_relation or out_relation
        out: set[str] = set()
        for shared in self.targets(node_id, out_relation):
            if any(bare(shared).startswith(p) for p in exclude_prefixes):
                continue
            out.update(self.sources(shared, back))
        out.discard(node_id)
        if same_kind:
            k = kind(node_id)
            out = {n for n in out if kind(n) == k}
        return sorted(out)
