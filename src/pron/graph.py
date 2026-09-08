"""The only door to kgdb: read edges of the typed graph the projector built.

pron never writes to kgdb. The graph lives at <world>/.pron/graph.nx.json, built by
`kgdb ingest --store` through its library (see pron.world.World.refresh). It is fresh
when the model hashes it was built from are the store's current ones (the ledger's
model excluded); otherwise every read says so and callers fall back to sldb.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import networkx as nx

from kgdb.graph.utils import load_graph

GRAPH_RELPATH = Path(".pron") / "graph.nx.json"
LEDGER_MODEL = "MoveDoc"


def doc_id(export_id: str) -> str:
    return f"sldb://document/{export_id}"


def model_id(name: str) -> str:
    return f"sldb://model/{name}"


def relation_type_id(name: str) -> str:
    return f"sldb://relation_type/{name}"


def field_id(model: str, field: str) -> str:
    return f"sldb://field/{model}.{field}"


class Graph:
    def __init__(self, root: str | Path) -> None:
        self.path = Path(root).resolve() / GRAPH_RELPATH
        self._g: nx.MultiDiGraph | None = None

    def available(self) -> bool:
        return self.path.exists()

    def load(self) -> nx.MultiDiGraph:
        if self._g is None:
            self._g = load_graph(self.path)
        return self._g

    def reload(self) -> None:
        self._g = None

    def metadata(self) -> dict[str, Any]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return data.get("graph", {}) or {}

    def built_from(self) -> dict[str, str]:
        """Model name -> hash_b the snapshot was built from (ledger excluded)."""
        models = self.metadata().get("models", {}) or {}
        return {k: v for k, v in models.items() if k != LEDGER_MODEL}

    def is_fresh(self, current_models: dict[str, str]) -> bool:
        if not self.available():
            return False
        current = {k: v for k, v in current_models.items() if k != LEDGER_MODEL}
        return self.built_from() == current

    def has_node(self, node_id: str) -> bool:
        return node_id in self.load()

    def node(self, node_id: str) -> dict[str, Any]:
        g = self.load()
        return g.nodes[node_id].get("schema", {}) if node_id in g else {}

    def edges_from(self, node_id: str, relation: str | None = None) -> list[dict[str, Any]]:
        """Outgoing edges: [{target, relation, metadata}]."""
        g = self.load()
        if node_id not in g:
            return []
        out = []
        for _, tgt, data in g.out_edges(node_id, data=True):
            if relation is None or data.get("relation") == relation:
                out.append({"source": node_id, "target": tgt, "relation": data.get("relation"), "metadata": data.get("metadata", {})})
        return out

    def edges_to(self, node_id: str, relation: str | None = None) -> list[dict[str, Any]]:
        g = self.load()
        if node_id not in g:
            return []
        out = []
        for src, _, data in g.in_edges(node_id, data=True):
            if relation is None or data.get("relation") == relation:
                out.append({"source": src, "target": node_id, "relation": data.get("relation"), "metadata": data.get("metadata", {})})
        return out

    def exists(self, source: str, target: str, relation: str) -> dict[str, Any] | None:
        for e in self.edges_from(source, relation):
            if e["target"] == target:
                return e
        return None
