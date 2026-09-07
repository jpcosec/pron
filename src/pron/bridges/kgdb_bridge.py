"""Single door to kgdb. Implements atom-bridges-are-the-only-doors-to-sldb-and-kgdb.

Loads the persisted networkx graph produced by `sldb semantic-export` +
`kgdb ingest-sldb`, and warns on staleness instead of serving old truth
(atom-graph-freshness-is-the-producers-responsibility).
"""

from __future__ import annotations

import json
from pathlib import Path

GRAPH_RELPATH = ".sldb/runtime/knowledge.nx.json"


class KgdbBridge:
    """Traversal access to the materialized knowledge graph."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self.graph_path = self.root / GRAPH_RELPATH
        self._graph: dict | None = None

    def available(self) -> bool:
        """Whether a materialized graph exists."""
        return self.graph_path.exists()

    def _load(self) -> dict:
        if self._graph is None:
            self._graph = json.loads(self.graph_path.read_text())
        return self._graph

    def snapshot_store_hash(self) -> str:
        """hash_a recorded at export time, for freshness comparison."""
        for node in self._load().get("nodes", []):
            source = (node.get("schema") or {}).get("source") or {}
            store = source.get("store") or {}
            if store.get("hash_a"):
                return store["hash_a"]
        return ""

    def is_stale(self, live_store_hash: str) -> bool:
        """True when the snapshot was built from a different store state."""
        recorded = self.snapshot_store_hash()
        return bool(recorded) and recorded != live_store_hash

    def node(self, node_id: str) -> dict | None:
        """One node's schema payload by id."""
        for node in self._load().get("nodes", []):
            if node.get("id") == node_id:
                return node.get("schema") or {}
        return None

    def edges_from(self, node_id: str, relation: str | None = None) -> list[dict]:
        """Outgoing edges of a node, optionally filtered by relation_type."""
        schema = self.node(node_id) or {}
        edges = schema.get("edges", [])
        if relation:
            edges = [e for e in edges if e.get("relation_type") == relation]
        return edges

    def edges_to(self, node_id: str, relation: str | None = None) -> list[str]:
        """Ids of nodes with an edge pointing at node_id (incoming)."""
        sources = []
        for node in self._load().get("nodes", []):
            for edge in (node.get("schema") or {}).get("edges", []):
                if edge.get("target_id") != node_id:
                    continue
                if relation and edge.get("relation_type") != relation:
                    continue
                sources.append(node["id"])
        return sources

    def document_node_id(self, model: str, name: str) -> str:
        """Canonical sldb:// id for a tracked document."""
        return f"sldb://document/{model}:{name}"
