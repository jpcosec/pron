"""The only door to kgdb: read edges of the typed graph the projector built (spec 03, 10).

pron never writes to kgdb. The graph lives at <world>/.pron/graph.nx.json, built by
`kgdb ingest --store` through its library (see pron.world.world.World.refresh). It is fresh
when the model hashes it was built from are the store's current ones (the ledger's
model excluded); otherwise every read says so and callers fall back to sldb.
"""

from __future__ import annotations

from pron.world.graph_file import GraphFile


def doc_id(export_id: str) -> str:
    return f"sldb://document/{export_id}"


def model_id(name: str) -> str:
    return f"sldb://model/{name}"


def relation_type_id(name: str) -> str:
    return f"sldb://relation_type/{name}"


def field_id(model: str, field: str) -> str:
    return f"sldb://field/{model}.{field}"


def tag_id(tag: str) -> str:
    return f"sldb://semantic_tag/{tag}"


def kind(node_id: str) -> str | None:
    """The `<kind>` of an `sldb://<kind>/...` id (document, model, semantic_tag, section, field, ...)."""
    if node_id.startswith("sldb://"):
        rest = node_id[len("sldb://") :]
        return rest.split("/", 1)[0] if "/" in rest else None
    return None


def bare(node_id: str) -> str:
    """The id without its `sldb://<kind>/` prefix; an id without one passes through."""
    if node_id.startswith("sldb://"):
        rest = node_id[len("sldb://") :]
        return rest.split("/", 1)[1] if "/" in rest else rest
    return node_id


class Graph(GraphFile):
    """The typed graph of a world: the file kgdb saved (`GraphFile`) and the walks over it,
    each one parametrized by a relation name."""

    # -- navigation (spec 10 §2): every walk is parametrized by a relation name -------------
    # Nothing here knows which relations a world declares; kgdb's structural ones
    # (semantic_parent, tagged_as, has_document, ...) are just the usual arguments.

    def node_type(self, node_id: str) -> str | None:
        identity = self.node(node_id).get("identity", {}) or {}
        return identity.get("node_type")

    def nodes_of_type(self, node_type: str) -> list[str]:
        """Ids of the nodes whose identity.node_type is `node_type`; a document's type is its
        model name."""
        return sorted(n for n in self.load() if self.node_type(n) == node_type)

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
