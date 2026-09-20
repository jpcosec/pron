"""The typed graph of a world (spec 03, 10): sldb's own edge index, the one door to edges.

pron no longer implements any walk here. The relation-parametrized traversals live in
sldb's graph layer (`sldb.api.graph`); this class holds the store path and the tags to
exclude, composes the index for each read, and delegates every walk. Reading never
rebuilds, and is memoized by the shards' own signature, not by anything this class
remembers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sldb.api import load_edge_index
from sldb.api.graph import (
    children,
    descendants,
    exists,
    neighbors_via,
    parent,
    roots,
    sources,
    targets,
)
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
        self.sp = sp
        self.exclude_tags = (
            tags_outside_graph() if exclude_tags is None else exclude_tags
        )

    def reload(self) -> None:
        """Kept for callers; the index invalidates itself by the shards' own signature."""

    def _idx(self) -> EdgeIndex:
        return load_edge_index(
            self.sp, include_linked=True, exclude_tags=self.exclude_tags
        )

    @property
    def stale(self) -> list[str]:
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
        return exists(self.sp, source, target, relation, self.exclude_tags)

    # -- navigation (spec 10 §2): every walk delegates to sldb's graph layer ---------------

    def targets(self, node_id: str, relation: str) -> list[str]:
        return targets(self.sp, node_id, relation, self.exclude_tags)

    def sources(self, node_id: str, relation: str) -> list[str]:
        return sources(self.sp, node_id, relation, self.exclude_tags)

    def roots(self, node_type: str, relation: str) -> list[str]:
        return roots(self.sp, node_type, relation, self.exclude_tags)

    def children(self, node_id: str, relation: str = "semantic_parent") -> list[str]:
        return children(self.sp, node_id, relation, self.exclude_tags)

    def parent(self, node_id: str, relation: str = "semantic_parent") -> str | None:
        return parent(self.sp, node_id, relation, self.exclude_tags)

    def descendants(
        self, node_id: str, relation: str = "semantic_parent", depth: int | None = None
    ) -> list[str]:
        return descendants(self.sp, node_id, relation, depth, self.exclude_tags)

    def neighbors_via(
        self,
        node_id: str,
        out_relation: str,
        in_relation: str | None = None,
        exclude_prefixes: tuple[str, ...] = (),
        same_kind: bool = True,
    ) -> list[str]:
        return neighbors_via(
            self.sp,
            node_id,
            out_relation,
            in_relation,
            exclude_prefixes,
            same_kind,
            self.exclude_tags,
        )
